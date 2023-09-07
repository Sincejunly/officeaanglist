#!/bin/bash

ips="192.168.5.4,192.168.5.3,192.168.5.2"  # 注意：包含逗号和顿号
IFS=',，' read -ra ip_array <<< "$ips"

for ip in "${ip_array[@]}"; do
  echo $ip
  python3 init.py -t $ip
done
 
