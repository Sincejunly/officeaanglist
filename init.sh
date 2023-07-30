#!/bin/sh
if [ "$(docker ps -a | grep $di_name)" ]; then docker rm -f $di_name; fi
if [ "$(docker ps -a | grep $di_name-db)" ]; then docker rm -f $di_name-db; fi
if [ "$(docker ps -a | grep qbittorrent-nox)" ]; then docker rm -f qbittorrent-nox; fi

#sed -i "6s/.*/    container_name: $dd_name-db/" docker-compose.yml
sed -i "48s/.*/    container_name: $dd_name/" docker-compose.yml
sed -i "62s/.*/      - DB_HOST=$ser_ip/" docker-compose.yml
sed -i "66s/.*/      - DB_PWD=$officedb_pw/" docker-compose.yml
sed -i "67s/.*/      - REDIS_SERVER_HOST=$ser_ip/" docker-compose.yml
sed -i "69s/.*/      - REDIS_PASSWORD=$db_r/" docker-compose.yml
sed -i "70s/.*/      - DOMAIN=$office_domain/" docker-compose.yml
sed -i "72s/.*/      - AListdb_host=$ser_ip/" docker-compose.yml
sed -i "75s/.*/      - AListdb_pw=$AListdb_pw/" docker-compose.yml
echo $office_domain
cat docker-compose.yml

