from flask import render_template, redirect, url_for, flash
from .. import db
from . import push
import jpush
from ..models import DevicePushMessage
from .forms import AddPushForm
from flask import current_app as app


@push.route('/add', methods=['GET', 'POST'])
def push_add():
    form = AddPushForm()
    if form.validate_on_submit():
        try:
            push = DevicePushMessage()
            push.platform = form.platform.data
            push.audience = form.audience.data
            push.message_type = form.message_type.data
            push.content = form.content.data
            db.session.add(push)
            db.session.commit()
            flash('add push success')
        except Exception:
            flash('add push fail', 'error')
        return redirect(url_for('push.push_list'))
    return render_template('push/add.html', form=form)


@push.route('/list', defaults={'page': 1})
@push.route('/list/<int:page>')
def push_list(page):
    pagination = DevicePushMessage.query.order_by(DevicePushMessage.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    pushes = pagination.items
    return render_template('push/list.html', pushes=pushes, pagination=pagination)


def push_message(message, message_type, platform, audience):
    _jpush = jpush.JPush(app.config['JPUSH_APP_KEY'], app.config['JPUSH_MASTER_SECRET'])
    push = _jpush.create_push()
    push.message(msg_content=message, content_type=message_type)
    push.audience = audience
    push.platform = platform
    push.send_validate()



