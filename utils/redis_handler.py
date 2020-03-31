# !/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import json

from utils.get_configure import env_file_conf
from utils.apollo_handler import apollo_envs_conf, apo_client
from utils.console_logger import Logger

log = Logger()
logger = log.get_logger()


def redis_conf(apollo_client,):
    """
            从apollo获取缓存配置
            :return: dict
    """
    external = env_file_conf('EXTERNAL', conf_type=bool, default=False)

    redis_host_conf = 'redis_host' if not external else "redis_external_host"
    redis_host = apollo_envs_conf(apollo_client, redis_host_conf)
    redis_port = apollo_envs_conf(apollo_client, "redis_port")
    redis_db = apollo_envs_conf(apollo_client, "redis_db")
    redis_passwd = apollo_envs_conf(apollo_client, "redis_passwd")

    logger.debug("Debug redis info {} {} {}".format(redis_host, redis_port, redis_db))

    return {
        "host": redis_host,
        "port": redis_port,
        "db": redis_db,
        "passwd": redis_passwd
    }


def redis_handler(apollo_client,):
    """
            获取redis连接
            :return: redis.Redis
    """
    cache_dict = redis_conf(apollo_client,)
    r = redis.Redis(
        host=cache_dict["host"],
        port=cache_dict["port"],
        db=cache_dict["db"],
        password=cache_dict["passwd"]
    )

    return r


def cache_get(apollo_client, name):
    """
            从redis获取数据
            :return:
    """
    r = redis_handler(apollo_client)
    try:
        val = json.loads(r.get(name)) if r.get(name) else []
    except Exception as e:
        logger.error("Get {} value from cache failed!{}".format(name, e.__str__()))
        return None
    else:
        return val


def cache_set(apollo_client, name, val):
    """
            保存数据到redis
            :return:
    """
    r = redis_handler(apollo_client)
    try:
        res = r.set(name=name, value=json.dumps(val))
    except Exception as e:
        logger.error("Storage {} to cache failed!{}".format(name, e.__str__()))
        return None
    else:
        logger.info("{} values {}".format(name, val))
        return res
