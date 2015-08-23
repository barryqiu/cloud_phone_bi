# from flask import g, jsonify
# from flask.ext.httpauth import HTTPBasicAuth
# from ..models import User
# from . import api
# from .errors import unauthorized, forbidden
#
# auth = HTTPBasicAuth()
#
#
#
#
# @auth.error_handler
# def auth_error():
#     return unauthorized('Invalid credentials')
#
#
# @api.before_request
# @auth.login_required
# def before_request():
#     if not g.current_user.is_anonymous() and \
#             not g.current_user.confirmed:
#         return forbidden('Unconfirmed account')
#
#
# @api.route('/token')
# def get_token():
#     if g.current_user.is_anonymous() or g.token_used:
#         return unauthorized('Invalid credentials')
#     return jsonify({'token': g.current_user.generate_auth_token(
#         expiration=3600), 'expiration': 3600})
