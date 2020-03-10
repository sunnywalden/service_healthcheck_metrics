#!/usr/bin/env python
# coding=utf-8
# author: sunnywalden@gmail.com

from py_eureka_client import eureka_client

from utils.get_configure import apollo_envs_conf, env_file_conf, unregister_services_conf
from utils.redis_handler import cache_get, cache_set
from utils.console_logger import Logger

log = Logger()
logger = log.logger_generate()


def get_client(eureka_hosts="127.0.0.1"):
    """
            获取eureka客户端连接
            :param eureka_hosts: eureka地址
            :return:
    """
    try:
        eureka_client.init_discovery_client(eureka_hosts)
    except AttributeError as et:
        logger.error("Eureka connetion failed! %e".format(et.__str__()))
        return None
    else:
        return eureka_client


def register_service(eureka_server=None, instance_ip='127.0.0.1', instance_port='8000', app_name=None):
    """
            注册服务到eureka
            :param eureka_server:
            :param instance_ip: eureka host ip
            :param instance_port: eureka host port
            :param app_name: apollo app_id
            :return: None
    """
    # The flowing code will register your server to eureka server and also start to send heartbeat every 30 seconds
    eureka_client.init_registry_client(
        eureka_server=eureka_server,
        app_name=app_name,
        instance_port=instance_port,
        instance_ip=instance_ip)


def unregister_service():
    """
            从eureka注销服务
            :return: None
    """
    eureka_client.stop()


def get_applications(eureka_hosts="127.0.0.1", eureka_client=None):
    """
            从eureka获取所有服务
            :param eureka_hosts: eureka地址
            :param eureka_client: eureka客户端
            :return: list
    """
    apps = eureka_client.get_applications(eureka_hosts)

    return apps.applications


def applications_info(app_objs):
    """
            服务信息解析
            :param app_objs: 服务状态信息
            :return: dict
    """
    apps_info = {}
    for app_obj in app_objs:
        apps_info[app_obj.name] = service_info(app_obj.instances)

    logger.info("Debug all applications {}".format(apps_info))

    return apps_info


def service_info(instances):
    """
            服务信息解析
            :param instances: eureka返回的所有服务信息
            :return: list
    """
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

    # logger.info("Debug all services {}".format(ins_info))

    return ins_info


def cache_services(applications_info):
    """
            服务注册到缓存
            :param app_infos: service_info返回的所有服务状态信息
            :return:
    """
    env_type = env_file_conf('ENV_TYPE', default='DEV')
    service_lists = []
    for app_name, app_info_list in applications_info.items():
        for app_info in app_info_list:
            logger.info(app_info)
            service_lists.append({"product": app_info["product"], "service": app_info["service"], "env_type": env_type})
    cached_services = cache_get('services')
    delete_services = unregister_services_conf()
    if not cached_services:
        services = service_lists
        unavailable_services = set()
    else:
        logger.info(cached_services, service_lists, delete_services)
        cached_services_str_list = list(map(lambda service_dict: '_'.join(service_dict.values()), cached_services))
        service_str_lists = list(map(lambda service_dict: '_'.join(service_dict.values()), service_lists))
        delete_str_services = list(map(lambda service_dict: '_'.join(service_dict.values()), delete_services))
        all_services = set(cached_services_str_list).union(set(service_str_lists)).difference(set(delete_str_services))
        # 异常服务集合
        unavailable_services = \
            set(cached_services_str_list).difference(set(service_str_lists)).difference(set(delete_str_services))
        services = list(map(lambda service_str: {
                "product": service_str.split('_')[0],
                "service": service_str.split('_')[1],
                "env_type": service_str.split('_')[2]
            }, all_services))

    cache_set('services', services)
    logger.info("Service cache updated!")
    return unavailable_services


def default_infos(service_list):
    service_infos = {}
    for service_dict in service_list:
        service = service_dict["service"]
        default_attr = {
            'status': 'Down',
            'health_check': '',
            'home_page': '',
            'status_page': '',
            'service_addr': '',
            'data_center': '',
            'hostname': ''
        }
        service_infos[service] = {**service_dict, **default_attr}

    return service_infos


if __name__ == '__main__':
    eureka_ip = '127.0.0.1'
    try:
        eureka_ip = apollo_envs_conf("eureka_ip")
    except Exception as e:
        logger.error("Connecting apollo failed!")
        exit(1)
    server_port = 8000
    server_host = "app-status.sunnywalden.com"
    application_name = "SERVICE-MONITOR"
    regions = ['default']
    # # while True:
    # register_ops()
    all_apps = get_applications(eureka_ip)
    app_infos = applications_info(all_apps)
    cache_services(app_infos)
    logger.info(app_infos)
