#!env/bin/python
# -*- coding:utf-8 -*-

import threading

from utils.get_configure import env_file_conf

eureka_client = None
env_type = env_file_conf('ENV_TYPE', default='DEV')


class MetricThread(threading.Thread):
    def __init__(self, func, args):
        super(MetricThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        """
            线程执行
            :return:
        """
        self.result = self.func(*self.args)

    def get_result(self):
        """
                返回线程结果
                :return: list
        """
        try:
            return self.result
        except Exception:
            return None
