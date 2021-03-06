from flask import g, jsonify, request
from flask.ext.httpauth import HTTPBasicAuth

from ..api_1_2 import api1_2
from ..api_1_1 import api1_1
from ..in_api_1_0 import in_api
from ..models import User
from . import api
from .errors import unauthorized, forbidden
import re

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(mobile_num_or_token, password):
    # if register no verify
    if request.endpoint == "api.new_user" or request.endpoint == "api.get_games" or \
                    request.endpoint == "api.get_verify_code" or \
                    request.endpoint == "api.get_games_share" or request.endpoint == "api.get_notice" or \
                    request.endpoint == "api.get_servers" or request.endpoint == "api.edit_password" or \
                    request.endpoint == "api1_1.get_servers" or request.endpoint == "api.get_trial_games" or \
                    request.endpoint == "api1_1.device_info" or request.endpoint == 'api1_1.device_ids' or \
                    request.endpoint == 'api.get_game' or request.endpoint == 'api.get_game_gift' or \
                    request.endpoint == 'api1_1.unix_time' or request.endpoint == 'api1_1.device_map' or \
                    request.endpoint == 'api1_2.get_run_apk_device':
        return True
    if password == '':
        pattern = re.compile(r'api\..*')
        g.current_user = User.verify_auth_token(mobile_num_or_token, not pattern.match(request.endpoint))
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(mobile_num=mobile_num_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@api1_1.before_request
@api1_2.before_request
@auth.login_required
def before_request():
    # if register no verify
    if request.endpoint != "api.get_games" and request.endpoint != "api.new_user" \
            and request.endpoint != "api.get_verify_code" \
            and request.endpoint != "api.get_games_share" and request.endpoint != "api.get_notice" \
            and request.endpoint != "api.get_servers" \
            and request.endpoint != "api.edit_password" and request.endpoint != "api1_1.get_servers" \
            and request.endpoint != 'api.get_trial_games' and request.endpoint != 'api1_1.device_info' \
            and request.endpoint != 'api1_1.device_ids' and request.endpoint != 'api.get_game' \
            and request.endpoint != 'api.get_game_gift' and request.endpoint != 'api1_1.unix_time' \
            and request.endpoint != 'api1_1.device_map' and request.endpoint != 'api1_2.get_run_apk_device' \
            and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@in_api.before_request
@auth.login_required
def in_api_before_request():
    if g.current_user.role < 3:
        return unauthorized('Invalid credentials')


@api.route('/token')
def get_token():
    if g.token_used:
        return unauthorized('Invalid credentials')
    token = g.current_user.generate_auth_token(expiration=3600 * 24 * 30)
    User.redis_set_token(g.current_user.id, token)
    return jsonify({'token': token, 'expiration': 3600 * 24 * 30})
