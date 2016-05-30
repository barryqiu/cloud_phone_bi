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


class TimeoutError(Exception): pass


def timeout(seconds, error_message="Timeout Error: the cmd 30s have not finished."):
    def decorated(func):
        result = ""

        def _handle_timeout(signum, frame):
            global result
            result = error_message
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            global result
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                return result
            return result

        return functools.wraps(func)(wrapper)

    return decorated


@timeout(2)
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


@timeout(2)
def upload_to_cdn(path, file_path):
    try:
        up = upyun.UpYun(app.config['CDN_BUCKET'], username=app.config['CDN_USER_NAME'],
                         password=app.config['CDN_PASSWORD'])
        with open(file_path, 'rb') as f:
            up.put(path, f)
        return app.config['CDN_HOST'] + path
    except Exception:
        return ''


@timeout(2)
def test_time_out():
    time.sleep(6)