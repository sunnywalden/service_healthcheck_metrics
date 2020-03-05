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
from utils.eureka_client import get_client, get_applications, applications_info

eureka_client = None
env_type = env_file_conf('ENV_TYPE', default='DEV')


def app_status():
    eureka_ip = '127.0.0.1'
    try:
        eureka_ip = apollo_envs_conf("eureka_ip")
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
    print("Applications health metric: %s".format(app_infos))

    return app_infos


class AppCollector(object):
    def __init__(self):
        self.app_list = app_status()

    def collect(self):
        g = GaugeMetricFamily(
            "service_health_status",
            "Application Health Status",
            labels=["product", "service", "env_type", "hostname", "health_check",  "service_addr", "homepage"]
        )
        for app, app_infos in self.app_list.items():
            print(" Application %s info %s" % (app, app_infos))
            for app_info in app_infos:
                app_statu = 0 if app_info['status'] != "UP" else 1
                try:
                    g.add_metric(
                        [
                            app_info['product'],
                            app_info['service'],
                            env_type,
                            app_info['hostname'],
                            app_info['health_check'],
                            app_info['service_addr'],
                            app_info['home_page']
                        ], app_statu
                    )
                except Exception as e:
                    print('Error while prepare metric %s'.format(e.__str__()))
                else:
                    print('push metric finished one time!')

        yield g


if __name__ == "__main__":
    start_http_server(8000)
    REGISTRY.register(AppCollector())
    while True:
        time.sleep(60)
