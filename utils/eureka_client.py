#!/usr/bin/env python
# coding=utf-8
# author: sunnywalden@gmail.com

import os
import sys
from py_eureka_client import eureka_client

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from utils.get_configure import apollo_envs_conf


def get_client(eureka_hosts="127.0.0.1"):
    try:
        eureka_client.init_discovery_client(eureka_hosts)
    except AttributeError as et:
        print("Eureka connetion failed! %e".format(et.__str__()))
        return None
    else:
        return eureka_client


def register_ops(eureka_server=None, instance_ip='127.0.0.1', instance_port='8000', app_name=None):
    # The flowing code will register your server to eureka server and also start to send heartbeat every 30 seconds
    eureka_client.init_registry_client(
        eureka_server=eureka_server,
        app_name=app_name,
        instance_port=instance_port,
        instance_ip=instance_ip)


def unregister_ops():
    eureka_client.stop()


def get_applications(eureka_hosts="127.0.0.1", eureka_client=None):
    apps = eureka_client.get_applications(eureka_hosts)

    return apps.applications


def applications_info(app_objs):
    apps_info = {}
    for app_obj in app_objs:
        apps_info[app_obj.name] = instance_info(app_obj.instances)

    return apps_info


def instance_info(instances):
    ins_info = []
    for instance in instances:
        product = "vms" if instance.appGroupName == "TEZIGN-INTELLIGENCE" else "sop"
        ins_info.append(
            {
                "product": product,
                "service": instance.vipAddress,
                "app_group": instance.appGroupName,
                "status": instance.status,
                "health_check": instance.healthCheckUrl,
                "home_page": instance.homePageUrl,
                "status_page": instance.statusPageUrl,
                "service_addr": instance.vipAddress,
                "data_center": instance.dataCenterInfo.name.strip().strip('\n'),
                "hostname": instance.hostName,

            }
        )

    return ins_info


if __name__ == '__main__':
    eureka_ip = '127.0.0.1'
    try:
        eureka_ip = apollo_envs_conf("eureka_ip")
    except Exception as e:
        print("Connecting apollo failed!")
        exit(1)
    server_port = 8000
    server_host = "app-status.tezign.com"
    application_name = "SERVICE-MONITOR"
    regions = ['default']
    # # while True:
    # register_ops()
    all_apps = get_applications(eureka_ip)
    app_infos = applications_info(all_apps)
    print(app_infos)

