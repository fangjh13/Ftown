Ftown
=====

This repository is my personal blog source code.

blog: [https://fythonfang.com/blog](https://fythonfang.com/blog)

## deploy use docker

create `.env` file in project folder, change or fill values and change `Ops/first-delpoy` files username and password.

```shell
cat > .env << EOF
FLASK_APP=manage.py                                 # app entrance
FLASK_ENV=production                                # run flask environment [development|production]
FTOWN_CONFIG=production                             # project environment [development|production|testing]
SECRET_KEY=balabalaabala                            # set flask secret key, used in session
MAIL_USERNAME=example@example.com                   # send mail username
MAIL_PASSWORD=1234567                               # mail password
QINIUAK=abc                                         # 七牛云 access key
QINIUSK=efg                                         # 七牛云 secret key
ELASTICSEARCH_URL=http://elasticsearch:9200         # elasticsearch url
DB_URI=db                                           # database url
FTOWNUSER=database_user                             # database username
FTOWNPASSWD=database_password                       # database password
EOF
```

create `Ops` folder, following structure.

```shell
Ops/
├── acme-out                                # mount acme.sh out
├── elasticsearch                           # elasticsearch config
│   └── elasticsearch.yml
├── mysql                                   # folder use store database, if not mount external ignore and delete volumes in docker-compose.yml
└── nginx
    ├── conf.d
    │   └── ftown.conf
    └── ssl                                 # ssl certs
        └── fythonfang.com                  # your domain if not use https ignore
            ├── ca.pem
            ├── cert.pem
            ├── full.pem
            └── key.pem
```

### method 1: not use https

`docker-compose.yml` config

```shell
version: "3.8"
services:
  ftown:
    image: ftown:v1.0
    container_name: ftown
    build:
      dockerfile: Dockerfile
      context: .
    volumes:
      - socket-dir:/socket

  proxy:
    image: nginx:1.19.0
    container_name: nginx
    ports:
      - 80:80
    volumes:
      - ./Ops/nginx/conf.d:/etc/nginx/conf.d
      - ./Ops/nginx/ssl:/etc/nginx/ssl
      - ./app:/srv/app
      - socket-dir:/socket

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.8.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms64m -Xmx128m"
      - "ES_HEAP_SIZE=100m"
      - "MAX_LOCKED_MEMORY=100000"
      - "MAX_OPEN_FILES=65535"
    volumes:
      - ./Ops/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/data/elasticsearch.yml

  db:
    image: mariadb:10.5.4
    container_name: mariadb
    environment:
      - MYSQL_ROOT_PASSWORD=my-secret-password     # root password if mount /var/lib/mysql delete it
#    volumes:
#      - ./Ops/mysql:/var/lib/mysql                 # mount external if not mount external delete it

volumes:
  socket-dir:
```

`ftown.conf` config file
 
```shell
upstream ftown_server {
  # fail_timeout=0 means we always retry an upstream even if it failed
  # to return a good HTTP response

  # for UNIX domain socket setups
  server unix:/socket/ftown.sock fail_timeout=0;
}

server {
  # if no Host match, close the connection to prevent host spoofing
  listen 80 default_server;
  return 444;
}

server {
  listen 80 deferred;
  client_max_body_size 4G;

  # set the correct host(s) for your site
  # server_name example.com www.example.com;
  server_name 127.0.0.1;

  keepalive_timeout 5;

  # path for static files
  root /srv/app/;

  location / {
    # checks for static file, if not found proxy to app
    try_files $uri @proxy_to_app;
  }

  location @proxy_to_app {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $http_host;
    # we don't want nginx trying to do something clever with
    # redirects, we set the Host: header above already.
    proxy_redirect off;
    proxy_pass http://ftown_server;
  }
}
```

run `docker-compose up` start app. first you should run `Ops/first-delpoy/create-database-and-user.sh` for initial database

### method 2: use HTTPS

If you use HTTPS, the nginx configuration file `ftown.conf` and `docker-compose.yml` is in repo.
