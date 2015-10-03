from flask import jsonify, request, g
from . import api
from .base_api import BaseApi
from manage import app
from ..models import User
from .. import db


@api.route('/user')
def get_user():
    try:
        return jsonify(BaseApi.api_success(g.current_user.to_json()))
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
