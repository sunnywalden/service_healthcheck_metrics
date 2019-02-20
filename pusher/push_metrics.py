#!env/bin/python
#-*- coding:utf-8 -*-
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from prometheus_client import push_to_gateway
from tools.log_generate import Log


class MetricsPush(object):
    def __init__(self):
        lg = Log()
        self.logger = lg.logger_generate('metrics_upload')

    def metric_pusher(self, registry, auth_hander=None):
        try:
            if auth_hander==None: push_to_gateway('10.1.16.32:9091', job='app_health', registry=registry)
            else: push_to_gateway('10.1.16.32:9091', job='app_health', registry=registry, handler=auth_hander)
            # g = Gauge
            self.logger.info('Metric upload successful')
        except Exception, e:
            self.logger.info('Metric upload failed!')
            # self.logger.error(traceback.format_exc())
            self.logger.error(e)
