from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, users, errors, devices, games, user_notice, game_task, pushes
