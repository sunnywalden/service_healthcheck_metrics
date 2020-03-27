#!env/bin/python
# -*- coding:utf-8 -*-

import logging

# 日志级别关系映射
level_relations = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


class Logger(object):
    def __init__(self, name='service_metrics', log_level='info'):
        self.__logger = logging.getLogger(name)
        log_level = level_relations[log_level]
        self.__logger.setLevel(log_level)

        std_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(process)d %(levelname)s %(thread)d - %(funcName)s %(filename)s:%(lineno)d -[日志信息]: %('
            'message)s '
        )
        std_handler.setFormatter(formatter)

        self.__logger.addHandler(std_handler)

    def get_logger(self):
        return self.__logger
