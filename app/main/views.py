from flask import render_template, abort, request, \
    current_app, send_from_directory
from flask.ext.login import login_required
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from flask import current_app as app


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/admin', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')


@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.root_path + '/' + app.config['UPLOAD_FOLDER'],
                               filename)

