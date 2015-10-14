from flask import render_template
from flask import current_app as app

from . import device
from ..models import Device


@device.route('/list', defaults={'page': 1})
@device.route('/list/<int:page>')
def device_list(page):
    pagination = Device.query.order_by(Device.collect_time.desc()).paginate(
        page, per_page=app.config['DEVICE_NUM_PER_PAGE'], error_out=False)
    devices = pagination.items
    return render_template('device/list.html', devices=devices, pagination=pagination)

