from flask import jsonify
from . import api1_1
from ..api_1_0.base_api import BaseApi
from ..models import *
from flask import current_app as app


@api1_1.route('/apk/rec')
def get_rec_apk():
    try:
        rec_apk_list = db.session.query(Apk).filter(Apk.rec > 0).order_by(-Apk.rec).all()
        return jsonify(BaseApi.api_success([apk.to_json() for apk in rec_apk_list]))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))