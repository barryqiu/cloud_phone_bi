from flask import jsonify, request, g
from . import api
from sqlalchemy import and_
from wtforms import ValidationError
from .base_api import BaseApi
from flask import current_app as app
from ..models import UserNotice, UserNoticeRel
from .. import db


@api.route('/user/notice/<int:game_id>')
def get_notice(game_id):
    try:
        notices = UserNotice.query.filter_by(game_id=game_id).all()
        if notices is None:
            return jsonify(BaseApi.api_wrong_param())
        ret = []
        for notice in notices:
            one = notice.to_json()
            if not hasattr(g, 'current_user'):
                ret.append(one)
                continue
            user_id = g.current_user.id
            notice_id = notice.id
            user_notice_rel = UserNoticeRel.query.filter(
                and_(UserNoticeRel.user_id == user_id, UserNoticeRel.notice_id == notice_id)).first()
            if user_notice_rel:
                one['isin'] = 1
            else:
                one['isin'] = 0
            ret.append(one)
        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/notice/<int:game_id>/filter')
def filter_notice(game_id):
    try:
        task_id = request.args.get('task_id')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        server_name = request.args.get('server_name')
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/notice', methods=['POST'])
def new_notice():
    try:
        user_notice = UserNotice.from_json(request.json)
        db.session.add(user_notice)
        db.session.commit()
        return jsonify(BaseApi.api_success(user_notice.to_json()))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/notice/in/<int:notice_id>')
def join_notice(notice_id):
    try:
        if not notice_id:
            raise ValidationError('does not have a notice_id')
        notice = UserNotice.query.get(notice_id)
        if not notice:
            raise ValidationError('notice does not exist')
        user_notice_rel = UserNoticeRel.query.filter(
            and_(UserNoticeRel.user_id == g.current_user.id, UserNoticeRel.notice_id == notice_id)).first()
        if user_notice_rel:
            raise ValidationError('already join in this notice')

        user_notice_rel = UserNoticeRel()
        user_notice_rel.notice_id = notice_id
        user_notice_rel.user_id = g.current_user.id
        db.session.add(user_notice_rel)
        db.session.commit()
        return jsonify(BaseApi.api_success('success'))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/user/notice')
def user_notice_list():
    try:
        user_id = g.current_user.id
        notices = db.session.query(UserNotice). \
            filter(UserNotice.id == UserNoticeRel.notice_id, UserNoticeRel.user_id == user_id)
        ret = []
        for notice in notices:
            one = notice.to_json()
            one['isin'] = 1
            ret.append(one)
        return jsonify(BaseApi.api_success(ret))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
