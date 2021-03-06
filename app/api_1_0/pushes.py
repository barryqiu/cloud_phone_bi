from flask import jsonify, request
from . import api
from app.exceptions import ValidationError
from app.utils import push_message_to_device
from .base_api import BaseApi
from flask import current_app as app
from .. import db
from ..models import Device


@api.route('/push', methods=['POST'])
def new_push():
    try:
        msg_type = request.json.get('msg_type')
        if not msg_type:
            raise ValidationError('no msg type')

        device_ids = request.json.get('device_id')
        if not device_ids:
            raise ValidationError('no device id')

        deviceids = device_ids.split(",")
        devices = Device.query.filter(Device.id.in_(deviceids)).all()
        content = request.json.get('content')
        ret = False
        for device in devices:
            ret = push_message_to_device(device.device_name, content, msg_type)
        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
