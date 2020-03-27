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

eureka_client = None
env_type = env_file_conf('ENV_TYPE', default='DEV')
log = Logger()
logger = log.get_logger()


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
        logger.error("Getting eureka addr configures from apollo or temp file failed! {}".format(e.__repr__()))
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
    logger.debug("Applications health metric: {}".format(app_infos))

    return {**app_infos, **app_default_infos}


def metric_prepare(app, app_infos):
    logger.info(" Application {} info {}".format(app, app_infos))
    metrics = []

    try:
        applications_info = tuple(filter(lambda app_info: app_info['status'] != 'UNKNOW', app_infos))
    except TypeError as te:
        logger.error("Metric {} cannt be resolved!{}".format(app_infos, te.__str__()))
        exit(1)
    else:
        for app_info in applications_info:
            app_statu = 0 if app_info['status'] != "UP" else 1

            metric_info = [
                app_info['product'],
                app_info['service'],
                env_type,
                app_info['hostname'],
                app_info['hostname'],
                app_info['health_check'],
                app_info['service_addr'],
                app_info['home_page'],
                app_statu
            ]

            try:
                metrics.index(metric_info)
            except:
                yield metric_info


class AppCollector(object):
    """
            prometheus custom metric collector
    """

    def __init__(self, thread_num=10):
        self.app_list = app_status()
        self.thread_num = thread_num

    def collect(self):
        """
                metric generate
                生成metric
        """

        g = GaugeMetricFamily(
            "service_health_status",
            "Application Health Status",
            labels=["product", "service", "env_type", "hostname", "instance", "health_check", "service_addr",
                    "homepage"]
        )

        for app, app_infos in self.app_list.items():
            if not app_infos: break
            metrics = metric_prepare(app, app_infos)
            for metric in metrics:
                g.add_metric(metric[:-1], metric[-1])
                logger.info(metric)

        yield g


if __name__ == "__main__":
    """
            通过http暴露metrics
    """
    start_http_server(8080)
    try:
        REGISTRY.register(AppCollector())
    except AttributeError as e:
        logger.error("Connecting to apollo server failed!{}".format(e.__str__()))
        exit(1)

    while True:
        time.sleep(60)
