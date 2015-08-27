from flask import jsonify, request, current_app, url_for
from . import api
from .base_api import BaseApi
from ..models import User
from ..models import Device
from .. import db

@api.route('/device/<string:name>')
def get_deviice(name):
    try:
        device = Device.query.filter_by(device_name=name).first()
        if device is None:
            return (jsonify(BaseApi.api_wrong_param()))
        return jsonify(BaseApi.api_success(device.to_json()))
    except Exception, e:
        return jsonify(BaseApi.api_system_error())


@api.route('/device')
def get_all_device():
    try:
        devices = Device.query.all()
        return jsonify(BaseApi.api_success([device.to_json() for device in devices]))
    except BaseException, e:
        print(e.message)
        return jsonify(BaseApi.api_system_error())


@api.route('/device', methods=['POST'])
def new_device():
    try:
        device = Device.from_json(request.json)
        now_device = User.query.filter_by(device_name = device.device_name).first()
        if now_device:
            return jsonify(BaseApi.api_success(now_device.to_json()))
        db.session.add(device)
        db.session.commit()
        return jsonify(BaseApi.api_success(device.to_json()))
    except BaseException, e:
        print(e.message)
        return jsonify(BaseApi.api_system_error())