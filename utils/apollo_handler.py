#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from pyapollo import ApolloClient

# sys.path.append("..")


def apo_client(app_id, **kwargs):
    """
            获取apollo客户端连接
            return: ApolloClient
    """
    ap_client = ApolloClient(app_id=app_id, **kwargs)
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

