from datetime import datetime

from flask import jsonify, request

from . import api
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
        user_id = request.json.get('user_id')
        game_id = request.json.get('game_id')

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')

        idle_device = Device.query.filter_by(state=DEVICE_STATE_IDLE).first()

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
            "device": idle_device.to_json()}
        return jsonify(BaseApi.api_success(ret))
    except BaseException, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/device/free', methods=['POST'])
def free_device():
    try:
        print(datetime.now())
        user_id = request.json.get('user_id')
        game_id = request.json.get('game_id')
        device_id = request.json.get('device_id')
        record_id = request.json.get('record_id')

        if user_id is None or user_id == '':
            raise ValidationError('does not have a user id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')
        if game_id is None or game_id == '':
            raise ValidationError('does not have a game id')

        device = Device.query.get_or_404(device_id)
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

        return jsonify(BaseApi.api_success("free success"))
    except BaseException, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))
