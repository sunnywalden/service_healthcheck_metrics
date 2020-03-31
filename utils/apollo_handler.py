#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyapollo import ApolloClient

from utils.config import config
from utils.get_configure import env_file_conf

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


def apo_client():
    """
            获取apollo客户端连接
            return: ApolloClient
    """


    print(
        "debug apollo configures {} {} {} {} {}".format(apollo_host, apollo_port, apollo_cluster, apollo_namespace,
                                                        apollo_app_id))

    ap_client = ApolloClient(
        apollo_app_id,
        config_server_url='http://' + apollo_host + ':' + apollo_port,
        cluster=apollo_cluster,
        timeout=300
    )

    return ap_client


def apo_config(apollo_client, conf_name=None, default_val=None, namespace=None):
    """
            从apollo获取配置项值
            :param apollo_client: ApolloClient apollo客户端
            :param conf_name: string 配置项名称
            :param default_val: string 配置项默认值
            :param namespace: string 配置项所属apollo命名空间
            :return: string, bool, int
    """
    conf_value = apollo_client.get_value(conf_name, default_val=default_val, namespace=namespace)

    return conf_value


def apollo_envs_conf(client, conf_name, conf_type='string'):
    """
            从apollo获取配置项值
            :param conf_name: 环境变量名称
            :param conf_type: 环境变量类型，string bool or int
            :return: string, bool, int
    """

    apo_value = apo_config(client, conf_name=conf_name, default_val=None, namespace=apollo_namespace)

    if conf_type == 'int' and apo_value:
        apo_value = int(apo_value)
    if conf_type == 'bool' and apo_value:
        if apo_value.upper() == 'TRUE':
            apo_value = True
        else:
            apo_value = False


    # 从apollo获取失败则从环境变量获取
    # if not apo_value:
    #     apo_value = tmp_conf(conf_name)
    # else:
    #     tmp_conf_dict = read_tmp()
    #     apo_value = tmp_conf_dict[conf_name]
    #     write_tmp(
    #         tmp_conf_dict
    #     )

    return apo_value
