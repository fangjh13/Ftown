FROM python:3.7.6

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /srv

COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt -i https://mirrors.cloud.tencent.com/pypi/simple

COPY app app
COPY migrations migrations
COPY config.py manage.py run.sh ./
COPY .env .env

CMD ["/bin/bash", "run.sh"]
