from datetime import datetime
from flask import jsonify, request, g
from . import api1_1
from ..api_1_0.base_api import BaseApi, ERR_CODE_EXCEED_ALLOT_NUM_ERROR, ERR_CODE_NO_DEVICE
from ..device.device_api import *
from ..models import AgentRecord, Game, datetime_timestamp, GameServer, User
from ..models import Device
from .. import db
from ..exceptions import ValidationError, MyException
from ..utils import push_message_to_device, filter_upload_url, push_closeime_to_device
from ..constant import *


@api1_1.route('/device/allot', methods=['POST'])
def allot_device():
    restore_device_ids = []
    idle_device = None
    user_id = 0
    try:

        # raise MyException(message='exceed the max allot num error', code=ERR_CODE_EXCEED_ALLOT_NUM_ERROR)

        user_id = g.current_user.id
        game_id = request.json.get('game_id')
        server_id = request.json.get('server_id')

        num_left = User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_LIMIT_NAME'], -1)
        if num_left < 0:
            raise MyException(message='exceed the max allot num error', code=ERR_CODE_EXCEED_ALLOT_NUM_ERROR)

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')

        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')
        if server_id is None or server_id == '':
            raise ValidationError('does not have a server_id')

        game = Game.query.get(game_id)
        if not game:
            raise ValidationError('game does not exists')

        if game.allow_allot != 1:
            raise ValidationError('game is Off the shelf')

        server = GameServer.query.get(server_id)
        if not server:
            raise ValidationError('server does not exists')

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

        # push start game command to device
        try:
            if not app.config['DEBUG']:
                push_message_to_device(idle_device.device_name, game.package_name, MSG_TYPE_START_APP)
        except Exception:
            pass
            # app.logger.exception('info')
            # raise MyException(message='jpush error', code=ERR_CODE_JPUSH_ERROR)

        address_map = Device.set_device_map(idle_device.device_name)

        agent_record = AgentRecord()
        agent_record.address_map = address_map
        agent_record.game_id = game_id
        agent_record.user_id = user_id
        agent_record.server_id = server_id
        agent_record.device_id = idle_device.id
        agent_record.type = RECORD_TYPE_START
        agent_record.record_time = datetime.now()
        agent_record.start_time = datetime.now()

        idle_device.state = DEVICE_STATE_BUSY
        db.session.add(idle_device)
        db.session.add(agent_record)
        db.session.commit()

        # record info into redis
        start_use_device(idle_device.id)

        # restore device ids
        for restore_device_id in restore_device_ids:
            Device.push_redis_set(restore_device_id)

        # increase user's allot device num
        User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_NAME'], 1)

        ret = {
            "record_id": agent_record.id,
            "game_id": game_id,
            "server_id": server_id,
            "address": address_map,
            "music_url": game.music_url,
            "device": idle_device.to_json(),
            "game_icon": game.icon_url,
            "game_name": game.game_name
        }

        Device.incr_allot("1.1", ALLOT_SUCCESS)

        app.logger.error('allot success user_id : %r, game_id: %r, device_id: %r' % (user_id, game_id,  idle_device.id))

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


@api1_1.route('/device/free', methods=['POST'])
def free_device():
    try:
        user_id = g.current_user.id
        game_id = request.json.get('game_id')
        device_id = request.json.get('device_id')
        record_id = request.json.get('record_id')
        server_id = request.json.get('server_id')

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')
        if device_id is None or device_id == '':
            raise ValidationError('does not have a device id')
        if record_id is None or record_id == '':
            raise ValidationError('does not have a record id')
        # if server_id is None or server_id == '':
        #     raise ValidationError('does not have a server id')

        game = Game.query.get(game_id)
        if not game:
            raise ValidationError('game does not exists')

        # server = GameServer.query.get(server_id)
        # if not server:
        #     raise ValidationError('server does not exists')

        device = Device.query.filter_by(id=device_id).first()
        if not device:
            raise ValidationError('device does not exists')

        end_record = AgentRecord.query.filter_by(start_id=record_id).first()
        if end_record is not None or device.state == DEVICE_STATE_IDLE:
            raise ValidationError('already free')

        start_agent_record = AgentRecord.query.filter_by(
            type=RECORD_TYPE_START,
            user_id=user_id,
            game_id=game_id,
            device_id=device_id,
            # server_id=server_id,
            id=record_id).first()

        if start_agent_record is None:
            raise ValidationError('start record does not exists')

        if start_agent_record.address_map:
            Device.del_device_map(start_agent_record.address_map)

        # push start game command to device
        try:
            if not app.config['DEBUG']:
                push_message_to_device(device.device_name, game.data_file_names, MSG_TYPE_CLEAR)
                push_closeime_to_device(device.device_name)
        except Exception as e:
            pass
            # app.logger.exception('info')
            # return jsonify(BaseApi.api_jpush_error())

        agent_rocord = AgentRecord()
        agent_rocord.start_id = record_id
        agent_rocord.game_id = game_id
        agent_rocord.user_id = user_id
        agent_rocord.device_id = device_id
        agent_rocord.server_id = server_id
        agent_rocord.type = RECORD_TYPE_END
        agent_rocord.record_time = datetime.now()
        agent_rocord.time_long = (agent_rocord.record_time - start_agent_record.record_time).seconds
        agent_rocord.start_time = start_agent_record.record_time

        device.state = DEVICE_STATE_IDLE

        db.session.add(device)
        db.session.add(agent_rocord)
        db.session.commit()

        # record some info into redis
        end_use_device(device_id, agent_rocord.time_long)

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

        app.logger.error('free success user_id : %r, device_id: %r, record_id: %r' % (user_id, device_id, record_id))

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        db.session.rollback()
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/user')
def user_device():
    try:
        user_id = g.current_user.id
        game_id = request.args.get('game_id')
        user_records = get_agent_record_by_user_id(user_id, game_id)

        ret = []
        for user_record in user_records:
            device = Device.query.filter_by(id=user_record.device_id).first()
            one = device.to_json()
            one['game_id'] = user_record.game_id
            one['server_id'] = user_record.server_id
            one['record_id'] = user_record.id
            one['address'] = user_record.address_map
            one['start_time'] = datetime_timestamp(user_record.start_time)
            one['remark'] = user_record.remark
            ret.append(one)

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/user/web')
def user_device_web():
    try:
        user_id = g.current_user.id
        game_id = request.args.get('game_id')
        user_records = get_agent_record_by_user_id(user_id, game_id)
        ret = []
        for user_record in user_records:
            device = Device.query.filter_by(id=user_record.device_id).first()
            game = Game.query.get(user_record.game_id)
            one = device.to_json()
            one['game_id'] = user_record.game_id
            one['game_name'] = game.game_name
            one['game_icon'] = filter_upload_url(game.icon_url)
            one['game_banner'] = filter_upload_url(game.banner_url)
            one['record_id'] = user_record.id
            one['start_time'] = datetime_timestamp(user_record.start_time)
            one['server_id'] = user_record.server_id
            one['address'] = user_record.address_map
            one['remark'] = user_record.remark
            if user_record.server_id:
                server = GameServer.query.get(user_record.server_id)
                if server:
                    one['server_name'] = server.server_name
            ret.append(one)

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/info', methods=['POST'])
def device_info():
    try:
        device_id = request.json.get('device_id')
        info_type = request.json.get('type')
        content = request.json.get('content')

        if device_id is None or device_id == '':
            raise ValidationError('does not have a device id')
        if info_type is None or info_type == '':
            raise ValidationError('does not have type')
        if content is None or content == '':
            raise ValidationError('does not have type')

        set_device_info(device_id, info_type, content)

        return jsonify(BaseApi.api_success('sucess'))
    except Exception as e:
        # app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/ids')
def device_ids():
    try:
        devices = db.session.query(Device).filter(Device.user_name == 'a').all()
        ret = []
        for device in devices:
            one = {
                "id": device.id,
                "lan_ip": device.lan_ip,
                "device_name": device.device_name,
                "state": device.state,
            }
            ret.append(one)
        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/map/<string:alias>')
def device_map(alias):
    try:
        device_name = Device.get_device_map(alias)
        if device_name:
            return jsonify(BaseApi.api_success("success"))
        raise ValidationError('alias %s, ret %s' % (alias, device_name))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/ws/<int:device_id>')
def device_ws_state(device_id):
    try:
        if not device_id:
            return
        device = Device.query.get(device_id)
        if not device:
            raise ValidationError('device id not right')

        ws_state = Device.get_device_ws_state(device.device_name)

        if not ws_state:
            ws_state = "0"

        return jsonify(BaseApi.api_success(ws_state))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/ws/alias/<string:alias>')
def device_ws_state_by_alias(alias):
    try:
        if not alias:
            raise ValidationError('no alias')

        device_name = Device.get_device_map(alias)
        if not device_name:
            raise ValidationError("wrong alias")

        ws_state = Device.get_device_ws_state(device_name)

        if not ws_state:
            ws_state = "0"

        return jsonify(BaseApi.api_success(ws_state))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/agent/record/remark', methods=['POST'])
def edit_device_agent_record():
    try:
        user_id = g.current_user.id
        record_id = request.json.get('record_id')
        if not record_id:
            raise ValidationError('empty record_id')
        remark = request.json.get('remark')
        record = AgentRecord.query.get(record_id)
        if not record or record.user_id != user_id:
            raise ValidationError('wrong record id')

        record.remark = remark
        db.session.add(record)
        db.session.commit()
        return jsonify(BaseApi.api_success("success"))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/forward/content', methods=['POST'])
def forward_content():
    try:
        device_id = request.json.get('device_id')
        if not device_id:
            raise ValidationError('does not have a device id')

        device_id = request.json.get('device_id')
        if not device_id:
            raise ValidationError('does not have a device id')

        device = Device.query.get(device_id)
        if not device:
            raise ValidationError('device id not right')

        content = request.json.get('content')
        if not content:
            raise ValidationError('content is empty')

        app.logger.error(content)
        content = content.encode('utf-8')

        if push_message_to_device(device.device_name, content, MSG_TYPE_WEBKEY_INPUT):
            return jsonify(BaseApi.api_success("suc"))
        return jsonify(BaseApi.api_push_msg_error())
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))

