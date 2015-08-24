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
    password = db.Column(db.String(64))
    system_version = db.Column(db.String(64))
    imei = db.Column(db.String(64))
    imsi = db.Column(db.String(64))
    model_number = db.Column(db.String(64))
    collect_time = db.Column(db.DateTime(), default=datetime.utcnow)
    android_id = db.Column(db.String(64))
    mac = db.Column(db.String(32))
    state = db.Column(db.Integer, default=1)
    level = db.Column(db.Integer, default=0)

    @staticmethod
    def from_json(json_user):
        user = User()
        user.mobile_num = json_user.get('mobile_num')
        if user.mobile_num is None or user.mobile_num == '':
            raise ValidationError('user does not have a mobile_num')
        user.password = json_user.get('password')
        user.system_version = json_user.get('system_version')
        return user

    def to_json(self):
        json_user = {
            'id': self.id,
            'mobile_bum': self.mobile_num,
            'system_version': self.system_version,
            'imei': self.imeim,
            'imsi': self.imsi,
            'model_num': self.model_number,
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
    collect_time = db.Column(db.DateTime(), default=datetime.utcnow)
    state = db.Column(db.Integer, default=1)

    @staticmethod
    def from_json(json_device):
        device = Device();
        device.device_name = json_device.get('device_name')
        if device.device_name is None or device.device_name == '':
            raise ValidationError('device does not have a name')
        device.random_code = json_device.get('random_code')
        if device.random_code is None or device.random_code == '':
            raise ValidationError('device does not have a random code')
        return device

    def to_json(self):
        json_deive = {
            'id': self.id,
            'deivice_name': self.device_name,
            'random_code': self.random_code,
            'collect_time': self.collect_time,
            'state': self.state
        }
        return json_deive

    def __repr__(self):
        return '<Device %r>' % self.device_name
