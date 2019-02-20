#!env/bin/python
#-*- coding:utf-8 -*-
import os
import sys
import time

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from prometheus_client.exposition import basic_auth_handler
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server
import urllib2
import json
from tools.daemon import Daemon

from tools.log_generate import Log


class SpringMetricCollector(object):
    def __init__(self, app, env_type, host, port, url, proto='http', auth_info=[]):
        self.app = app
        self.env_type = env_type
        self.host = host
        self.port = port
        self.url = url
        self.proto = proto
        self.auth_info = auth_info

    lg = Log()
    logger = lg.logger_generate('metrics_upload_test')

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
            logger.info('Metric send to prometheus %s' % app_gauge)
            return app_gauge

        except Exception, e:
            logger.error('Error counted while metric collection!')
            logger.error(e)

    # getting original metric data
    def collect(self):
        # lg = Log()
        # logger = lg.logger_generate('metrics_upload_test')
        #url = 'http://sit-admin.qude369.com/kpt-admin/api/applications'
        if self.auth_info:
            username = self.auth_info[0]
            password = self.auth_info[1]
        url = self.proto + '://' + self.host + ':' + str(self.port) + self.url

        res_data = urllib2.urlopen(url)
        res = json.loads(res_data.read())
        logger.debug('interface returned %s' % res)
        # lbs = ['serviceName', 'serviceStatus', 'managementUrl', 'managementPort', 'healthUrl', 'serviceUrl',
        #        'userName', 'managementContextPath', 'infoGitBranch', 'infoGitTags', 'infoBuildVersion']
        lbs = ['app_name', 'environment_type', 'app_status', 'host', 'port', 'url', ]
        # lbs = ['serviceName', 'serviceStatus']
        if len(res) == 0: logger.error('Getting metrics from app failed %s' % res_data); exit(1)

        else:
            if url.endswith('health'):
                app_status = res['status']
            elif url.endswith('qos'):
                app_status = res['status']['code']
            else:
                app_status = res['status']

        logger.info('Metric of application %s' % self.app)

        app_name = self.app.decode('utf-8').encode('utf-8').replace('-', '').lower() + '_' + self.env_type + '_' + self.host.replace('.', '')
                            # lbs_value = [a_name + '_' + sv_name, status, management_url, management_port, health_url,
                            #              service_url, user_name, management_context_path, info_git_branch,
                            #              info_git_tags,
                            #              info_build_version]
        lbs_value = [self.app, self.env_type, app_status, self.host, str(self.port), url]
                            # lbs_value = [a_name + sv_name, status]
                            # app_g = self.metric_handler(a_name + sv_name, lbs, lbs_value)
        app_g = self.metric_handler(app_name, lbs, lbs_value)
        yield app_g


class MetricPrepare(object):

    def __init__(self):
        lg = Log()
        self.logger = lg.logger_generate('metrics_upload_test')
        self.url = 'http://192.168.100.41:10081/rs/health'
        self.username = 'admin'
        self.password = 'admin'

    # user authentication method
    def auth_handler(self, url, method, timeout, headers, data):
        return basic_auth_handler(url, method, timeout, headers, data, self.username, self.password)


class SpringBootDaemon(Daemon):
    # def __init__(self):
    lg = Log()
    logger = lg.logger_generate('metrics_upload_test')

    def run(self):

        while True:
            try:
                REGISTRY.register(SpringMetricCollector('approve', 'online', '10.1.1.77', 10081, '/approve-online/health'))
                REGISTRY.register(SpringMetricCollector('approve', 'online', '10.1.1.76', 10081, '/approve-online/health'))
                REGISTRY.register(SpringMetricCollector('approve-base', 'online', '10.1.1.76', 10080, '/approve-base/actuator/health'))
                REGISTRY.register(SpringMetricCollector('approve-base', 'online', '10.1.1.77', 10080,'/approve-base/actuator/health'))
                REGISTRY.register(SpringMetricCollector('zhanzhao-web', 'online', '192.168.100.15', 2603, '/qos'))
                REGISTRY.register(SpringMetricCollector('zhanzhao-web', 'online', '192.168.102.9', 2603, '/qos'))
            except Exception, e:
                logger.error('Error counted while metric collector registry!')
                logger.error(e)
        # push metrics to push gateway
            else:
                start_http_server(9812)
                # mpush = MetricsPush()

                # mp = MetricPrepare()

                # mpush.metric_pusher(REGISTRY)

                # mpush.metric_pusher(REGISTRY, mp.auth_handler)
                time.sleep(5)


if __name__ == "__main__":
    # custom collector registry
    pid = '/tmp/springboot_metrics.pid'
    lg = Log()
    logger = lg.logger_generate('metrics_upload_test')

    s_daemon = SpringBootDaemon(pid)
    s_daemon.stop()
    s_daemon.start()
    #daemon = Daemonize(app='springboot_metrics', pid=pid, action=sdaemon.run_Daemon())

    #daemon.start()
    if os.path.isfile(pid):
        logger.info('app springboot_metrics started!')
    else:
        logger.info('app start failed!')

        #     mpush = MetricsPush()
        #
        #     mp = MetricPrepare()
        #
        #     mpush.metric_pusher(REGISTRY, mp.auth_handler)
            # time.sleep(1)
