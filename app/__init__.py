# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.redis import FlaskRedis
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
redis_store = FlaskRedis()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    @app.template_filter('datetimeformat')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        return value.strftime(format)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    redis_store.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .game import game as game_blueprint
    app.register_blueprint(game_blueprint, url_prefix='/game')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .device import device as device_blueprint
    app.register_blueprint(device_blueprint, url_prefix='/device')

    from .push import push as push_blueprint
    app.register_blueprint(push_blueprint, url_prefix='/push')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/1.0')

    from .api_1_1 import api1_1 as api_1_1_blueprint
    app.register_blueprint(api_1_1_blueprint, url_prefix='/api/1.1')

    from .server import server as server_blueprint
    app.register_blueprint(server_blueprint, url_prefix='/server')

    return app
