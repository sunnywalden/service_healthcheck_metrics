#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

from utils.apollo_handler import apo_client, apo_config
from utils.config import config

root_path = os.path.dirname(os.path.abspath(__file__))
tmp_path = os.path.join(root_path, 'configs/' + 'configs.dat')


def env_file_conf(conf_name, conf_type='string', default=None):
    """
            从系统环境变量获取配置项值
            :param default:
            :param conf_name: 环境变量名称
            :param conf_type: 环境变量类型，string bool or int
            :return: string, bool, int
    """
    conf_value = os.getenv(conf_name, default)

    if conf_type == 'int' and conf_value:
        conf_value = int(conf_value)
    if conf_type == 'bool' and conf_value:
        if conf_value.upper() == 'TRUE':
            conf_value = True
        else:
            conf_value = False
    if conf_type == 'float' and conf_value:
        conf_value = float(conf_value)

    return conf_value


def apollo_envs_conf(conf_name, conf_type='string'):
    """
            从apollo获取配置项值
            :param conf_name: 环境变量名称
            :param conf_type: 环境变量类型，string bool or int
            :return: string, bool, int
    """
    env_type = env_file_conf('ENV_TYPE').upper() if env_file_conf('ENV_TYPE') else "DEV"
    apollo_conf = config('configs/apollo.ini')
    external = env_file_conf('EXTERNAL', conf_type='bool')
    print('Debug environment variables {} {}'.format(env_type, external))
    apollo_host_conf = 'host' if not external else 'external_host'
    apollo_host = apollo_conf.getOption(section=env_type, option=apollo_host_conf, default='127.0.0.1')
    apollo_port = apollo_conf.getOption(section=env_type, option='port', default=8080, )
    apollo_cluster = apollo_conf.getOption(section=env_type, option='cluster', default='default')
    apollo_namespace = apollo_conf.getOption(section=env_type, option="namespace", default="application")
    apollo_app_id = apollo_conf.getOption(section=env_type, option="app_id", default="")

    print(
        "debug apollo configures {} {} {} {} {}".format(apollo_host, apollo_port, apollo_cluster, apollo_namespace,
                                                        apollo_app_id))

    client = apo_client(
        apollo_app_id,
        config_server_url='http://' + apollo_host + ':' + apollo_port,
        cluster=apollo_cluster,
        timeout=300
    )

    client.start()

    apo_value = apo_config(client, conf_name=conf_name, default_val=None, namespace=apollo_namespace)

    if conf_type == 'int' and apo_value:
        apo_value = int(apo_value)
    if conf_type == 'bool' and apo_value:
        if apo_value.upper() == 'TRUE':
            apo_value = True
        else:
            apo_value = False

    client.stop()

    # 从apollo获取失败则从环境变量获取
    if not apo_value:
        apo_value = tmp_conf(conf_name)
    else:
        tmp_conf_dict = read_tmp()
        apo_value = tmp_conf_dict[conf_name]
        write_tmp(
            tmp_conf_dict
        )

    return apo_value


def unregister_services_conf():
    """
            从.ini获取需要下架的服务
            :return:
    """
    env_type = env_file_conf('ENV_TYPE').upper() if env_file_conf('ENV_TYPE') else "DEV"
    seervices_conf = config('configs/unregister_services.ini')
    services_str = seervices_conf.getOption(env_type, 'services', default='{}')
    service_dict = json.loads(services_str)
    all_services = []
    if not service_dict: return all_services
    for product, service_str in service_dict.items():
        for service in services_str.split(','):
            service_attr = {"product": all_services[product], "service": service, "env_type": env_type}
            try:
                all_services.index(service_attr)
            except ValueError:
                all_services.append(service_attr)
    return all_services


def get_conf(conf_name, conf_type='string'):
    """
            获取配置项值
            :param conf_name: 环境变量名称
            :param conf_type: 环境变量类型，string bool or int
            :return: string, bool, int
    """
    apollo_value = apollo_envs_conf(conf_name, conf_type=conf_type)

    env_file_value = env_file_conf(conf_name, conf_type=conf_type)

    config_value = apollo_value if apollo_value else env_file_value

    return config_value


def tmp_conf(conf_name):
    """
            从缓存的临时文件获取配置项值
            :param conf_name: 环境变量名称
            :return: string, bool, int
    """
    all_configures = read_tmp()
    if all_configures:
        if conf_name in all_configures.keys:
            return all_configures[conf_name]
    else:
        return None


def read_tmp():
    """
                conf缓存文件读取所有配置项值
                :return:
    """
    if not os.path.exists(tmp_path):
        os.mknod(tmp_path)
        return None
    with open(tmp_path, mode='r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            print("error while read temp file: {}".format(e.__str__()))
            return None


def write_tmp(conf_dict):
    """
                写取配置项值到缓存文件
                :param conf_dict: 配置字典
                :return:
    """

    with open(tmp_path, mode='w', encoding='utf-8') as f:
        try:
            json.dump(conf_dict, f)
        except Exception as e:
            print(e.__str__())
