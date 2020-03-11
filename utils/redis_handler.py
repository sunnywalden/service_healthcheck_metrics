# !/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import json

from utils.get_configure import apollo_envs_conf, env_file_conf
from utils.console_logger import Logger

log = Logger()
logger = log.logger()


def redis_conf():
    """
            从apollo获取缓存配置
            :return: dict
    """
    external = env_file_conf('EXTERNAL', conf_type=bool, default=False)

    redis_host_conf = 'redis_host' if not external else "redis_external_host"
    redis_host = apollo_envs_conf(redis_host_conf)
    redis_port = apollo_envs_conf("redis_port")
    redis_db = apollo_envs_conf("redis_db")
    redis_passwd = apollo_envs_conf("redis_passwd")

    print("Debug redis info {} {} {}".format(redis_host, redis_port, redis_db))

    return {
        "host": redis_host,
        "port": redis_port,
        "db": redis_db,
        "passwd": redis_passwd
    }


def redis_handler():
    """
            获取redis连接
            :return: redis.Redis
    """
    cache_dict = redis_conf()
    r = redis.Redis(
        host=cache_dict["host"],
        port=cache_dict["port"],
        db=cache_dict["db"],
        password=cache_dict["passwd"]
    )

    return r


def cache_get(name):
    """
            从redis获取数据
            :return:
    """
    r = redis_handler()
    try:
        val = json.loads(r.get(name)) if r.get(name) else []
    except Exception as e:
        # print("Get {} value from cache failed!{}".format(name, e.__str__()))
        print("Get {} value from cache failed!{}".format(name, e.__str__()))
        return None
    else:
        return val


def cache_set(name, val):
    """
            保存数据到redis
            :return:
    """
    r = redis_handler()
    try:
        res = r.set(name=name, value=json.dumps(val))
    except Exception as e:
        # print("Storage {} to cache failed!{}".format(name, e.__str__()))
        print("Storage {} to cache failed!{}".format(name, e.__str__()))
        return None
    else:
        # print("{} values {}".format(name, val))
        print("{} values {}".format(name, val))
        return res
