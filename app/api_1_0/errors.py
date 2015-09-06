from flask import jsonify
from app.exceptions import ValidationError
from . import api


ERR_CODE_SYSTEM = 99
ERR_CODE_BAD_REQUEST = 100
ERR_CODE_UNAUTHORIZED = 101
ERR_CODE_FORBIDDEN = 101
ERR_CODE_WRONG_PARAM = 1
ERR_CODE_SUCCESS = 0


def bad_request(message):
    response = jsonify({'err_code': ERR_CODE_BAD_REQUEST, 'content': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'err_code': ERR_CODE_UNAUTHORIZED, 'content': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'err_code': ERR_CODE_FORBIDDEN, 'content': message})
    response.status_code = 403
    return response


def system_error(message):
    response = jsonify({'err_code': ERR_CODE_SYSTEM, 'content': message})
    response.status_code = 500
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
