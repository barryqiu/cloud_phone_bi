from flask import jsonify, request
from . import api
from .base_api import BaseApi
from flask import current_app as app
from ..models import Game


@api.route('/game')
def get_games():
    try:
        games = Game.query.filter_by(state=1).all()
        return jsonify(BaseApi.api_success([game.to_json() for game in games]))
    except BaseException, e:
        app.logger.error(e.message)
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/game/share')
def get_games_share():
    try:
        return jsonify(BaseApi.api_success('1'))
    except BaseException, e:
        app.logger.error(e.name+e.message)
        return jsonify(BaseApi.api_system_error(e.name+e.message))
