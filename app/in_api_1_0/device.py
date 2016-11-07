from ..exceptions import ValidationError
from ..utils import convert_pagination
from . import in_api
from flask import jsonify, request
from ..api_1_0.base_api import BaseApi
from ..device.device_api import *
from ..utils import push_message_to_device


@in_api.route('/device/<int:device_id>')
def device_info_in(device_id):
    try:
        if not device_id:
            return
        all_device_info = Device.get_all_device_info(device_id)
        all_device_info = format_device_info(device_id, all_device_info)
        return jsonify(BaseApi.api_success(all_device_info))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@in_api.route('/device/list/<int:page>')
def device_list(page):
    try:
        pagination = Device.query.order_by(Device.collect_time.desc()).paginate(
            page, per_page=app.config['DEVICE_NUM_PER_PAGE'], error_out=False)
        devices = pagination.items
        ret_device = {}
        for device in devices:
            one_device_info = Device.get_all_device_info(device.id)
            ret_device[device.id] = format_device_info(device.id, one_device_info, 1)
        ret = {'devices': ret_device, 'pageinfo': convert_pagination(pagination)}
        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@in_api.route('/device/reboot/<int:device_id>')
def device_info(device_id):
    try:
        if not device_id:
            raise ValidationError('does not have a device id')

        device = Device.query.get(device_id)
        if not device:
            raise ValidationError('device id not right')
        if push_message_to_device(device.device_name, "", MSG_TYPE_REBOOT):
            return jsonify(BaseApi.api_success("suc"))
        return jsonify(BaseApi.api_push_msg_error())
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@in_api.route('/device/forward/content', methods=['POST'])
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

        if push_message_to_device(device.device_name, content, MSG_TYPE_WEBKEY_INPUT):
            return jsonify(BaseApi.api_success("suc"))
        return jsonify(BaseApi.api_push_msg_error())
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
