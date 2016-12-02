from datetime import datetime
from flask import jsonify, request, g
from . import api1_2
from ..api_1_0.base_api import BaseApi, ERR_CODE_EXCEED_ALLOT_NUM_ERROR, ERR_CODE_NO_DEVICE
from ..device.device_api import *
from ..models import AgentRecord2, Apk, datetime_timestamp, User
from ..models import Device
from .. import db
from ..exceptions import ValidationError, MyException
from ..utils import push_message_to_device, filter_upload_url
from ..constant import *


@api1_2.route('/device/allot', methods=['POST'])
def allot_device():
    restore_device_ids = []
    idle_device = None
    user_id = 0
    try:
        user_id = g.current_user.id
        apk_id = request.json.get('apk_id')

        num_left = User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_LIMIT_NAME'], -1)
        if not app.config['DEBUG'] and num_left < 0:
            raise MyException(message='exceed the max allot num error', code=ERR_CODE_EXCEED_ALLOT_NUM_ERROR)

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')

        if apk_id is None or apk_id == '':
            raise ValidationError('does not have a apk id')
        apk = Apk.query.get(apk_id)
        if not apk:
            raise ValidationError('apk does not exists')

        if apk.allow_allot != 1:
            raise ValidationError('apk is Off the shelf')

        idle_device = None
        retry_times = 0
        while True:
            device_id = Device.pop_redis_set()
            if not device_id:
                break
            device = Device.query.get(device_id)
            if not device or device.state != DEVICE_STATE_IDLE:
                continue
            is_available = device_available(device)

            if is_available:
                idle_device = device
                break
            else:
                # put device_id back
                restore_device_ids.append(device_id)
                retry_times += 1
            if retry_times > ALLOT_RETRY:
                break

        if idle_device is None:
            raise MyException(message='no free device', code=ERR_CODE_NO_DEVICE)

        # push start apk command to device
        try:
            if not app.config['DEBUG']:
                push_message_to_device(idle_device.device_name, apk.package_name, MSG_TYPE_START_APP)
        except Exception:
            pass
            # app.logger.exception('info')
            # raise MyException(message='jpush error', code=ERR_CODE_JPUSH_ERROR)

        address_map = Device.set_device_map(idle_device.device_name)

        agent_record2 = AgentRecord2()
        agent_record2.address_map = address_map
        agent_record2.apk = apk
        agent_record2.user = g.current_user
        agent_record2.device = idle_device
        agent_record2.type = RECORD_TYPE_START
        agent_record2.record_time = datetime.now()
        agent_record2.start_time = datetime.now()

        idle_device.state = DEVICE_STATE_BUSY
        db.session.add(idle_device)
        db.session.add(agent_record2)
        db.session.commit()

        # record info into redis
        start_use_device(idle_device.id)

        # restore device ids
        for restore_device_id in restore_device_ids:
            Device.push_redis_set(restore_device_id)

        # increase user's allot device num
        User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_NAME'], 1)

        ret = {
            "record_id": agent_record2.id,
            "apk": apk.to_json(),
            "address": address_map,
            "device": idle_device.to_json(),
        }

        Device.incr_allot("1.2", ALLOT_SUCCESS)

        app.logger.info('allot success user_id : %r, apk_id: %r, device_id: %r' % (user_id, apk_id, idle_device.id))

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_LIMIT_NAME'], 1)
        app.logger.exception('info')
        db.session.rollback()
        if idle_device:
            restore_device_ids.append(idle_device)
        for restore_device_id in restore_device_ids:
            Device.push_redis_set(restore_device_id)
        Device.incr_allot("1.1", ALLOT_FAIL)
        return jsonify(BaseApi.api_except_error(e))


@api1_2.route('/device/free', methods=['POST'])
def free_device():
    try:
        user_id = g.current_user.id
        apk_id = request.json.get('apk_id')
        device_id = request.json.get('device_id')
        record_id = request.json.get('record_id')

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')
        if apk_id is None or apk_id == '':
            raise ValidationError('does not have a apk id')
        if device_id is None or device_id == '':
            raise ValidationError('does not have a device id')
        if record_id is None or record_id == '':
            raise ValidationError('does not have a record id')

        apk = Apk.query.get(apk_id)
        if not apk:
            raise ValidationError('apk does not exists')

        device = Device.query.filter_by(id=device_id).first()
        if not device:
            raise ValidationError('device does not exists')

        end_record = AgentRecord2.query.filter_by(start_id=record_id).first()
        if end_record is not None or device.state == DEVICE_STATE_IDLE:
            raise ValidationError('already free')

        start_agent_record = AgentRecord2.query.filter_by(
            type=RECORD_TYPE_START,
            user_id=user_id,
            apk_id=apk_id,
            device_id=device_id,
            id=record_id).first()

        if start_agent_record is None:
            raise ValidationError('start record does not exists')

        if start_agent_record.address_map:
            Device.del_device_map(start_agent_record.address_map)

        # push start apk command to device
        try:
            if not app.config['DEBUG']:
                push_message_to_device(device.device_name, apk.data_file_names, MSG_TYPE_CLEAR)
        except Exception as e:
            pass
            # app.logger.exception('info')
            # return jsonify(BaseApi.api_jpush_error())

        agent_rocord2 = AgentRecord2()
        agent_rocord2.start_id = record_id
        agent_rocord2.apk = apk
        agent_rocord2.user = g.current_user
        agent_rocord2.device = device
        agent_rocord2.type = RECORD_TYPE_END
        agent_rocord2.record_time = datetime.now()
        agent_rocord2.time_long = (agent_rocord2.record_time - start_agent_record.record_time).seconds
        agent_rocord2.start_time = start_agent_record.record_time

        device.state = DEVICE_STATE_IDLE

        db.session.add(device)
        db.session.add(agent_rocord2)
        db.session.commit()

        # record some info into redis
        end_use_device(device_id, agent_rocord2.time_long)

        # add device into queue
        Device.push_redis_set(device.id)

        # decrease user's allot device num
        User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_NAME'], -1)
        # increase user's allot device num limit
        User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_LIMIT_NAME'], 1)

        ret = {
            "device_id": device_id,
            "device_name": device.device_name
        }

        app.logger.info('free success user_id : %r, device_id: %r, record_id: %r' % (user_id, device_id, record_id))

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        db.session.rollback()
        return jsonify(BaseApi.api_system_error(e.message))


@api1_2.route('/device/user')
def user_device():
    try:
        user_id = g.current_user.id
        apk_id = request.args.get('apk_id')
        user_records = get_agent_record_by_user_id_v2(user_id, apk_id)

        ret = []
        for user_record in user_records:
            one = user_record.device.to_json()
            one['apk_id'] = user_record.apk_id
            one['record_id'] = user_record.id
            one['address'] = user_record.address_map
            one['start_time'] = datetime_timestamp(user_record.start_time)
            one['remark'] = user_record.remark
            ret.append(one)

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_2.route('/device/user/web')
def user_device_web():
    try:
        user_id = g.current_user.id
        apk_id = request.args.get('apk_id')
        user_records = get_agent_record_by_user_id_v2(user_id, apk_id)
        ret = []
        for user_record in user_records:
            one = user_record.device.to_json()
            one['apk_id'] = user_record.apk_id
            one['apk_name'] = user_record.apk.apk_name
            one['apk_icon'] = filter_upload_url(user_record.apk.icon_url)
            one['apk_banner'] = filter_upload_url(user_record.apk.banner_url)
            one['record_id'] = user_record.id
            one['start_time'] = datetime_timestamp(user_record.start_time)
            one['address'] = user_record.address_map
            one['remark'] = user_record.remark
            ret.append(one)

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
