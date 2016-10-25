from datetime import datetime
from flask import render_template, url_for, flash,redirect
from flask import current_app as app
from .. import db

from . import device
from flask.ext.login import login_required
from app.device.device_api import get_agent_record_by_device_id, end_use_device
from app.exceptions import ValidationError
from app.utils import push_message_to_device
from ..models import Device, AgentRecord, Game, User

DEVICE_STATE_DEL = 0
DEVICE_STATE_IDLE = 1
DEVICE_STATE_BUSY = 2

RECORD_TYPE_START = 0
RECORD_TYPE_END = 1


@device.route('/list', defaults={'page': 1})
@device.route('/list/<int:page>')
@login_required
def device_list(page):
    pagination = Device.query.order_by(Device.collect_time.desc()).paginate(
        page, per_page=app.config['DEVICE_NUM_PER_PAGE'], error_out=False)
    devices = pagination.items
    return render_template('device/list.html', devices=devices, pagination=pagination)


@device.route('/free/<page>/<device_id>')
@login_required
def free_device(page, device_id):
    try:
        start_record = get_agent_record_by_device_id(device_id)
        if start_record is None:
            raise ValidationError('already free')

        if start_record.address_map:
            Device.del_device_map(start_record.address_map)

        game = Game.query.get(start_record.game_id)
        agent_device = Device.query.get(device_id)

        # push start game command to device
        push_message_to_device(agent_device.device_name, game.data_file_names, 'clear')

        agent_record = AgentRecord()
        agent_record.start_id = start_record.id
        agent_record.game_id = game.id
        agent_record.user_id = start_record.user_id
        agent_record.device_id = device_id
        agent_record.server_id = start_record.server_id
        agent_record.type = RECORD_TYPE_END
        agent_record.record_time = datetime.now()
        agent_record.time_long = (agent_record.record_time - start_record.record_time).seconds
        agent_record.start_time = start_record.record_time

        agent_device.state = DEVICE_STATE_IDLE

        db.session.add(agent_device)
        db.session.add(agent_record)
        db.session.commit()

        # add device into queue
        Device.push_redis_set(agent_device.id)

        end_use_device(device_id, agent_record.time_long)

        # decrease user's allot device num
        User.redis_incr_ext_info(start_record.user_id, app.config['ALLOT_NUM_NAME'], -1)
        User.redis_incr_ext_info(start_record.user_id, app.config['ALLOT_NUM_LIMIT_NAME'], 1)
        flash("free device %s success." % device_id)
    except Exception as e:
        db.session.rollback()
        flash("free device  %s fail. error: %s" % (device_id,  e.message))
    return redirect(url_for('device.device_list', page=page))
