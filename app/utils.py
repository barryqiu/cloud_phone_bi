import time

__author__ = 'barryqiu'


class TimeUtil:
    def __init__(self):
        pass

    @staticmethod
    def get_time_stamp():
        return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
