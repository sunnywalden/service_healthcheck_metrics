#!env/bin/python
#-*- coding:utf-8 -*-
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from prometheus_client.core import GaugeMetricFamily
import urllib2
from base64 import encodestring
import json
from tools.log_generate import Log


class SpringBootMetric(object):
    def __init__(self, app, env_type, host, port, url, auth_info=[], proto='http'):
        self.app = app
        self.env_type = env_type
        self.host = host
        self.port = port
        self.url = url
        self.proto = proto
        self.auth_info = auth_info
        if self.auth_info:
            self.username = self.auth_info[0]
            self.password = self.auth_info[1]
        lg = Log()
        self.logger = lg.logger_generate('metrics_exporter')

    def metric_handler(self, app_name, lbs, lbs_value):
        for i in range(len(lbs_value)):

            if not isinstance(lbs_value[i], int): lbs_value[i] = lbs_value[i].encode('utf-8')
            lbs[i] = lbs[i].encode('utf-8')
        if lbs_value[2] == 'UP':
            value = 1
        else:
            value = 0
        app_gauge = GaugeMetricFamily(app_name,
                                      'The latest metrics of service based on spring boot',
                                      labels=lbs)
        try:
            app_gauge.add_metric(lbs_value, value)
            self.logger.info('Metric send to prometheus %s' % app_gauge)
            return app_gauge

        except Exception, e:
            self.logger.error('Error counted while metric collection!')
            self.logger.error(e)

    # getting original metric data
    def collect(self):
        url = self.proto + '://' + self.host + ':' + str(self.port) + self.url

        if self.auth_info:

            req = urllib2.Request(url)
            basestr = encodestring('%s:%s'% (self.username, self.password))[:-1]
            req.add_header('Authorization', 'Basic %s' % basestr)
            res_data = urllib2.urlopen(req)
        else:
            res_data = urllib2.urlopen(url)

        res = json.loads(res_data.read())
        self.logger.debug('interface returned %s' % res)

        lbs = ['app_name', 'environment_type', 'app_status', 'host', 'port', 'url', ]
        if len(res) == 0: self.logger.error('Getting metrics from app failed %s' % res_data); exit(1)

        else:
            if url.endswith('health'):
                app_status = res['status']
            elif url.endswith('qos'):
                app_status = res['status']['code']
            else:
                app_status = res['status']

        self.logger.info('Metric of application %s' % self.app)

        app_name = self.app.decode('utf-8').encode('utf-8').replace('-', '').lower() + '_' + self.env_type + '_' + self.host.replace('.', '')
        lbs_value = [self.app, self.env_type, app_status, self.host, str(self.port), url]
        app_g = self.metric_handler(app_name, lbs, lbs_value)
        yield app_g


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

