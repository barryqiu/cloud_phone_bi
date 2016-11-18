from flask import jsonify

from ..utils import convert_pagination
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


@api1_1.route('/apk/<int:page>')
def get_apk(page):
    pagination = Apk.query.order_by(Apk.add_time.desc()).paginate(
        page, per_page=app.config['DEVICE_NUM_PER_PAGE'], error_out=False)
    ret = {'apks': [apk.to_json() for apk in pagination.items], 'pageinfo': convert_pagination(pagination)}
    return jsonify(BaseApi.api_success(ret))
