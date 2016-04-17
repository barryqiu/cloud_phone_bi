from flask import Blueprint

trial_game = Blueprint('trial_game', __name__)

from . import views
