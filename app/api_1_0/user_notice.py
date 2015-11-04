from flask import jsonify, request, g
from . import api
from .base_api import BaseApi
from flask import current_app as app
from ..models import UserNotice
from .. import db


@api.route('/user/notice/<int:game_id>')
def get_notice(game_id):
    try:
        notices = UserNotice.query.filter_by(game_id=game_id).all()
        if notices is None:
            return jsonify(BaseApi.api_wrong_param())
        return jsonify(BaseApi.api_success([notice.to_json() for notice in notices]))
    except Exception, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/notice', methods=['POST'])
def new_notice():
    try:
        user_notice = UserNotice.from_json(request.json)
        db.session.add(user_notice)
        db.session.commit()
        return jsonify(BaseApi.api_success(user_notice.to_json()))
    except BaseException, e:
        db.session.rollback()
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))
