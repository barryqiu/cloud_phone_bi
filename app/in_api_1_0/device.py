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

        page_info = {'has_next': pagination.has_next, 'has_prev': pagination.has_prev,
                     'page': pagination.page, 'pages': pagination.pages,
                     'per_page': pagination.per_page,
                     'total': pagination.total, 'prev_num': pagination.prev_num}
        ret = {'devices': ret_device, 'pageinfo': page_info}
        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
