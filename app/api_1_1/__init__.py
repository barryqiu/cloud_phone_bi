from flask import Blueprint
api1_1 = Blueprint('api1_1', __name__)
from . import users, devices, servers, common

