FROM python:3.7.6

WORKDIR /srv

COPY requirement.txt ./
RUN pip install -r requirement.txt -i https://mirrors.cloud.tencent.com/pypi/simple

COPY app app
COPY migrations migrations
COPY config.py manage.py run.sh ./
COPY .env .env

EXPOSE 8000

CMD ["/bin/bash", "run.sh"]