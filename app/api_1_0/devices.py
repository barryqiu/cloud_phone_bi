from datetime import datetime
import urllib2

from flask import jsonify, request, g, Session

from . import api
from sqlalchemy import and_
from .base_api import BaseApi
from manage import app
from ..models import AgentRecord
from ..models import Device
from .. import db
from app.exceptions import ValidationError

DEVICE_STATE_DEL = 0
DEVICE_STATE_IDLE = 1
DEVICE_STATE_BUSY = 2

RECORD_TYPE_START = 0
RECORD_TYPE_END = 1


@api.route('/device/<string:name>')
def get_device(name):
    try:
        device = Device.query.filter_by(device_name=name).first()
        if device is None:
            return jsonify(BaseApi.api_wrong_param())
        return jsonify(BaseApi.api_success(device.to_json()))
    except Exception, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/device')
def get_all_device():
    try:
        devices = Device.query.all()
        return jsonify(BaseApi.api_success([device.to_json() for device in devices]))
    except BaseException, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/device', methods=['POST'])
def new_device():
    try:
        device = Device.from_json(request.json)
        now_device = Device.query.filter_by(device_name=device.device_name).first()
        if now_device:
            return jsonify(BaseApi.api_success(now_device.to_json()))
        db.session.add(device)
        db.session.commit()
        return jsonify(BaseApi.api_success(device.to_json()))
    except BaseException, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/device/allot', methods=['POST'])
def allot_device():
    try:
        user_id = g.current_user.id
        game_id = request.json.get('game_id')

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')

        idle_devices = Device.query.filter_by(state=DEVICE_STATE_IDLE).all()

        idle_device = None
        for device in idle_devices:
            if device_available(device):
                idle_device = device
                break

        if idle_device is None:
            return jsonify(BaseApi.api_success(""))

        idle_device.state = DEVICE_STATE_BUSY

        agent_rocord = AgentRecord()
        agent_rocord.game_id = game_id
        agent_rocord.user_id = user_id
        agent_rocord.device_id = idle_device.id
        agent_rocord.type = RECORD_TYPE_START
        agent_rocord.record_time = datetime.now()

        db.session.add(agent_rocord)
        db.session.add(idle_device)
        db.session.commit()
        print jsonify(idle_device.to_json())
        ret = {
            "record_id": agent_rocord.id,
            "game_id": game_id,
            "device": idle_device.to_json()}
        return jsonify(BaseApi.api_success(ret))
    except BaseException, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/device/free', methods=['POST'])
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

        device = Device.query.filter_by(id=device_id).first()
        if device.state != DEVICE_STATE_BUSY:
            raise ValidationError('wrong device id')

        start_agent_record = AgentRecord.query.filter_by(
            type=RECORD_TYPE_START,
            user_id=user_id,
            game_id=game_id,
            device_id=device_id,
            id=record_id).first()

        if start_agent_record is None:
            raise ValidationError('start record does not exists')

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

        ret = {
            "device_id": device_id,
            "device_name": device.device_name
        }

        return jsonify(BaseApi.api_success(ret))
    except BaseException, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/device/user')
def user_device():
    try:
        user_id = g.current_user.id
        start_ids = []
        end_records = db.session.query(AgentRecord).filter(AgentRecord.start_id.notin_([0])).all()

        for end_record in end_records:
            start_ids.append(end_record.start_id)

        user_records = AgentRecord.query.filter(
            and_(AgentRecord.type == 0, AgentRecord.user_id == user_id, AgentRecord.id.notin_(start_ids))).all()

        device_ids = []
        for user_record in user_records:
            device_ids.append(user_record.device_id)

        devices =  db.session.query(Device).filter(Device.id.in_(device_ids)).all()

        return jsonify(BaseApi.api_success([device.to_json() for device in devices]))
    except Exception, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


def device_available(device):
    url = "http://yunphoneclient.shinegame.cn/connlen/"+device.device_name+"/2"
    url_top = "http://yunphoneclient.shinegame.cn"
    url3 = "http://yunphoneclient.shinegame.cn/"+device.device_name+"/screenshot.jpg?vlfnnn"

    username = device.user_name
    password = device.password
    realm = "Webkey"

    auth = urllib2.HTTPDigestAuthHandler()
    auth.add_password(realm,url_top,username,password)
    opener = urllib2.build_opener(auth)
    urllib2.install_opener(opener)
    try:
        res_data = urllib2.urlopen(url3)
        if res_data.code == 200:
            return True
        else:
            return False
    except:
        return False


