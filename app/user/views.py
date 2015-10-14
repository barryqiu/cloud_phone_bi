from . import user

from flask import render_template
from flask import current_app as app

from ..models import User


@user.route('/list', defaults={'page': 1})
@user.route('/list/<int:page>')
def user_list(page):
    pagination = User.query.filter_by(state=1).order_by(User.collect_time.desc()).paginate(
        page, per_page=app.config['USER_NUM_PER_PAGE'], error_out=False)
    users = pagination.items
    return render_template('user/list.html', users=users, pagination=pagination)
