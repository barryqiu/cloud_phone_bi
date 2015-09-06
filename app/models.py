from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from app.exceptions import ValidationError
from . import db


class User(db.Model):
    __tablename__ = 'tb_user'
    id = db.Column(db.Integer, primary_key=True)
    mobile_num = db.Column(db.String(16), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    system_version = db.Column(db.String(64))
    imei = db.Column(db.String(64))
    imsi = db.Column(db.String(64))
    model_number = db.Column(db.String(64))
    collect_time = db.Column(db.DateTime(), default=datetime.now)
    android_id = db.Column(db.String(64))
    mac = db.Column(db.String(32))
    state = db.Column(db.Integer, default=1)
    level = db.Column(db.Integer, default=0)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600*24*30):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600*24*30):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    @staticmethod
    def from_json(json_user):
        user = User()
        user.mobile_num = json_user.get('mobile_num')
        if user.mobile_num is None or user.mobile_num == '':
            raise ValidationError('user does not have a mobile_num')
        user.password = json_user.get('password')
        if user.password_hash is None or user.password_hash == '':
            raise ValidationError('user does not have a password')
        user.confirmed = True
        user.system_version = json_user.get('system_version')
        user.model_number = json_user.get('model_number')
        user.imei = json_user.get('imei')
        user.imsi = json_user.get('imsi')
        user.android_id = json_user.get('android_id')
        user.mac = json_user.get('mac')
        return user

    def to_json(self):
        json_user = {
            'id': self.id,
            'mobile_num': self.mobile_num,
            'system_version': self.system_version,
            'imei': self.imei,
            'imsi': self.imsi,
            'collect_time': self.collect_time,
            'android_id': self.android_id,
            'mac': self.mac,
            'state': self.state,
            'level': self.level
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


class Device(db.Model):
    __tablename__ = 'tb_device'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(50), unique=True, index=True)
    random_code = db.Column(db.String(30))
    user_name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    collect_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)

    @staticmethod
    def from_json(json_device):
        device = Device()
        device.device_name = json_device.get('device_name')
        if device.device_name is None or device.device_name == '':
            raise ValidationError('device does not have a name')

        device.random_code = json_device.get('random_code')
        if device.random_code is None or device.random_code == '':
            raise ValidationError('device does not have a random code')

        device.user_name = json_device.get('user_name')
        if device.user_name is None or device.user_name == '':
            raise ValidationError('device does not have a username')

        device.password = json_device.get('password')
        if device.password is None or device.password == '':
            raise ValidationError('device does not have a password')

        return device

    def to_json(self):
        json_deive = {
            'id': self.id,
            'deivice_name': self.device_name,
            'random_code': self.random_code,
            'user_name': self.user_name,
            'password': self.password,
            'collect_time': self.collect_time,
            'state': self.state
        }
        return json_deive

    def __repr__(self):
        return '<Device %r>' % self.device_name


class Game(db.Model):
    __tablename__ = 'tb_game'
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(50), unique=True, index=True)
    icon_url = db.Column(db.String(150))
    add_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)

    @staticmethod
    def from_json(json_game):
        game = Game();
        game.game_name = json_game.get('game_name')
        if game.game_name is None or game.game_name == '':
            raise ValidationError('game does not have a name')
        return game

    def to_json(self):
        json_deive = {
            'id': self.id,
            'game_name': self.game_name,
            'icon_url': self.icon_url,
            'add_time': self.add_time,
            'state': self.state,
        }
        return json_deive

    def __repr__(self):
        return '<Game %r>' % self.game_name


class AgentRecord(db.Model):
    __tablename__ = 'tb_agent_record'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime(), default=datetime.now())
    record_time = db.Column(db.DateTime(), default=datetime.now())
    time_long = db.Column(db.Integer)
    game_id = db.Column(db.Integer)
    device_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    state = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Record %r,%r,%r>' % self.user_id % self.game_id % self.device_id
