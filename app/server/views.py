from json import dump
from flask import render_template, redirect, url_for, flash
from .. import db
from . import server
from werkzeug.utils import secure_filename
from ..utils import TimeUtil, upload_to_cdn
from ..models import Server
from .forms import AddServerForm
from flask import current_app as app


@server.route('/add', methods=['GET', 'POST'])
def server_add():
    form = AddServerForm()
    if form.validate_on_submit():
        try:
            new_server = Server(server_name=form.servername.data)

            filename = TimeUtil.get_time_stamp() + secure_filename(form.servericon.data.filename)
            form.servericon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
            new_server.icon_url = upload_to_cdn("/uploads/" + filename,
                                                app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
            if not new_server.icon_url:
                new_server.icon_url = "/uploads/" + filename
            db.session.add(new_server)
            db.session.commit()
            flash('add server success')
        except Exception, e:
            db.session.rollback()
            flash('add server fail' + e.message, 'error')
        return redirect(url_for('server.server_list'))
    return render_template('server/add.html', form=form)


@server.route('/list', defaults={'page': 1})
@server.route('/list/<int:page>')
def server_list(page):
    pagination = Server.query.filter_by().order_by(Server.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    servers = pagination.items
    return render_template('server/list.html', servers=servers, pagination=pagination)


@server.route('/del/<page>/<server_name>')
def server_del(page, server_name):
    try:
        server_names = server_name.split(",")
        Server.query.filter(Server.server_name.in_(server_names)).delete(synchronize_session='fetch')
        db.session.commit()
        flash('del success.')
    except Exception:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('server.server_list', page=page))
