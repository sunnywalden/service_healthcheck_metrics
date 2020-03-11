# prometheus_monitor

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](http://github.com/hhyo/archery/blob/master/LICENSE)
[![version](https://img.shields.io/badge/python-3.7.5-blue.svg)](https://www.python.org/downloads/release/python-375/)

    本项目作为Prometheus（为了方便，下文均采用简称：Prome）监控方案中，应用监控的实现。从Eureka获取所有服务的监控状态数据，

将数据格式转换到Prome的metric格式，通过http协议暴露在指定端口的/metrics路径下。Prome通过pull请求获取。

    接口接收metric数据，字段：metric_name, metric_value,metric_lables。
	1）字段说明
		Metric_name 监控项的名称

		Metric_value 监控项的值（必须为数字）

		Metric_labels 监控项的标签（字典key-value形式，采用双引号）
	2）Metric_name命名规范
		
		Service name（仅限小写字母，kptinvest）+ 服务明细（db）+ 值类型（health） + metric值单位 +  metric值统计类型，例子： process_cpu_seconds_total

	3）Metric_labels字段约束，包括app、host、port

		host 监控数据来源主机，ip地址，docker用主机名替代
		port 监控数据来源应用端口
		app  应用名称


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### configure

请根据实际需要，修改.ini中Apollo信息；
配置中心设置Eureka、Redis相关配置项。



### Deploy

```shell script

mkdir -p /data/healthcheck_metrics/configs

cp -r configs/* /data/healthcheck_metrics/configs/

docker-compose up -d

```



## Acknowledgments

* serverdensity/python-daemon

