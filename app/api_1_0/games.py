from flask import jsonify, request
from . import api
from .base_api import BaseApi
from manage import app
from ..models import Game
from .. import db


@api.route('/game')
def get_games():
    try:
        games = Game.query.filter_by(state=1).all()
        return jsonify(BaseApi.api_success([game.to_json() for game in games]))
    except BaseException, e:
        app.logger.error(e.name+e.message)
        return jsonify(BaseApi.api_system_error(e.name+e.message))
