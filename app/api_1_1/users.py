from flask import jsonify,  g, request
from . import api1_1
from ..api_1_0.base_api import BaseApi
from ..models import *
from flask import current_app as app


@api1_1.route('/user')
def get_user():
    try:
        return jsonify(BaseApi.api_success(g.current_user.to_json()))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/user/apk', methods=['GET'])
def get_user_apk():
    try:
        return jsonify(BaseApi.api_success([apk.apk.to_json() for apk in g.current_user.apk.all()]))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/user/apk/add/<int:apk_id>')
def add_user_apk(apk_id):
    try:
        if not apk_id:
            raise ValidationError('does not have a user id')
        apk = Apk.query.get(apk_id)
        if not apk:
            raise ValidationError('wrong apk id')
        g.current_user.add_apk(apk)
        return jsonify(BaseApi.api_success("success"))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api1_1.route('/user/apk/del/<int:apk_id>')
def del_user_apk(apk_id):
    try:
        if not apk_id:
            raise ValidationError('does not have a user id')
        apk = Apk.query.get(apk_id)
        if not apk:
            raise ValidationError('wrong apk id')
        g.current_user.del_apk(apk)
        return jsonify(BaseApi.api_success("success"))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
