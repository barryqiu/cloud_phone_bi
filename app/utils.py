#!/usr/bin/python
# -*- coding: utf-8 -*-
import functools
import json
import random
import time
import urllib2

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


def push_message_to_device(device_name, content, msg_type):
    msg = {
        'msg_type': msg_type,
        'content': content
    }

    url = "http://yunphoneclient.shinegame.cn/%s/injkeyvn" % device_name

    try:
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')

        retry_times = 0
        response = None
        str_content = json.dumps(msg)
        str_content = str_content.replace("\"%s\"" % msg_type, "\'\"%s\"\'" % msg_type)
        str_content = str_content.replace("\"%s\"" % content, "\'\"%s\"\'" % content)
        while True:
            response = urllib2.urlopen(req, str_content, timeout=2)
            the_page = response.read()
            content = str.strip(the_page)
            app.logger.error("%s:%s:%s:%s" % (device_name, str_content, response.code, content[0:10]))
            retry_times += 1
            if retry_times > 3:
                break
        if response.code == 200:
            return True
    except Exception as e:
        app.logger.exception('error')
    return False


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


def datetime_timestamp(dt):
    # s = str(dt)
    try:
        v = int(time.mktime(time.strptime(str(dt), '%Y-%m-%d %H:%M:%S')))
        return str(v)
    except:
        return 0
