from . import api
import Queue
from flask import current_app as app
from app.models import Device
from ..constant import *
from ..error_code import *

__author__ = 'barry'


class BaseApi:
    def __init__(self):
        pass

    @staticmethod
    def api_success(content):
        ret = {
            'err_code': ERR_CODE_SUCCESS,
            'content': content,
        }
        return ret

    @staticmethod
    def api_system_error(msg):
        if msg is None or msg == '':
            msg = "system error"
        ret = {
            'err_code': ERR_CODE_SYSTEM,
            'content': msg,
        }
        return ret

    @staticmethod
    def api_except_error(e):
        msg = "system error"
        err_code = ERR_CODE_SYSTEM
        if e and hasattr(e, 'message') and e.message:
            msg = e.message
        if e and hasattr(e, 'code') and e.code:
            err_code = e.code
        ret = {
            'err_code': err_code,
            'content': msg,
        }
        return ret

    @staticmethod
    def api_wrong_param():
        ret = {
            'err_code': ERR_CODE_WRONG_PARAM,
            'content': 'wrong param',
        }
        return ret

    @staticmethod
    def api_wrong_verify_code():
        ret = {
            'err_code': ERR_CODE_WRONG_VERIFY_CODE,
            'content': 'wrong verify code',
        }
        return ret

    @staticmethod
    def api_no_device():
        ret = {
            'err_code': ERR_CODE_NO_DEVICE,
            'content': 'no free device',
        }
        return ret

    @staticmethod
    def api_jpush_error():
        ret = {
            'err_code': ERR_CODE_JPUSH_ERROR,
            'content': 'jpush error',
        }
        return ret

    @staticmethod
    def api_exceed_allot_num_error():
        ret = {
            'err_code': ERR_CODE_EXCEED_ALLOT_NUM_ERROR,
            'content': 'exceed the max allot num error',
        }
        return ret

    @staticmethod
    def api_already_reg_error():
        ret = {
            'err_code': ERR_CODE_ALREADY_REG,
            'content': 'the user already exists',
        }
        return ret

    @staticmethod
    def api_push_msg_error():
        ret = {
            'err_code': ERR_CODE_PUSH_MSG_ERR,
            'content': 'push msg to device error'
        }
        return ret

    @staticmethod
    def api_common_error(code, msg):
        ret = {
            'err_code': code,
            'content': msg
        }
        return ret


@api.before_app_first_request
def init_queue():
    idle_devices = Device.query.filter_by(state=DEVICE_STATE_IDLE).all()
    q = Queue.Queue(0)
    for device in idle_devices:
        q.put(device.id)
    app.devices = q
