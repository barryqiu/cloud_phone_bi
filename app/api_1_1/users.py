from flask import jsonify,  g
from . import api1_1
from app.api_1_0.base_api import BaseApi
from flask import current_app as app


@api1_1.route('/user')
def get_user():
    try:
        return jsonify(BaseApi.api_success(g.current_user.to_json()))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))