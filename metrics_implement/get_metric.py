#!env/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import time

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from prometheus_client.core import REGISTRY, CollectorRegistry
from prometheus_client import start_http_server
from metrics_implement.springboot_metric_exporter import SpringBootMetric
from tools.daemon import Daemon
from tools.log_generate import Log
from tools.json_file_handler import data_read
from pusher.push_metrics import MetricsPush


class SpringBootDaemon(Daemon):

    lg = Log()
    logger = lg.logger_generate('get_metric')

    def run(self):
        # lg = Log()
        # logger = lg.logger_generate('metrics_upload_test')
        while True:
            # for app in self.app_list:
                self.log('dealing with app %s now' % self.app_list)
                metric_inter = MetricInterface(self.app_list)

                metric_inter.get_metrics()

                time.sleep(5)


class MetricInterface(object):

    def __init__(self, app_lists):
        self.app_list = app_lists
        mi_lg = Log()
        self.logger = mi_lg.logger_generate('get_metric')

    def get_metrics(self):
        self.logger.info('export metric of app %s now' % self.app_list)
        if not app_list: self.logger.error('Application info empty!'); exit(1)
        for app in self.app_list:
            # registry = CollectorRegistry()
            try:
                if 'auth_info' not in app.keys():
                    # if not self.auth_info:
                    # registry.register(SpringBootMetric(app['app'], app['env_type'], app['host'], app['port'], app['url']))
                    REGISTRY.register(SpringBootMetric(app['app'], app['env_type'], app['host'], app['port'], app['url']))
                else:
                    REGISTRY.register(SpringBootMetric(app['app'], app['env_type'], app['host'], app['port'], app['url'], app['auth_info']))
                    # registry.register(SpringBootMetric(app['app'], app['env_type'], app['host'], app['port'], app['url'], app['auth_info']))

            except Exception, e:
                # self.logger.error('Error counted while metric collector registry!')
                self.logger.info(e)
            # push metrics to push gateway
            else:
                m_push = MetricsPush()
                m_push.metric_pusher(REGISTRY)
                # start_http_server(9813)
                self.logger.info('push metric finished one time!')


if __name__ == "__main__":
    # custom collector registry
    pid = '/tmp/get_metric.pid'
    lg = Log()
    log_name = 'get_metric'
    logger = lg.logger_generate(log_name)

    apps = data_read()
    app_list = apps.values()
    # app_list = [
    #     {'app': 'approve', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10081, 'url': '/approve-online/health'},
    #     {'app': 'approve', 'env_type': 'online', 'host': '10.1.1.76', 'port': 10081, 'url': '/approve-online/health'},
    #     {'app': 'approve-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080,
    #      'url': '/approve-base/actuator/health'},
    #     {'app': 'approve-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080,
    #      'url': '/approve-base/actuator/health'},
    #     {'app': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.100.15', 'port': 2603, 'url': '/qos'},
    #     {'app': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.102.9', 'port': 2603, 'url': '/qos'}]

    s_daemon = SpringBootDaemon(pid, app_list)
    s_daemon.stop()
    s_daemon.start()
    if os.path.isfile(pid):
        print('app springboot_metrics started!')
        logger.info('app springboot_metrics started!')
    else:
        logger.info('app start failed!')
        print('app start failed!')
