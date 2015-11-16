from . import api
import Queue
from flask import current_app as app
from app.models import Device

__author__ = 'barry'

ERR_CODE_SYSTEM = 99
ERR_CODE_WRONG_PARAM = 1
ERR_CODE_SUCCESS = 0

DEVICE_STATE_DEL = 0
DEVICE_STATE_IDLE = 1
DEVICE_STATE_BUSY = 2

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
    def api_wrong_param():
        ret = {
            'err_code': ERR_CODE_WRONG_PARAM,
            'content': 'wrong param',
        }
        return ret


@api.before_app_first_request
def init_queue():
    idle_devices = Device.query.filter_by(state=DEVICE_STATE_IDLE).all()
    q = Queue.Queue(0)
    for device in idle_devices:
        q.put(device.id)
    app.devices = q
    print "start queue size %r" % q.qsize()
