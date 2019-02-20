# -*- coding:utf-8 -*-
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.wsgi import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import os, sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)


from tools.common_file_handler import data_read, data_write



from tools.daemon import Daemon
from tools.log_generate import Log
from tools.json_file_handler import data_read, data_write
from metrics_implement.common_metric_exporter import CommonGaugeMetric
from prometheus_client.core import REGISTRY, CollectorRegistry
from prometheus_client import start_http_server, Gauge
from pusher.push_metrics import MetricsPush
import os
import time
import json

app = Flask(__name__)
api = Api(app)

data_file_name = 'metrics.dat'

# metric_list = data_read()
# metric_list = {
#     '1': {'metric_name': 'metricrove', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10081,
#           'url': '/metricrove-online/health'},
#     '2': {'metric_name': 'metricrove', 'env_type': 'online', 'host': '10.1.1.76', 'port': 10081,
#           'url': '/metricrove-online/health'},
#     '3': {'metric': 'metricrove-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080,
#           'url': '/metricrove-base/actuator/health'},
#     '4': {'metric': 'metricrove-base', 'env_type': 'online', 'host': '10.1.1.77', 'port': 10080,
#           'url': '/metricrove-base/actuator/health'},
#     '5': {'metric': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.100.15', 'port': 2603, 'url': '/qos'},
#     '6': {'metric_name': 'zhanzhao-web', 'env_type': 'online', 'host': '192.168.102.9', 'port': 2603, 'url': '/qos'}}

lg = Log()
logger = lg.logger_generate('metric_get_interface')


def abort_if_metric_doesnt_exist(keyword):
    metric_list = data_read(data_file_name)
    count = 0
    for i in range(1, len(metric_list) + 1):
        if keyword in metric_list[str(i)].values():
            count += 1
    if count == 0:
        abort(404, message="metric {} doesn't exist".format(keyword))


start_http_server(9815)

parser = reqparse.RequestParser()
parser.add_argument('metric_name', type=str, help='metric name')
parser.add_argument('metric_des', type=str, help='metric describe')
parser.add_argument('metric_value', type=float, help='metric value')
parser.add_argument('metric_labels', type=str, help='metric attributes in key-value form')


class Metrics(Resource):

    def __common_struct(self, data, success=True, msg='error'):
        if success:
            output = {'response': data, 'status': '1', 'message': 'success'}
        else:
            output = {'response': data, 'status': '0', 'message': msg}
        return json.dumps(output)

    def __metric_handler(self):
        for i in range(len(self.lbs_values)):

            if not isinstance(self.lbs_values[i], float) and not isinstance(self.lbs_values[i], int):
                self.lbs_values[i] = self.lbs_values[i].encode('utf-8')
            self.lbs[i] = self.lbs[i].encode('utf-8')
        metric_gauge = Gauge(self.metric_name, self.lbs, self.lbs_values)
        metric_gauge.set(self.metric_value)
        return metric_gauge

    def get(self, keyword):
        metric_list = data_read(data_file_name)
        logger.info(keyword, len(metric_list))
        metrics = []
        for metric in metric_list:
            metric_dict = json.load(metric)
            if keyword in json.loads(metric_dict.values()):
                metrics.append(metric_dict)
        if not metrics:
            return 'metric not exist', 204
        else:
            return metrics, 201

    def delete(self, keyword):
        metric_list = data_read(data_file_name)
        abort_if_metric_doesnt_exist(keyword)
        for i in range(1, len(metric_list) + 1):
            if keyword in metric_list[str(i)].values():
                del metric_list[str(i)]
        data_write(metric_list, data_file_name)
        return metric_list, 201

    def post(self):

        args = parser.parse_args(strict=True)
        metric_name = args['metric_name']
        metric_des = args['metric_des']
        metric_value = args['metric_value']
        tmp_labels = args['metric_labels']
        # print(type(tmp_labels), tmp_labels)
        metric_labels = json.loads(tmp_labels)
        now = int(round(time.time() * 1000000000))
        metric_info = {'metric_name': metric_name, 'metric_value': metric_value, 'metric_labels': metric_labels, 'timestamp': now}

        try:
            # REGISTRY.unregister(CommonMetric)
            metric = CommonGaugeMetric(metric_name, metric_value, metric_labels, now, metric_des)
            # g.time()
            # REGISTRY.register(CommonGaugeMetric(metric_name, metric_value, metric_labels, now))
        except Exception, e:
            logger.info(e)
            res = self.__common_struct('{}', False, str(e))
            return res, 204
        # push metrics to push gateway

        else:
            res = self.__common_struct(metric_info, True, 'success')
            return res, 201

            # m_push = MetricsPush()
            # m_push.metric_pusher(REGISTRY)
            # try:
            #
            #     # start_http_server(9815)
            # except Exception, e:
            #     logger.info(e)
            #     return res, 204
            # else:
            #
            #     return res, 201



class MetricList(Resource):
    def get(self):
        metric_list = data_read(data_file_name)
        # data_write(metric_list)
        return metric_list

    def post(self):
        metric_list = data_read(data_file_name)
        args = parser.parse_args()
        metric_id = len(metric_list) + 1
        metric_list[str(metric_id)] = {'metric_name': args['metric_name'], 'value': args['value'], 'labels': args['labels']}
        data_write(metric_list, data_file_name)
        return metric_list[metric_id], 201


api.add_resource(Metrics, '/', '/metric')
# api.add_resource(MetricList, '/metric')


class FlaskDaemon(Daemon):
    def run(self):
        app.run(debug=True)
        # lg = Log()
        # logger = lg.logger_generate('metrics_upload_test')
        # while True:
        #     # for metric in self.metric_list:
        #         self.log('dealing with metric %s now' % self.metric_list)
        #         metric_inter = MetricInterface(self.metric_list)
        #
        #         metric_inter.get_metrics()
        #
        #         time.sleep(5)


if __name__ == '__main__':
    # REGISTRY.unregister(CommonMetric)

    app.run(host='0.0.0.0', debug=True)

    # lg = Log()
    # logger = lg.logger_generate('get_metric')

    # pid = '/tmp/metric_get_interface.pid'
    # s_daemon = FlaskDaemon(pid)
    # s_daemon.stop()
    # s_daemon.start()
    # if os.path.isfile(pid):
    #     logger.info('metric springboot_metrics started!')
    # else:
    #     logger.info('metric start failed!')
