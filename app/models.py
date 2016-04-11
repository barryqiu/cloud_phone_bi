import time
from datetime import datetime
import urllib2
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app.exceptions import ValidationError
from . import db, login_manager, redis_store
from app.utils import filter_upload_url


def datetime_timestamp(dt):
    # s = str(dt)
    try:
        v = int(time.mktime(time.strptime(str(dt), '%Y-%m-%d %H:%M:%S')))
        return str(v)
    except:
        return 0


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


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


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
            'model_number': self.model_number,
            'collect_time': datetime_timestamp(self.collect_time),
            'android_id': self.android_id,
            'mac': self.mac,
            'state': self.state,
            'level': self.level
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.mobile_num

    @staticmethod
    def redis_incr_ext_info(user_id, key, num):
        redis_key = ('YUNPHONE:USER_EXT:%s' % user_id).upper()
        return redis_store.hincrby(redis_key, key, num)

    @staticmethod
    def redis_get_ext_info(user_id, key):
        redis_key = ('YUNPHONE:USER_EXT:%s' % user_id).upper()
        return redis_store.hget(redis_key, key)


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
    def test_conn(device):
        try:
            url = 'http://yunphoneclient.shinegame.cn/' + device.device_name

            # proxy = urllib2.ProxyHandler({'http': 'proxy.tencent.com:8080'})
            # opener = urllib2.build_opener(proxy)
            # urllib2.install_opener(opener)

            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            the_page = response.read()

            return not 'Phone is not in the database. Is it online?' in the_page
        except Exception:
            return False

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
            'state': self.state
        }
        return json_device

    def __repr__(self):
        return '<Device %r>' % self.device_name

    @staticmethod
    def push_redis_set(device_id):
        redis_key = 'YUNPHONE:DEVICES'.upper()
        return redis_store.sadd(redis_key, device_id)

    @staticmethod
    def pop_redis_set():
        redis_key = 'YUNPHONE:DEVICES'.upper()
        return redis_store.spop(redis_key)

    @staticmethod
    def available_num():
        redis_key = 'YUNPHONE:DEVICES'.upper()
        return redis_store.scard(redis_key)

    @staticmethod
    def set_device_info(device_id, info_type, content):
        redis_key = ('YUNPHONE:DEVICE:INFO:%s' % device_id).upper()
        return redis_store.hset(redis_key, ("%s" % info_type), content)


class Game(db.Model):
    __tablename__ = 'tb_game'
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(50), unique=True, index=True)
    icon_url = db.Column(db.String(150))
    banner_url = db.Column(db.String(150))
    package_name = db.Column(db.String(250))
    data_file_names = db.Column(db.Text)
    add_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)

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
            'add_time': datetime_timestamp(self.add_time),
            'state': self.state,
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
    state = db.Column(db.Integer, default=1)

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


class GameServer(db.Model):
    __tablename__ = 'tb_game_server'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, default=0)
    icon_url = db.Column(db.String(150))
    package_name = db.Column(db.String(250))
    data_file_names = db.Column(db.Text)
    server_name = db.Column(db.String(50))
    server_des = db.Column(db.Text)
    add_time = db.Column(db.DateTime(), default=datetime.now())

    def to_json(self):
        json_game_server = {
            'id': self.id,
            'game_id': self.game_id,
            'icon_url': filter_upload_url(self.icon_url),
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
