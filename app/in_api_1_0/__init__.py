from flask import Blueprint

in_api = Blueprint('in_api', __name__)

from . import test, device

