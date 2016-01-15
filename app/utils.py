import random
import time
import jpush
from flask import current_app as app


__author__ = 'barryqiu'


class TimeUtil:
    def __init__(self):
        pass

    @staticmethod
    def get_time_stamp():
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


def generate_verification_code():
    code_list = []
    for i in range(10):
        code_list.append(str(i))
    my_slice = random.sample(code_list, 6)
    verification_code = ''.join(my_slice)
    return verification_code


def push_message_to_alias(message, msg_type, alias, platform='android'):
    _jpush = jpush.JPush(app.config['JPUSH_APP_KEY'], app.config['JPUSH_MASTER_SECRET'])
    push = _jpush.create_push()
    push.message = jpush.message(message, content_type=msg_type)
    push.audience = jpush.audience(jpush.alias(alias))
    # push.audience = jpush.audience(jpush.all_)
    push.platform = jpush.platform(platform)
    ret = push.send()
    return ret.payload['sendno'].encode('utf-8')




