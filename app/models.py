# -*- coding: utf-8 -*-
import time
from datetime import datetime
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from .constant import SERVICE_STATE
from .exceptions import ValidationError
from . import db, login_manager, redis_store
from .utils import filter_upload_url, gen_random_string, datetime_timestamp


class Admin(UserMixin, db.Model):
    __tablename__ = 'tb_admin'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    state = db.Column(db.Integer, default=1)
    role = db.Column(db.Integer, default=1)

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Admin %r>' % self.user_name


class UserApk(db.Model):
    __tablename__ = "tb_user_apk"
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'), primary_key=True)
    apk_id = db.Column(db.Integer, db.ForeignKey('tb_apk.id'), primary_key=True)
    add_time = db.Column(db.DateTime(), default=datetime.now)


class AgentRecord2(db.Model):
    __tablename__ = 'tb_agent_record2'
    id = db.Column(db.Integer, primary_key=True)
    start_id = db.Column(db.Integer, default=0)
    type = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime(), default=datetime.now())
    record_time = db.Column(db.DateTime(), default=datetime.now())
    time_long = db.Column(db.Integer, default=0)
    device_id = db.Column(db.Integer, db.ForeignKey('tb_device.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('tb_user.id'))
    address_map = db.Column(db.String(40), default='')
    apk_id = db.Column(db.Integer, db.ForeignKey('tb_apk.id'))
    remark = db.Column(db.String(150))
    state = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Record %r,%r,%r>' % self.user_id % self.game_id % self.device_id

    def to_json(self):
        json_agent_record = {
            'id': self.id,
            'start_id': self.start_id,
            'device': self.device.to_json(),
            'user': self.user.to_json(),
            'apk': self.apk.to_json(),
            'address_map': self.address_map,
            'remark': self.remark
        }
        return json_agent_record


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'tb_user'
    id = db.Column(db.Integer, primary_key=True)
    mobile_num = db.Column(db.String(16), unique=True, index=True)
    email = db.Column(db.String(128), unique=True, index=True)
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
    role = db.Column(db.Integer, default=1)

    apk = db.relationship('UserApk', foreign_keys=[UserApk.user_id],
                          backref=db.backref('user', lazy='joined'),
                          lazy='dynamic',
                          cascade='all, delete-orphan')

    agent_records = db.relationship("AgentRecord2", backref="user")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600 * 24 * 30):
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

    def generate_reset_token(self, expiration=3600 * 24 * 30):
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

    def to_json(self):
        json_user = {
            'id': self.id,
            'mobile_num': self.mobile_num,
            'system_version': self.system_version,
            'imei': self.imei,
            'imsi': self.imsi,
            'model_number': self.model_number,
            'collect_time': datetime_timestamp(self.collect_time),
            'android_id': self.android_id,
            'mac': self.mac,
            'state': self.state,
            'level': self.level,
            'email': self.email
        }
        return json_user

    def has_apk(self, apk):
        return self.apk.filter_by(apk_id=apk.id).first() is not None

    def add_apk(self, apk):
        if not self.has_apk(apk):
            user_apk = UserApk(user=self, apk=apk)
            db.session.add(user_apk)
            db.session.commit()

    def del_apk(self, apk):
        now_apk = self.apk.filter_by(apk_id=apk.id).first()
        if now_apk:
            db.session.delete(now_apk)
            db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.mobile_num

    @staticmethod
    def verify_auth_token(token, verify_current):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        if verify_current:
            new_token = User.redis_get_token(data['id'])
            if new_token and new_token != token:
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
        user.email = json_user.get('email')
        return user

    @staticmethod
    def redis_incr_ext_info(user_id, key, num):
        redis_key = ('YUNPHONE:USER_EXT:%s' % user_id).upper()
        return redis_store.hincrby(redis_key, key, num)

    @staticmethod
    def redis_get_ext_info(user_id, key):
        redis_key = ('YUNPHONE:USER_EXT:%s' % user_id).upper()
        return redis_store.hget(redis_key, key)

    @staticmethod
    def redis_get_token(user_id):
        redis_key = ('YUNPHONE:USER_TOEKN:%s' % user_id).upper()
        return redis_store.get(redis_key)

    @staticmethod
    def redis_set_token(user_id, token):
        redis_key = ('YUNPHONE:USER_TOEKN:%s' % user_id).upper()
        return redis_store.set(redis_key, token)


class Device(db.Model):
    __tablename__ = 'tb_device'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(50), unique=True, index=True)
    random_code = db.Column(db.String(30))
    user_name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    collect_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)
    lan_ip = db.Column(db.String(30))
    agent_records = db.relationship('AgentRecord2', backref='device')

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
        json_device = {
            'id': self.id,
            'device_name': self.device_name,
            'random_code': self.random_code,
            'user_name': self.user_name,
            'password': self.password,
            'collect_time': datetime_timestamp(self.collect_time),
            'state': self.state,
            'lan_ip': self.lan_ip
        }
        return json_device

    def __repr__(self):
        return '<Device %r>' % self.device_name

    @staticmethod
    def push_redis_set(device_id, set_type=0):
        # judge whether the device id is legal
        try:
            device_id = int(device_id)
        except Exception:
            return 0

        if device_id <= 0:
            return 0

        redis_key = 'YUNPHONE:DEVICES'.upper()
        if set_type:
            redis_key += "%s" % set_type
        return redis_store.sadd(redis_key, device_id)

    @staticmethod
    def pop_redis_set(set_type=0):
        redis_key = 'YUNPHONE:DEVICES'.upper()
        if set_type:
            redis_key += "%s" % set_type
        device_id = redis_store.spop(redis_key)
        return device_id

    @staticmethod
    def rem_redis_set(device_id, set_type=0):
        redis_key = 'YUNPHONE:DEVICES'.upper()
        if set_type:
            redis_key += "%s" % set_type
        count = redis_store.srem(redis_key, device_id)
        return count

    @staticmethod
    def available_num():
        redis_key = 'YUNPHONE:DEVICES'.upper()
        return redis_store.scard(redis_key)

    @staticmethod
    def set_device_info(device_id, info_type, content):
        redis_key = ('YUNPHONE:DEVICE:INFO:%s' % device_id).upper()
        redis_store.hset(redis_key, ("%s" % info_type), content)

        if info_type == SERVICE_STATE:
            active_redis_key = ('YUNPHONE:DEVICE:ACTIVE:%s' % device_id).upper()
            redis_store.set(active_redis_key, content)
            redis_store.expire(active_redis_key, 300)
        return

    @staticmethod
    def incr_device_info(device_id, info_type, content):
        redis_key = ('YUNPHONE:DEVICE:INFO:%s' % device_id).upper()
        redis_store.hincrby(redis_key, ("%s" % info_type), content)
        return

    @staticmethod
    def get_device_info(device_id, info_type):
        redis_key = ('YUNPHONE:DEVICE:INFO:%s' % device_id).upper()
        return redis_store.hget(redis_key, ("%s" % info_type))

    @staticmethod
    def get_all_device_info(device_id):
        redis_key = ('YUNPHONE:DEVICE:INFO:%s' % device_id).upper()
        return redis_store.hgetall(redis_key)

    @staticmethod
    def get_device_active(device_id):
        redis_key = ('YUNPHONE:DEVICE:ACTIVE:%s' % device_id).upper()
        return redis_store.get(redis_key)

    @staticmethod
    def set_device_map(device_name):
        random_str = gen_random_string()
        redis_key = ('YUNPHONE:DEVICE:MAP:%s' % random_str).upper()
        redis_store.set(redis_key, device_name)
        return random_str

    @staticmethod
    def del_device_map(random_str):
        redis_key = ('YUNPHONE:DEVICE:MAP:%s' % random_str).upper()
        return redis_store.delete(redis_key)

    @staticmethod
    def get_device_map(random_str):
        redis_key = ('YUNPHONE:DEVICE:MAP:%s' % random_str).upper()
        return redis_store.get(redis_key)

    @staticmethod
    def incr_allot(api, allot_result):
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        redis_key = ('YUNPHONE:DEVICE:%s:ALLOT:%s' % (api, date)).upper()
        redis_key_all = ('YUNPHONE:DEVICE:%s:ALLOT:ALL' % api).upper()
        redis_store.hincrby(redis_key, allot_result, 1)
        redis_store.hincrby(redis_key_all, allot_result, 1)
        return

    @staticmethod
    def get_device_ws_state(device_name):
        redis_key = ('YUNPHONE:DEVICE:WS:STATE:%s' % device_name).upper()
        return redis_store.get(redis_key)


class Game(db.Model):
    __tablename__ = 'tb_game'
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(50), index=True)
    icon_url = db.Column(db.String(150))
    banner_url = db.Column(db.String(150))
    music_url = db.Column(db.String(150))
    package_name = db.Column(db.String(250))
    data_file_names = db.Column(db.Text)
    game_desc = db.Column(db.Text)
    gift_desc = db.Column(db.Text)
    gift_url = db.Column(db.String(150))
    qr_url = db.Column(db.String(150))
    apk_url = db.Column(db.String(150))
    banner_side = db.Column(db.String(150))
    square_img = db.Column(db.String(150))
    add_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)  # 0：删除； 1：挂机游戏； 2：体验游戏；
    allow_allot = db.Column(db.Integer, default=0)  # 0：禁止分配； 1：允许分配

    @staticmethod
    def from_json(json_game):
        game = Game()
        game.game_name = json_game.get('game_name')
        if game.game_name is None or game.game_name == '':
            raise ValidationError('game does not have a name')
        return game

    def to_json(self):
        json_game = {
            'id': self.id,
            'game_name': self.game_name,
            'package_name': self.package_name,
            'data_file_names': self.data_file_names,
            'icon_url': filter_upload_url(self.icon_url),
            'banner_url': filter_upload_url(self.banner_url),
            'music_url': filter_upload_url(self.music_url),
            'add_time': datetime_timestamp(self.add_time),
            'game_desc': self.game_desc,
            'gift_desc': self.gift_desc,
            'gift_url': self.gift_url,
            'qr_url': self.qr_url,
            'apk_url': self.apk_url,
            'banner_side': self.banner_side,
            'square_img': self.square_img,
            'state': self.state,
            'allow_allot': self.allow_allot,
        }
        return json_game

    def __repr__(self):
        return '<Game %r>' % self.game_name


class AgentRecord(db.Model):
    __tablename__ = 'tb_agent_record'
    id = db.Column(db.Integer, primary_key=True)
    start_id = db.Column(db.Integer, default=0)
    type = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime(), default=datetime.now())
    record_time = db.Column(db.DateTime(), default=datetime.now())
    time_long = db.Column(db.Integer, default=0)
    game_id = db.Column(db.Integer, default=0)
    server_id = db.Column(db.Integer, default=0)
    device_id = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, default=0)
    address_map = db.Column(db.String(40), default='')
    state = db.Column(db.Integer, default=1)
    business_id = db.Column(db.Integer, default=0)
    remark = db.Column(db.String(150))

    def __repr__(self):
        return '<Record %r,%r,%r>' % self.user_id % self.game_id % self.device_id

    def to_json(self):
        json_agent_record = {
            'id': self.id,
            'start_id': self.start_id,
            'device_id': self.device_id,
            'user_id': self.user_id,
            'game_id': self.game_id,
            'server_id': self.server_id,
            'address_map': self.address_map,
            'remark': self.remark
        }
        return json_agent_record


class GameTask(db.Model):
    __tablename__ = 'tb_game_task'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, default=0)
    task_name = db.Column(db.String(50))
    task_des = db.Column(db.Text)
    add_time = db.Column(db.DateTime(), default=datetime.now())

    def to_json(self):
        json_game_task = {
            'id': self.id,
            'game_id': self.game_id,
            'task_name': self.task_name,
            'task_des': self.task_name,
            'add_time': datetime_timestamp(self.add_time),
        }
        return json_game_task


class Server(db.Model):
    __tablename__ = 'tb_server'
    icon_url = db.Column(db.String(150), primary_key=True)
    server_name = db.Column(db.String(50))
    add_time = db.Column(db.DateTime(), default=datetime.now())

    def to_json(self):
        json_server = {
            'icon_url': filter_upload_url(self.icon_url),
            'server_name': self.server_name,
            'add_time': datetime_timestamp(self.add_time),
        }
        return json_server


class GameServer(db.Model):
    __tablename__ = 'tb_game_server'
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(50))
    game_id = db.Column(db.Integer, default=0)
    package_name = db.Column(db.String(250))
    data_file_names = db.Column(db.Text)
    server_des = db.Column(db.Text)
    qr_url = db.Column(db.String(150))
    apk_url = db.Column(db.String(150))
    add_time = db.Column(db.DateTime(), default=datetime.now())

    def to_json(self):
        json_game_server = {
            'id': self.id,
            'game_id': self.game_id,
            'package_name': self.package_name,
            'data_file_names': self.data_file_names,
            'server_name': self.server_name,
            'server_des': self.server_des,
            'add_time': datetime_timestamp(self.add_time),
        }
        return json_game_server


class UserNotice(db.Model):
    __tablename__ = 'tb_user_notice'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    task_name = db.Column(db.String(50))  # De-normalization Design
    task_id = db.Column(db.Integer, default=0)
    title = db.Column(db.String(150))
    server_name = db.Column(db.String(150))
    level_need = db.Column(db.String(150))
    profession_need = db.Column(db.String(150))
    other_need = db.Column(db.String(250))
    game_id = db.Column(db.Integer, default=0, index=True)
    publish_time = db.Column(db.DateTime(), default=datetime.now())
    start_time = db.Column(db.Integer, default=0)
    end_time = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Record %r,%r,%r>' % self.id % self.user_id % self.game_id

    @staticmethod
    def from_json(json_user_notice):
        user_notice = UserNotice()

        user_notice.user_id = json_user_notice.get('user_id')
        if not user_notice.user_id:
            raise ValidationError('does not have a user_id')

        user_notice.game_id = json_user_notice.get('game_id')
        if not user_notice.game_id:
            raise ValidationError('does not have a game_id')
        game = Game.query.get(user_notice.game_id)
        if game is None:
            raise ValidationError('the game does not exist')

        user_notice.task_id = json_user_notice.get('task_id')
        if not user_notice.task_id:
            raise ValidationError('does not have a task_id')
        game_task = GameTask.query.get(user_notice.task_id)
        if game_task is None or game_task.game_id != int(user_notice.game_id):
            raise ValidationError('wrong task_id')
        user_notice.task_name = game_task.task_name

        user_notice.title = json_user_notice.get('title')
        if not user_notice.title:
            raise ValidationError('does not have title')

        user_notice.server_name = json_user_notice.get('server_name')
        if not user_notice.server_name:
            raise ValidationError('does not have server name')

        user_notice.level_need = json_user_notice.get('level_need')
        user_notice.profession_need = json_user_notice.get('profession_need')
        user_notice.other_need = json_user_notice.get('other_need')
        user_notice.start_time = json_user_notice.get('start_time')
        user_notice.end_time = json_user_notice.get('end_time')

        return user_notice

    def to_json(self):
        json_user_notice = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'level_need': self.level_need,
            'profession_need': self.profession_need,
            'server_name': self.server_name,
            'game_id': self.game_id,
            'other_need': self.other_need,
            'publish_time': datetime_timestamp(self.publish_time),
            'task_id': self.task_id,
            'task_name': self.task_name,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
        return json_user_notice


class UserNoticeRel(db.Model):
    __tablename__ = 'tb_user_notice_rel'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0)
    notice_id = db.Column(db.Integer, default=0)
    add_time = db.Column(db.DateTime(), default=datetime.now())

    def __repr__(self):
        return '<Rel %r,%r,%r>' % self.id % self.user_id % self.notice_id


class DevicePushMessage(db.Model):
    __tablename__ = 'tb_device_push_message'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(120))
    audience = db.Column(db.Text)
    message_type = db.Column(db.Integer, default=0)
    content = db.Column(db.String(250))
    ext1 = db.Column(db.Integer, default=0)
    ext2 = db.Column(db.String(250))
    ext3 = db.Column(db.Text)
    add_time = db.Column(db.DateTime, default=datetime.now())
    modify_time = db.Column(db.DateTime, default=datetime.now())
    state = db.Column(db.Integer, default=0)

    def __repr__(self):
        return 'Message %r,%r,%r' % self.id % self.message_type % self.content


class GameGift(db.Model):
    __tablename__ = 'tb_game_gift'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    code = db.Column(db.String(120))
    type = db.Column(db.Integer, default=0)
    ext1 = db.Column(db.Integer, default=0)
    ext2 = db.Column(db.String(250))
    ext3 = db.Column(db.Text)
    add_time = db.Column(db.DateTime, default=datetime.now())
    modify_time = db.Column(db.DateTime, default=datetime.now())
    state = db.Column(db.Integer, default=0)

    def __repr__(self):
        return 'Message %r,%r,%r' % self.id % self.game_id % self.code


class GiftRecord(db.Model):
    __tablename__ = 'tb_gift_record'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    gift_id = db.Column(db.Integer)
    mobile = db.Column(db.String(16))
    type = db.Column(db.Integer, default=0)
    ext1 = db.Column(db.Integer, default=0)
    ext2 = db.Column(db.String(250))
    ext3 = db.Column(db.Text)
    add_time = db.Column(db.DateTime, default=datetime.now())
    modify_time = db.Column(db.DateTime, default=datetime.now())
    state = db.Column(db.Integer, default=1)

    def __repr__(self):
        return 'Message %r,%r,%r' % self.id % self.game_id % self.gift_id


class Business(db.Model):
    __tablename__ = 'tb_business'
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(50))
    business_desc = db.Column(db.Text)
    allot_limit_type = db.Column(db.Integer, default=0)
    allot_limit_num = db.Column(db.Integer, default=0)
    add_time = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return 'Business %r, %r, %r' % self.id % self.business_name % self.business_desc % \
               self.allot_limit_type % self.allot_limit_num

    def to_json(self):
        json_business = {
            'id': self.id,
            'business_name': self.business_name,
            'business_desc': self.business_desc,
            'allot_limit_type': self.allot_limit_type,
            'allot_limit_num': self.allot_limit_num,
            'add_time': self.add_time,
        }
        return json_business


class DeviceQueue(db.Model):
    __tablename__ = 'tb_device_queue'
    device_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, default=0)
    server_id = db.Column(db.Integer, default=0)
    business_id = db.Column(db.Integer, default=0)
    add_time = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return 'DeviceQueue %r, %r, %r' % self.device_id % self.game_id % self.server_id % self.business_id


class CategoryApk(db.Model):
    __tablename__ = 'tb_category_apk'
    apk_id = db.Column(db.Integer, db.ForeignKey('tb_apk.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('tb_category.id'), primary_key=True)
    add_time = db.Column(db.DateTime, default=datetime.now())


class Category(db.Model):
    __tablename__ = 'tb_category'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50))
    add_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)

    apk = db.relationship('CategoryApk', foreign_keys=[CategoryApk.category_id],
                          backref=db.backref('category', lazy='joined'),
                          lazy='dynamic',
                          cascade='all, delete-orphan')

    def __repr__(self):
        return 'Category %r, %r, %r' % self.id % self.category_name % self.add_time

    def to_json(self):
        category_apk = {
            'id': self.id,
            'category_name': self.category_name,
            'add_time': datetime_timestamp(self.add_time),
            'state': self.state,
        }
        return category_apk


class Apk(db.Model):
    __tablename__ = 'tb_apk'
    id = db.Column(db.Integer, primary_key=True)
    apk_name = db.Column(db.String(50), index=True)
    icon_url = db.Column(db.String(150))
    banner_url = db.Column(db.String(150))
    music_url = db.Column(db.String(150))
    package_name = db.Column(db.String(250))
    data_file_names = db.Column(db.Text)
    apk_desc = db.Column(db.Text)
    qr_url = db.Column(db.String(150))
    apk_url = db.Column(db.String(150))
    banner_side = db.Column(db.String(150))
    square_img = db.Column(db.String(150))
    add_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)  # 0：删除； 1： 正常
    allow_allot = db.Column(db.Integer, default=0)  # 0：禁止分配； 1：允许分配
    rec = db.Column(db.Integer, default=0)  # 推荐值 大于0表示推荐游戏,按照 rec 降序排列

    user = db.relationship('UserApk', foreign_keys=[UserApk.apk_id],
                           backref=db.backref('apk', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    category = db.relationship('CategoryApk', foreign_keys=[CategoryApk.apk_id],
                           backref=db.backref('apk', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')

    agent_records = db.relationship('AgentRecord2', backref='apk')

    @staticmethod
    def from_json(json_apk):
        apk = Apk()
        apk.game_name = json_apk.get('apk_name')
        if apk.apk_name is None or apk.apk_name == '':
            raise ValidationError('apk does not have a name')
        return apk

    def to_json(self):
        json_apk = {
            'id': self.id,
            'apk_name': self.apk_name,
            'package_name': self.package_name,
            'data_file_names': self.data_file_names,
            'icon_url': filter_upload_url(self.icon_url),
            'banner_url': filter_upload_url(self.banner_url),
            'music_url': filter_upload_url(self.music_url),
            'add_time': datetime_timestamp(self.add_time),
            'apk_desc': self.apk_desc,
            'qr_url': self.qr_url,
            'apk_url': self.apk_url,
            'banner_side': self.banner_side,
            'square_img': self.square_img,
            'state': self.state,
            'allow_allot': self.allow_allot,
        }
        return json_apk
