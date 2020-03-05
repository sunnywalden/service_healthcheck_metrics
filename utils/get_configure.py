#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from utils.apollo_handler import apo_client, apo_config
from utils.config import config


def env_file_conf(conf_name, conf_type='string', default=None):

    conf_value = os.getenv(conf_name, default)

    if conf_type == 'int' and conf_value:
        conf_value = int(conf_value)
    if conf_type == 'bool' and conf_value:
        if conf_value.upper() == 'TRUE':
            conf_value = True
        else:
            conf_value = False

    return conf_value


def apollo_envs_conf(conf_name, conf_type='string'):
    env_type = env_file_conf('ENV_TYPE').upper() if env_file_conf('ENV_TYPE') else "DEV"
    apollo_conf = config('configs/apollo.ini')
    apollo_host = apollo_conf.getOption(section=env_type, option='host', default='127.0.0.1')
    apollo_port = apollo_conf.getOption(section=env_type, option='port', default=8080, )
    apollo_cluster = apollo_conf.getOption(section=env_type, option='cluster', default='default')
    apollo_namespace = apollo_conf.getOption(section=env_type, option="namespace", default="application")
    apollo_app_id = apollo_conf.getOption(section=env_type, option="app_id", default="")

    print(apollo_host, apollo_port, apollo_cluster, apollo_namespace, apollo_app_id)

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

    return apo_value


def get_conf(conf_name, conf_type='string'):

    apollo_value = apollo_envs_conf(conf_name, conf_type=conf_type)

    env_file_value = env_file_conf(conf_name, conf_type=conf_type)

    config_value = apollo_value if apollo_value else env_file_value

    return config_value
