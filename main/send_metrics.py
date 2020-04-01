#!env/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "."))
sys.path.append(BASE_DIR)

from utils.get_configure import env_file_conf
from utils.eureka_metrics import get_client, get_applications, applications_info, cache_services, default_infos
from utils.console_logger import Logger
from utils.apollo_handler import apo_client, apollo_envs_conf


env_type = env_file_conf('ENV_TYPE', default='DEV')
log = Logger()
logger = log.get_logger()

ek_client = None
eureka_ip = '127.0.0.1'


def eureka_client():

    external = env_file_conf('EXTERNAL', conf_type='bool')
    eureka_conf = 'eureka_ip' if not external else 'eureka_external_ip'
    global eureka_ip
    try:
        eureka_ip = apollo_envs_conf(apollo_client, eureka_conf)
    except Exception as e:
        logger.error("Getting eureka addr configures from apollo or temp file failed! {}".format(e.__repr__()))
        exit(1)
    global ek_client
    if not ek_client:
        ek_client = get_client(eureka_ip)
    if not ek_client: return None

    return ek_client


def app_status(apollo_client, eureka_client):
    """
            从eureka获取服务health check数据
            :return: list
    """

    all_apps = get_applications(eureka_ip, eureka_client)
    app_infos = applications_info(all_apps)
    unavailable_services = cache_services(apollo_client, app_infos)
    unavailable_services_info = list(
        map(
            lambda service_str: {
                "product": service_str.split('_')[0],
                "service": service_str.split('_')[1],
                "env_type": service_str.split('_')[2],
                # "status": "DOWN"
            },
            unavailable_services)
    )
    logger.info("Services unavailable info {}".format(unavailable_services_info))
    app_default_infos = default_infos(unavailable_services_info)
    logger.debug("Applications health metric: {}".format(app_infos))

    return {**app_infos, **app_default_infos}
    # return app_infos.extend(app_default_infos)


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
    def __init__(self, apollo_client, eureka_client):
        self.apollo_client = apollo_client
        self.eureka_client = eureka_client

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

        app_list = app_status(self.apollo_client, self.eureka_client)

        for app, app_infos in app_list.items():
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
    apollo_client = apo_client()
    ek_client = eureka_client()
    apollo_client.start()
    REGISTRY.register(AppCollector(apollo_client, ek_client))
    apollo_client.stop()
    ek_client.stop()

    while True:
        time.sleep(60)


