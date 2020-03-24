#!env/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "."))
sys.path.append(BASE_DIR)

from utils.get_configure import apollo_envs_conf, env_file_conf
from utils.eureka_metrics import get_client, get_applications, applications_info, cache_services, default_infos
from utils.console_logger import Logger
from main.metric_threading import MetricThread

eureka_client = None
env_type = env_file_conf('ENV_TYPE', default='DEV')
log = Logger()
logger = log.logger()


def app_status():
    """
            从eureka获取服务health check数据
            :return: list
    """
    eureka_ip = '127.0.0.1'
    external = env_file_conf('EXTERNAL', conf_type='bool')
    eureka_conf = 'eureka_ip' if not external else 'eureka_external_ip'
    try:
        eureka_ip = apollo_envs_conf(eureka_conf)
    except Exception as e:
        print("Connecting apollo failed! %s".format(e.__repr__()))
        exit(1)
    global eureka_client
    if not eureka_client:
        eureka_client = get_client(eureka_ip)
        if not eureka_client: return None
    all_apps = get_applications(eureka_ip, eureka_client)
    eureka_client.stop()
    app_infos = applications_info(all_apps)
    unavailable_services = cache_services(app_infos)
    unavailable_services_info = list(
        map(
            lambda service_str: {
                "product": service_str.split('_')[0],
                "service": service_str.split('_')[1],
                "env_type": service_str.split('_')[2]
            },
            unavailable_services)
    )
    app_default_infos = default_infos(unavailable_services_info)
    print("Applications health metric: %s".format(app_infos))

    return {**app_infos, **app_default_infos}


def metric_prepare(app, app_infos):
    print(" Application %s info %s" % (app, app_infos))
    metrics = []
    for app_info in app_infos:
        app_statu = 0 if app_info['status'] != "UP" else 1

        metric_info = [
            app_info['product'],
            app_info['service'],
            env_type,
            app_info['hostname'],
            app_info['health_check'],
            app_info['service_addr'],
            app_info['home_page'],
            app_statu
        ]

        try:
            metrics.index(metric_info)
        except:

            try:
                metrics.append(
                    metric_info
                )
            except Exception as e:
                print('Error while prepare metric {}'.format(e.__str__()))
                exit(1)
            else:
                print('push metric finished one time!')

    return metrics


class AppCollector(object):
    """
            prometheus custom metric collector
    """

    def __init__(self, thread_num=10):
        self.app_list = app_status()
        self.thread_num = thread_num
        self.g = GaugeMetricFamily(
            "service_health_status",
            "Application Health Status",
            labels=["product", "service", "env_type", "hostname", "health_check", "service_addr", "homepage"]
        )

    def collect(self):
        """
                metric generate
                生成metric
        """

        threads = []
        for app, app_infos in self.app_list.items():
            for i in range(self.thread_num):
                thread = MetricThread(metric_prepare, args=(app, app_infos))
                threads.append(thread)

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        metric_list = []
        for thread in threads:
            thread_res = thread.get_result()
            if thread_res:
                metric_list.append(thread_res)

        for metrics in metric_list:
            for metric in metrics:
                self.g.add_metric(metric[:-1], metric[-1])
                print(metric[:-1], metric[-1])

        yield self.g


if __name__ == "__main__":
    """
            通过http暴露metrics
    """
    start_http_server(8080)
    try:
            REGISTRY.register(AppCollector())
    except AttributeError as e:
            print("Connecting to apollo server failed!")
            exit(1)
    while True:
            time.sleep(60)


