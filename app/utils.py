#!/usr/bin/python
# -*- coding: utf-8 -*-
import functools
import json
import random
import time
import jpush

import signal
from flask import current_app as app
from upyun import upyun
import hashlib

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


def filter_upload_url(url):
    if not url:
        return ''
    if url.startswith('http:'):
        return url
    return app.config['UPLOAD_HOST'] + url


def push_message_to_alias(content, msg_type, alias, platform='android'):
    msg = {
        'msg_type': msg_type,
        'content': content
    }

    _jpush = jpush.JPush(app.config['JPUSH_APP_KEY'], app.config['JPUSH_MASTER_SECRET'])
    push = _jpush.create_push()
    push.message = jpush.message(json.dumps(msg))
    push.audience = jpush.audience(jpush.alias(alias))
    push.platform = jpush.platform(platform)
    ret = push.send()
    return ret.payload['sendno'].encode('utf-8')


def upload_to_cdn(path, file_path):
    try:
        up = upyun.UpYun(app.config['CDN_BUCKET'], username=app.config['CDN_USER_NAME'],
                         password=app.config['CDN_PASSWORD'])
        with open(file_path, 'rb') as f:
            up.put(path, f)
        return app.config['CDN_HOST'] + path
    except Exception:
        return ''


def gen_random_string():
    time_now = "%f" % time.time()
    m5 = hashlib.md5()
    m5.update(time_now)
    return m5.hexdigest()
