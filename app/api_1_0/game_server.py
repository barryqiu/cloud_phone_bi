from flask import jsonify
from . import api
from .base_api import BaseApi
from flask import current_app as app
from ..models import GameTask, GameServer


@api.route('/game/server/<int:game_id>')
def get_servers(game_id):
    try:
        servers = GameServer.query.filter_by(game_id=game_id).all()
        if servers is None:
            return jsonify(BaseApi.api_wrong_param())
        return jsonify(BaseApi.api_success([server.to_json() for server in servers]))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))
