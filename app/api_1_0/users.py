from flask import jsonify, request, g
from . import api
from app.sms.SmsUtil import send_smd
from app.utils import generate_verification_code
from .base_api import BaseApi
from flask import current_app as app
from ..models import User
from .. import db, redis_store


@api.route('/user')
def get_user():
    try:
        return jsonify(BaseApi.api_success(g.current_user.to_json()))
    except Exception, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/code/<mobile>')
def get_verify_code(mobile):
    try:
        code = generate_verification_code()

        # store code into redis
        redis_key = ('YUNPHONE:VERIFYCODE:%s' % mobile).upper()
        redis_store.set(redis_key, code)
        redis_store.expire(redis_key, app.config['VERIFY_CODE_TTL'])
        send_smd(mobile, code, 300)

        return jsonify(BaseApi.api_success(code))
    except Exception, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user', methods=['POST'])
def new_user():
    try:
        user = User.from_json(request.json)
        now_user = User.query.filter_by(mobile_num=user.mobile_num).first()
        if now_user:
            return jsonify(BaseApi.api_success(now_user.to_json()))
        db.session.add(user)
        db.session.commit()
        return jsonify(BaseApi.api_success(user.to_json()))
    except BaseException, e:
        db.session.rollback()
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))
