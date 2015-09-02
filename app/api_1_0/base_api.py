__author__ = 'barry'

ERR_CODE_SYSTEM = 99
ERR_CODE_WRONG_PARAM = 1
ERR_CODE_SUCCESS = 0


class BaseApi:
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
