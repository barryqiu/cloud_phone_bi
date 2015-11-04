from flask import jsonify, request, g
from . import api
from .base_api import BaseApi
from manage import app
from ..models import User, UserNotice, GameTask
from .. import db


@api.route('/game/task/<int:game_id>')
def get_tasks(game_id):
    try:
        tasks = GameTask.query.filter_by(game_id=game_id).all()
        if tasks is None:
            return jsonify(BaseApi.api_wrong_param())
        return jsonify(BaseApi.api_success([task.to_json() for task in tasks]))
    except Exception, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))

