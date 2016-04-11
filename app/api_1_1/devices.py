from datetime import datetime
import urllib2

from flask import jsonify, request, g, Session

from . import api1_1
from sqlalchemy import and_
from flask import current_app as app
from app.api_1_0.base_api import BaseApi
from ..models import AgentRecord, Game, datetime_timestamp, GameServer, User
from ..models import Device
from .. import db
from app.exceptions import ValidationError
from app.utils import push_message_to_alias, filter_upload_url

DEVICE_STATE_DEL = 0
DEVICE_STATE_IDLE = 1
DEVICE_STATE_BUSY = 2

RECORD_TYPE_START = 0
RECORD_TYPE_END = 1


@api1_1.route('/device/allot', methods=['POST'])
def allot_device():
    restore_device_ids = []
    try:
        user_id = g.current_user.id
        game_id = request.json.get('game_id')
        server_id = request.json.get('server_id')

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')

        # judge whether bigger than the max allot num
        allot_num = User.redis_get_ext_info(user_id, app.config['ALLOT_NUM_NAME'])
        if allot_num >= app.config['MAX_ALLOT_NUM']:
            return jsonify(BaseApi.api_exceed_allot_num_error())

        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')
        if server_id is None or server_id == '':
            raise ValidationError('does not have a server_id')

        game = Game.query.get(game_id)
        if not game:
            raise ValidationError('game does not exists')

        server = GameServer.query.get(server_id)
        if not server:
            raise ValidationError('server does not exists')

        idle_device = None
        while True:
            device_id = Device.pop_redis_set()
            if not device_id:
                break
            device = Device.query.get(device_id)
            if not device or device.state != DEVICE_STATE_IDLE:
                continue
            if device_available(device):
                idle_device = device
                break
            else:
                # put device_id back
                restore_device_ids.append(device_id)

        # restore device ids
        for restore_device_id in restore_device_ids:
            Device.push_redis_set(restore_device_id)

        if idle_device is None:
            return jsonify(BaseApi.api_no_device())

        # push start game command to device
        try:
            push_message_to_alias(game.package_name, 'startapp', idle_device.id)
        except Exception:
            Device.push_redis_set(idle_device.id)
            app.logger.exception('info')
            return jsonify(BaseApi.api_jpush_error())

        agent_record = AgentRecord()
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

        # increase user's allot device num
        User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_NAME'], 1)

        ret = {
            "record_id": agent_record.id,
            "game_id": game_id,
            "server_id": server_id,
            "device": idle_device.to_json()}

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        db.session.rollback()
        for restore_device_id in restore_device_ids:
            Device.push_redis_set(restore_device_id)
        return jsonify(BaseApi.api_system_error(e.message))


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
        if not device or device.state != DEVICE_STATE_BUSY:
            raise ValidationError('wrong device id')

        end_record = AgentRecord.query.filter_by(start_id=record_id).first()
        if end_record is not None:
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

        # push start game command to device
        try:
            push_message_to_alias(game.data_file_names, 'clear', device_id)
        except Exception as e:
            app.logger.exception('info')
            return jsonify(BaseApi.api_jpush_error())

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

        # add device into queue
        Device.push_redis_set(device.id)

        # decrease user's allot device num
        User.redis_incr_ext_info(user_id, app.config['ALLOT_NUM_NAME'], -1)

        ret = {
            "device_id": device_id,
            "device_name": device.device_name
        }

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        db.session.rollback()
        return jsonify(BaseApi.api_system_error(e.message))


def device_available(device):
    if not device.user_name or not device.password:
        return False

    url = "http://yunphoneclient.shinegame.cn/connlen/" + device.device_name + "/2"
    url_top = "http://yunphoneclient.shinegame.cn"
    url3 = "http://yunphoneclient.shinegame.cn/" + device.device_name + "/screenshot.jpg?vlfnnn"

    username = device.user_name
    password = device.password
    realm = "CloudPhone"

    auth = urllib2.HTTPDigestAuthHandler()
    auth.add_password(realm, url_top, username, password)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)

    # proxy
    # proxy = urllib2.ProxyHandler({'http': 'proxy.tencent.com:8080'})
    # opener = urllib2.build_opener(proxy)
    # urllib2.install_opener(opener)

    try:
        res_data = urllib2.urlopen(url3)
        if res_data.code == 200:
            return True
        else:
            return False
    except Exception, e:
        return False


@api1_1.route('/device/user')
def user_device():
    try:
        user_id = g.current_user.id
        game_id = request.args.get('game_id')
        start_ids = []
        end_records = db.session.query(AgentRecord).filter(
            and_(AgentRecord.start_id > 0, AgentRecord.user_id == user_id)).all()

        for end_record in end_records:
            start_ids.append(end_record.start_id)

        user_records = None
        if not game_id:
            user_records = AgentRecord.query.filter(
                and_(AgentRecord.type == 0, AgentRecord.user_id == user_id, AgentRecord.id.notin_(start_ids))).all()
        else:
            user_records = AgentRecord.query.filter(
                and_(AgentRecord.type == 0, AgentRecord.user_id == user_id, AgentRecord.game_id == game_id,
                     AgentRecord.id.notin_(start_ids))).all()

        ret = []
        for user_record in user_records:
            device = Device.query.filter_by(id=user_record.device_id).first()
            one = device.to_json()
            one['game_id'] = user_record.game_id
            one['server_id'] = user_record.server_id
            one['record_id'] = user_record.id
            one['start_time'] = datetime_timestamp(user_record.start_time)
            ret.append(one)

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/device/user/web')
def user_device_web():
    try:
        user_id = g.current_user.id
        start_ids = []
        game_id = request.args.get('game_id')

        end_records = db.session.query(AgentRecord).filter(
            and_(AgentRecord.start_id > 0, AgentRecord.user_id == user_id)).all()

        for end_record in end_records:
            start_ids.append(end_record.start_id)
        user_records = None
        if not game_id:
            user_records = AgentRecord.query.filter(
                and_(AgentRecord.type == 0, AgentRecord.user_id == user_id, AgentRecord.id.notin_(start_ids))).all()
        else:
            user_records = AgentRecord.query.filter(
                and_(AgentRecord.type == 0, AgentRecord.user_id == user_id, AgentRecord.game_id == game_id,
                     AgentRecord.id.notin_(start_ids))).all()
        ret = []
        for user_record in user_records:
            device = Device.query.filter_by(id=user_record.device_id).first()
            game = Game.query.get(user_record.game_id)
            server = GameServer.query.get(user_record.server_id)
            one = device.to_json()
            one['game_id'] = user_record.game_id
            one['game_name'] = game.game_name
            one['game_icon'] = filter_upload_url(game.icon_url)
            one['game_banner'] = filter_upload_url(game.banner_url)
            one['record_id'] = user_record.id
            one['start_time'] = datetime_timestamp(user_record.start_time)
            one['server_id'] = user_record.server_id
            if server:
                one['server_name'] = server.server_name
                one['game_icon'] = filter_upload_url(server.icon_url)
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

        Device.set_device_info(device_id, info_type, content)

        return jsonify(BaseApi.api_success('sucess'))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


