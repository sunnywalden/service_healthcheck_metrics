#!env/bin/python
# -*- coding:utf-8 -*-

import logging
import sys


class Logger(object):
    def __init__(self, name=None, log_level=logging.DEBUG):
        self.__logger = logging.getLogger(name)
        self.log_level = log_level

    def logger_generate(self):
        stdout_handler = logging.StreamHandler(sys.stdout)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stdout_handler.setLevel(self.log_level)
        stderr_handler.setLevel(max(self.log_level, logging.WARNING))
        formatter = logging.Formatter(
            '%(asctime)s %(process)d %(levelname)s %(thread)d - %(funcName)s %(filename)s:%(lineno)d -[日志信息]: %('
            'message)s '
        )
        stdout_handler.setFormatter(formatter)
        stderr_handler.setFormatter(formatter)
        self.__logger.addHandler(stdout_handler)
        self.__logger.addHandler(stderr_handler)

        return self.__logger
