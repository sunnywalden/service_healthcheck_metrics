#!env/bin/python
#-*- coding:utf-8 -*-
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from prometheus_client.core import GaugeMetricFamily
from prometheus_client import Gauge
import urllib2
from base64 import encodestring
import json
import time
from tools.log_generate import Log


class CommonGaugeMetric(object):
    def __init__(self, metric_name, metric_value, metric_labels, timestamp, metric_des=''):
        self.metric_name = metric_name
        self.metric_des = metric_des
        self.metric_value = metric_value
        self.metric_labels = metric_labels
        self.timestamp = timestamp
        lg = Log()
        self.logger = lg.logger_generate('metrics_exporter')
        self.lbs, self.lbs_values = [], []
        for lb in metric_labels:
            self.lbs.append(lb)
            self.lbs_values.append(str(metric_labels[lb]))

    def metric_handler(self):
        for i in range(len(self.lbs_values)):

            if not isinstance(self.lbs_values[i], float) and not isinstance(self.lbs_values[i], int):
                self.lbs_values[i] = self.lbs_values[i].encode('utf-8')
            self.lbs[i] = self.lbs[i].encode('utf-8')
        metric_gauge = Gauge(self.metric_name, self.lbs, self.lbs_values)
        metric_gauge.set(self.metric_value)
        return metric_gauge

        # metric_gauge = GaugeMetricFamily(self.metric_name,
        #                               'The latest metrics of service based on spring boot',
        #                               labels=self.lbs)

        # try:
        #     metric_gauge.add_metric(self.lbs_values, self.metric_value, timestamp=self.timestamp)
        #     self.logger.info('Metric send to prometheus %s' % metric_gauge)
        #     return metric_gauge
        #
        # except Exception, e:
        #     self.logger.error('Error counted while metric collection!')
        #     self.logger.error(e)

    # getting original metric data
    def collect(self):
        # url = self.proto + '://' + self.host + ':' + str(self.port) + self.url
        #
        # if self.auth_info:
        #
        #     req = urllib2.Request(url)
        #     basestr = encodestring('%s:%s'% (self.username, self.password))[:-1]
        #     req.add_header('Authorization', 'Basic %s' % basestr)
        #     res_data = urllib2.urlopen(req)
        # else:
        #     res_data = urllib2.urlopen(url)
        #
        # res = json.loads(res_data.read())
        # self.logger.debug('interface returned %s' % res)
        #
        # lbs = ['app_name', 'environment_type', 'app_status', 'host', 'port', 'url', ]
        # if len(res) == 0: self.logger.error('Getting metrics from app failed %s' % res_data); exit(1)
        #
        # else:
        #     if url.endswith('health'):
        #         app_status = res['status']
        #     elif url.endswith('qos'):
        #         app_status = res['status']['code']
        #     else:
        #         app_status = res['status']
        #
        # self.logger.info('Metric of application %s' % self.app)
        #
        # app_name = self.app.decode('utf-8').encode('utf-8').replace('-', '').lower() + '_' + self.env_type + '_' + self.host.replace('.', '')
        # lbs_value = [self.app, self.env_type, app_status, self.host, str(self.port), url]
        metric_g = self.metric_handler()
        yield metric_g


# if __name__ == "__main__":
#     # custom collector registry
#     pid = '/tmp/metrics_exporter.pid'
#     lg = Log()
#     log_name = 'metrics_exporter'
#     logger = lg.logger_generate(log_name)
#
#     app_list = [{'app': 'approve', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10081, 'url': '/approve-online/health'}, {'app': 'approve', 'env_type': 'online', 'host': '10.1.1.76', 'port': 10081, 'url': '/approve-online/health'}, {'app': 'approve-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080, 'url': '/approve-base/actuator/health'}, {'app': 'approve-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080, 'url': '/approve-base/actuator/health'}, {'app': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.100.15', 'port': 2603, 'url': '/qos'}, {'app': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.102.9', 'port': 2603, 'url': '/qos'}]
#
#     for app in app_list:
#         try:
#             if 'auth_info' not in app.keys():
#                 # if not self.auth_info:
#                 REGISTRY.register(SpringBootMetric(app['app'], app['env_type'], app['host'], app['port'], app['url']))
#             else:
#                 REGISTRY.register(SpringBootMetric(app['app'], app['env_type'], app['host'], app['port'], app['url'],app['auth_info']))
#
#         except Exception, e:
#             logger.error('Error counted while metric collector registry!')
#             logger.error(e)
    # s_daemon = SpringBootDaemon(pid, app_list)
    # s_daemon.stop()
    # s_daemon.start()
    # if os.path.isfile(pid):
    #     logger.info('app springboot_metrics started!')
    # else:
    #     logger.info('app start failed!')

