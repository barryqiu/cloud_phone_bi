from datetime import datetime
import urllib2

from flask import jsonify, request, g, Session

from . import api1_1
from sqlalchemy import and_
from flask import current_app as app
from app.api_1_0.base_api import BaseApi
from ..models import AgentRecord, Game, datetime_timestamp
from ..models import Device
from .. import db
from app.exceptions import ValidationError
from app.utils import push_message_to_alias

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

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')

        game = Game.query.get(game_id)
        if not game:
            raise ValidationError('game does not exists')

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

        agent_record = AgentRecord()
        agent_record.game_id = game_id
        agent_record.user_id = user_id
        agent_record.device_id = idle_device.id
        agent_record.type = RECORD_TYPE_START
        agent_record.record_time = datetime.now()
        agent_record.start_time = datetime.now()

        idle_device.state = DEVICE_STATE_BUSY
        db.session.add(idle_device)
        db.session.add(agent_record)
        db.session.commit()

        # push start game command to device
        push_message_to_alias(game.package_name, 'startapp', idle_device.id)

        ret = {
            "record_id": agent_record.id,
            "game_id": game_id,
            "device": idle_device.to_json()}

        return jsonify(BaseApi.api_success(ret))
    except BaseException, e:
        db.session.rollback()
        for restore_device_id in restore_device_ids:
            Device.push_redis_set(restore_device_id)
        app.logger.error(e.message)
        # return jsonify(BaseApi.api_system_error(e.message))
        raise e


@api1_1.route('/device/free', methods=['POST'])
def free_device():
    try:
        user_id = g.current_user.id
        game_id = request.json.get('game_id')
        device_id = request.json.get('device_id')
        record_id = request.json.get('record_id')

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')
        if device_id is None or device_id == '':
            raise ValidationError('does not have a device id')
        if record_id is None or record_id == '':
            raise ValidationError('does not have a record id')
        game = Game.query.get(game_id)
        if not game:
            raise ValidationError('game does not exists')

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
            id=record_id).first()

        if start_agent_record is None:
            raise ValidationError('start record does not exists')

        # push start game command to device
        push_message_to_alias(game.data_file_names, 'clear', device_id)

        agent_rocord = AgentRecord()
        agent_rocord.start_id = record_id
        agent_rocord.game_id = game_id
        agent_rocord.user_id = user_id
        agent_rocord.device_id = device_id
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

        ret = {
            "device_id": device_id,
            "device_name": device.device_name
        }

        return jsonify(BaseApi.api_success(ret))
    except BaseException, e:
        db.session.rollback()
        app.logger.error(e.message)
        # return jsonify(BaseApi.api_system_error(e.message))
        raise e


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
