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
    collect_time = db.Column(db.Integer)
    android_id = db.Column(db.String(64))
    mac = db.Column(db.String(32))
    state = db.Column(db.Integer, default=1)
    level = db.Column(db.Integer, default=0)

    @staticmethod
    def from_json(json_user):
        user = User()
        user.mobile_num = json_user.get('mobile_num')
        if user.mobile_num is None or user.mobile_num =='':
            raise ValidationError('user doer not have a mobile_num')
        user.password = json_user.get('password')
        user.system_version = json_user.get('system_version')
        return user


    def to_json(self):
        json_user = {
            'id': self.id,
            'mobile_bum': self.mobile_num,
            'system_version': self.system_version,
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.username


