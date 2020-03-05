#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from pyapollo import ApolloClient

sys.path.append("..")


def apo_client(app_id, **kwargs):
    ap_client = ApolloClient(app_id=app_id, **kwargs)
    return ap_client


def apo_config(apollo_client, conf_name=None, default_val=None, namespace=None):
    conf_value = apollo_client.get_value(conf_name, default_val=default_val, namespace=namespace)

    return conf_value

