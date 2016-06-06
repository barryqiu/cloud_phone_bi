from flask import jsonify, request
from sqlalchemy import and_

from . import api
from .base_api import BaseApi
from flask import current_app as app
from ..models import Game, GameGift, GiftRecord
from .. import db


@api.route('/game')
def get_games():
    try:
        games = Game.query.filter_by(state=1).all()
        return jsonify(BaseApi.api_success([game.to_json() for game in games]))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/game/<int:game_id>')
def get_game(game_id):
    try:
        game = Game.query.get(game_id)
        return jsonify(BaseApi.api_success(game.to_json()))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/game/trial')
def get_trial_games():
    try:
        games = Game.query.filter_by(state=2).all()
        return jsonify(BaseApi.api_success([game.to_json() for game in games]))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.message))


@api.route('/game/share')
def get_games_share():
    try:
        return jsonify(BaseApi.api_success('1'))
    except Exception as e:
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.name + e.message))


@api.route('/game/gift/<int:game_id>')
def get_game_gift(game_id):
    try:
        mobile = request.args['mobile']

        gift_record = GiftRecord.query.filter(
            and_(GiftRecord.game_id == game_id, GiftRecord.mobile == mobile)).first()

        if gift_record:
            return jsonify(BaseApi.api_success(""))

        gift = db.session.query(GameGift).filter(
            and_(GameGift.game_id == game_id, GameGift.state == 0)).with_for_update(read=True).first()
        if not gift:
            return jsonify(BaseApi.api_success(""))

        gift.state = 1
        db.session.add(gift)

        gift_record = GiftRecord()
        gift_record.gift_id = gift.id
        gift_record.game_id = game_id
        gift_record.mobile = mobile
        db.session.add(gift_record)
        db.session.commit()
        return jsonify(BaseApi.api_success(gift.code))
    except Exception as e:
        db.session.rollback()
        app.logger.exception('info')
        return jsonify(BaseApi.api_system_error(e.name + e.message))
