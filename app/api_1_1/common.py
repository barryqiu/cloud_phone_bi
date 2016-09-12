from flask import jsonify
import time
from app.api_1_0.base_api import BaseApi
from . import api1_1


@api1_1.route('/unixtime')
def unix_time():
    return jsonify(BaseApi.api_success(time.time()))
