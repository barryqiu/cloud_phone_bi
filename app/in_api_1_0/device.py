from . import in_api
from flask import jsonify
from ..api_1_0.base_api import BaseApi
from ..device.device_api import *


@in_api.route('/device/<int:device_id>')
def device_info(device_id):
    try:
        if not device_id:
            return
        all_device_info = Device.get_all_device_info(device_id)
        all_device_info = format_device_info(device_id, all_device_info)
        return jsonify(BaseApi.api_success(all_device_info))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
