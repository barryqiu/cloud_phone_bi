from flask import jsonify,  g
from . import api1_1
from app.api_1_0.base_api import BaseApi
from flask import current_app as app
from app.models import Server


@api1_1.route('/servers')
def get_servers():
    try:
        servers = Server.query.filter_by().all()
        return jsonify(BaseApi.api_success([server.to_json() for server in servers]))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
