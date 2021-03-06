import random
from flask import jsonify, request, g
from . import api
from app.exceptions import ValidationError
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
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/code/<mobile>')
def get_verify_code(mobile):
    try:
        # store code into redis
        redis_key_data = ('YUNPHONE:VERIFYCODE:%s' % mobile).upper()
        redis_key_record = ('YUNPHONE:VERIFYCODE:RECORD:%s' % mobile).upper()
        code = redis_store.get(redis_key_record)

        if code:
            return jsonify(BaseApi.api_success(code))

        code = generate_verification_code()
        redis_store.set(redis_key_data, code)
        redis_store.expire(redis_key_data, app.config['VERIFY_CODE_DATA_TTL'])
        redis_store.set(redis_key_record, code)
        redis_store.expire(redis_key_record, app.config['VERIFY_CODE_RECORD_TTL'])
        send_smd(mobile, code, app.config['VERIFY_CODE_DATA_TTL'])

        return jsonify(BaseApi.api_success('success'))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user', methods=['POST'])
def new_user():
    try:
        user = User.from_json(request.json)

        invite_code = request.json.get('invite_code')
        if invite_code != "48936542":
            raise ValidationError("wrong invite_code")
        # verify code
        # code = request.json.get('code')
        # redis_key = ('YUNPHONE:VERIFYCODE:%s' % user.mobile_num).upper()
        # code_redis = redis_store.get(redis_key)
        #
        # if not app.config['DEBUG']:
        #     if not code_redis or code != code_redis:
        #         return jsonify(BaseApi.api_wrong_verify_code())

        now_user = User.query.filter_by(mobile_num=user.mobile_num).first()
        if now_user:
            return jsonify(BaseApi.api_already_reg_error())
        db.session.add(user)
        db.session.commit()
        User.redis_incr_ext_info(user.id, app.config['ALLOT_NUM_LIMIT_NAME'], app.config['MAX_ALLOT_NUM'])
        return jsonify(BaseApi.api_success(user.to_json()))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/random/<int:num>')
def random_user(num):
    x = 1
    ret = []
    while True:
        if x > num:
            break
        user = User()
        user.mobile_num = int(random.random() * 100000000) + 100000000
        pd = int(random.random() * 100000) + 100000
        user.password = "%s" % pd
        user.confirmed = True
        user.system_version = 'random'
        user.model_number = 'random'
        user.imei = 'random'
        user.imsi = 'random'
        user.android_id = 'random'
        user.mac = 'random'
        now_user = User.query.filter_by(mobile_num=user.mobile_num).first()
        if now_user:
            continue
        db.session.add(user)
        db.session.commit()
        json_user = {
            'id': user.id,
            'mobile_num': user.mobile_num,
            'password': pd
        }
        ret.append(json_user)
        x += 1
    return jsonify(BaseApi.api_success(ret))


@api.route('/user/password', methods=['POST'])
def edit_password():
    try:
        mobile_num = request.json.get('mobile_num')
        if mobile_num is None or mobile_num == '':
            raise ValidationError('user does not have a mobile_num')
        password = request.json.get('password')
        if password is None or password == '':
            raise ValidationError('user does not have a password')

        # verify code
        code = request.json.get('code')
        redis_key = ('YUNPHONE:VERIFYCODE:%s' % mobile_num).upper()
        code_redis = redis_store.get(redis_key)

        if not app.config['DEBUG']:
            if not code_redis or code != code_redis:
                return jsonify(BaseApi.api_wrong_verify_code())

        now_user = User.query.filter_by(mobile_num=mobile_num).first()
        if not now_user:
            raise ValidationError('this user does not exists')
        now_user.password = password
        db.session.add(now_user)
        db.session.commit()
        return jsonify(BaseApi.api_success(now_user.to_json()))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
