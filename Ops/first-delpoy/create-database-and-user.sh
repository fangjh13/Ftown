#!/usr/bin/sh

MYSQL_ROOT_PASSWD="my-secret-password"

COMMAND_SH="docker exec -i mariadb sh -c 'exec mysql -uroot -p"${MYSQL_ROOT_PASSWD}"' < Ops/first-delpoy/db-create.sql"

eval ${COMMAND_SH}

COMMAND_SH="docker exec -i ftown sh -c 'flask deploy'"

eval ${COMMAND_SH}

echo 'inital database finished'
