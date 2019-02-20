# -*- coding:utf-8 -*-
import json
import os, sys
from tools.log_generate import Log

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

file_dir = '../data'
# file = 'urls.json'
lg = Log()
logger = lg.logger_generate('metric_interface')


def return_file(file_name):
    # with open(, m) as f:
    #     logger.info('Open %s for %s' % (file, m))
    return os.path.join(file_dir, file_name)


def data_write(urls, file_name):
    todo_f = return_file(file_name)

    with open(todo_f, 'w') as f:
    # f = open_file('w')
        try:
            json.dump(urls, f)
            return 'success'
        except Exception, e:
            return e
        # logger.info('Urls write to file %s success!' % file)


def data_read(file_name):
    todo_f = return_file(file_name)
    with open(todo_f, 'r') as f:
    # f = open_file('r')
        try:
            res = json.load(f, encoding='utf-8')
            # logger.info('Read file %s success!' % file)
        except Exception, e:
            res = {}
            logger.error(e)
        else:
            return res
