from flask import Blueprint

apk = Blueprint('apk', __name__)

from . import views
