# -*- coding:utf-8 -*-
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import os, sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from tools.daemon import Daemon
from tools.log_generate import Log
from tools.json_file_handler import data_read, data_write
import os

app = Flask(__name__)
api = Api(app)

data_file_name = 'urls.json'
# app_list = data_read()
# app_list = {
#     '1': {'app_name': 'approve', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10081,
#           'url': '/approve-online/health'},
#     '2': {'app_name': 'approve', 'env_type': 'online', 'host': '10.1.1.76', 'port': 10081,
#           'url': '/approve-online/health'},
#     '3': {'app': 'approve-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080,
#           'url': '/approve-base/actuator/health'},
#     '4': {'app': 'approve-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080,
#           'url': '/approve-base/actuator/health'},
#     '5': {'app': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.100.15', 'port': 2603, 'url': '/qos'},
#     '6': {'app_name': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.102.9', 'port': 2603, 'url': '/qos'}}

lg = Log()
logger = lg.logger_generate('metric_interface')


def abort_if_app_doesnt_exist(keyword):
    app_list = data_read(data_file_name)
    count = 0
    for i in range(1, len(app_list) + 1):
        if keyword in app_list[str(i)].values():
            count += 1
    if count == 0:
        abort(404, message="App {} doesn't exist".format(keyword))



parser = reqparse.RequestParser()
parser.add_argument('app_name', type=str, help='application name')
parser.add_argument('host', type=str, help='application health check host')
parser.add_argument('port', type=int, help='application health check port')
parser.add_argument('env_type', type=str, help='environment type, maybe online, pre or dev')
parser.add_argument('url', type=str, help='application health check '
                                          'endpoint, such as: /health')


class App(Resource):
    def get(self, keyword):
        app_list = data_read(data_file_name)
        logger.info(keyword, len(app_list))
        app_urls = {}
        for i in range(1, len(app_list) + 1):
            logger.info(app_list[str(i)].values())
            if keyword in app_list[str(i)].values():
                app_urls[str(i)] = (app_list[str(i)])
        if not app_urls:
            return 'app not exist', 204
        else:
            return app_urls, 201

    def delete(self, keyword):
        app_list = data_read(data_file_name)
        abort_if_app_doesnt_exist(keyword)
        for i in range(1, len(app_list) + 1):
            if keyword in app_list[str(i)].values():
                del app_list[str(i)]
        data_write(app_list, data_file_name)
        return app_list, 201

    def put(self, keyword):
        app_list = data_read(data_file_name)
        # parser = reqparse.RequestParser()
        # parser.add_argument('app_name', type=str, help='application name')
        # parser.add_argument('env_type', type=str, help='environment type, maybe online, pre or dev')
        # parser.add_argument('url', type=str, help='application health check url, consists of proto host port and '
        #                                           'endpoint, such as: http://192.168.1.2:9000/health')
        args = parser.parse_args(strict=True)
        app_info = {'app_name': args['app_name'], 'host': args['host'], 'port': args['port'],
                    'env_type': args['env_type'], 'url': args['url']}
        app_id = len(app_list) + 1
        app_list[str(app_id)] = app_info
        res = data_write(app_list, data_file_name)
        if res == "success": return app_info, 201
        else: return res


class AppList(Resource):
    def get(self):
        app_list = data_read(data_file_name)
        # data_write(app_list)
        return app_list

    def post(self):
        app_list = data_read(data_file_name)
        args = parser.parse_args()
        app_id = len(app_list) + 1
        app_list[str(app_id)] = {'app_name': args['app_name'], 'host': args['host'], 'port': args['port'],
                            'env_type': args['env_type'], 'url': args['url']}
        data_write(app_list, data_file_name)
        return app_list[app_id], 201


api.add_resource(App, '/apps/<keyword>')
api.add_resource(AppList, '/apps')


class FlaskDaemon(Daemon):
    def run(self):
        app.run(host='0.0.0.0', port=9500)
        # lg = Log()
        # logger = lg.logger_generate('metrics_upload_test')
        # while True:
        #     # for app in self.app_list:
        #         self.log('dealing with app %s now' % self.app_list)
        #         metric_inter = MetricInterface(self.app_list)
        #
        #         metric_inter.get_metrics()
        #
        #         time.sleep(5)


if __name__ == '__main__':
    # app.run(debug=True)
    # lg = Log()
    # logger = lg.logger_generate('get_metric')
    pid = '/tmp/metric_interface.pid'
    s_daemon = FlaskDaemon(pid)
    s_daemon.stop()
    s_daemon.start()
    if os.path.isfile(pid):
        logger.info('app springboot_metrics started!')
    else:
        logger.info('app start failed!')
