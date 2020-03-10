FROM sunnywalden/centos7-python3.7:latest

# env
ENV ENV_TYPE=prod \
    EXTERNAL=False

RUN mkdir -p /opt/application/healthcheck_exporter/

# add project to the image
ADD . /opt/application/healthcheck_exporter/

WORKDIR /opt/application/healthcheck_exporter/

RUN mkdir -p ~/.pip/ && \
    echo "[global]" > ~/.pip/pip.conf && \
    echo "index-url = http://mirrors.aliyun.com/pypi/simple" >> ~/.pip/pip.conf && \
    echo "[install]" >> ~/.pip/pip.conf && \
    echo "trusted-host = mirrors.aliyun.com" >> ~/.pip/pip.conf && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/*


# RUN server after docker is up
ENTRYPOINT python main/send_metrics.py

EXPOSE 8000