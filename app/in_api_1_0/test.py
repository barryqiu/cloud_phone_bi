from flask import jsonify
from . import in_api
from ..api_1_0.base_api import BaseApi
from flask.ext.login import login_required


@in_api.route('/test')
def get_servers():
    return jsonify(BaseApi.api_success("suc"))
