#!env/bin/python
# -*- coding:utf-8 -*-
import logging
import socket
from logging.handlers import RotatingFileHandler
import os


class Logger(object):
    def __init__(self):
        self.__logger = logging.getLogger('log')

    def logger_generate(self, name):

        self.__logger.setLevel(logging.INFO)

        log_file = os.path.join('./logs', name + '.log')

        handler = RotatingFileHandler(filename=log_file, mode='a', encoding='utf-8', maxBytes=1024 * 1024,
                                      backupCount=3)

        formatter = logging.Formatter(
            fmt='%(asctime)s %(process)d %(levelname)s %(thread)d - %(funcName)s %(filename)s:%(lineno)d %(message)s')
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)
        socket.setdefaulttimeout(10)

        return self.__logger
