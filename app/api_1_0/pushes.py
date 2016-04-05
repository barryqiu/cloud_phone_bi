import json

__author__ = 'love'
from flask import jsonify, request
from . import api
from app.exceptions import ValidationError
from app.utils import push_message_to_alias
from .base_api import BaseApi
from flask import current_app as app
from .. import db


@api.route('/push', methods=['POST'])
def new_push():
    try:
        msg_type = request.json.get('msg_type')
        if not msg_type:
            raise ValidationError('no msg type')

        device_id = request.json.get('device_id')
        if not device_id:
            raise ValidationError('no device id')

        content = request.json.get('content')

        ret = push_message_to_alias(content, msg_type, device_id.encode('utf-8'))

        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
