#!/bin/bash

AListdb_ty=mysql
AListdb_host=db
AListdb_port=3306
AListdb_us=officeaanglist
AListdb_pw=AVXKj[JqUB[ev9Cs
AListdb_name=officeaanglist




function get_ip() {
  local host=$1
  local ipv4_regex="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
  if [[ $host =~ $ipv4_regex ]]; then
    thost=$host
  else
    thost=$(ping -c 1 $host | awk -F'[()]' '/PING/{print $2}')
  fi
  echo $thost
}


sed -i "10s/.*/    \"type\": \"$AListdb_ty\",/" /var/www/app/AList/data/config.json
sed -i "11s/.*/    \"host\": \"$(get_ip $AListdb_host)\",/" /var/www/app/AList/data/config.json
sed -i "12s/.*/    \"port\": $AListdb_port,/" /var/www/app/AList/data/config.json
sed -i "13s/.*/    \"user\": \"$AListdb_us\",/" /var/www/app/AList/data/config.json
sed -i "14s/.*/    \"password\": \"$AListdb_pw\",/" /var/www/app/AList/data/config.json
sed -i "15s/.*/    \"name\": \"$AListdb_name\",/" /var/www/app/AList/data/config.json