# prometheus_monitor

    本项目作为Prometheus（为了方便，下文均采用简称：Prome）监控方案中，应用监控的实现。通过接口接收监控数据，

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

### Prerequisites

```
prometheus-client  	==0.4.2
python             	>=2.7
werkzeug		0.14.1
prometheus-client	0.4.2
flask			1.0.2
flask_restful		0.3.6
uwsgi			2.0.17.1
```

### Installing

1.clone this project to your server with git clone comand.
git clone ...

2.install those depending packages in requirements.txt with pip install.
```
yum install -y python-devel

yum install python-pip

pip install --upgrade pip

python -m pip install --user virtualenv

cd prometheus_metrics

python -m virtualenv env

source env/bin/activate

pip install -r requirements.txt
```


3.update main/config.ini in your needs for ip 、port and other configures alter.


4.alter iptables configure to let requests of services' port could reachable.

```
iptables -A INPUT -p tcp --dport 9814 -j ACCEPT
```


5.service start.
```
	cd main

	uwsgi --ini ../configs/config.ini
```


## Acknowledgments

* serverdensity/python-daemon

