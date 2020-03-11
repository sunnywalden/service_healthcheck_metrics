#!env/bin/python
# -*- coding:utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler
import sys

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

        # def logger_generate(self):
        stdout_handler = logging.StreamHandler(sys.stdout)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stdout_handler.setLevel(log_level)
        # stderr_handler.setLevel(max(self.log_level, logging.WARNING))
        formatter = logging.Formatter(
            '%(asctime)s %(process)d %(levelname)s %(thread)d - %(funcName)s %(filename)s:%(lineno)d -[日志信息]: %('
            'message)s '
        )
        stdout_handler.setFormatter(formatter)

        fileHandler = TimedRotatingFileHandler(filename='logs/' + name + '.log', when='D', backupCount=3,
                                               encoding="utf-8")
        # 设置日志文件中的输出格式
        fileHandler.setFormatter(formatter)

        # stderr_handler.setFormatter(formatter)
        self.__logger.addHandler(stdout_handler)
        self.__logger.addHandler(fileHandler)

    def logger(self):
        return self.__logger
