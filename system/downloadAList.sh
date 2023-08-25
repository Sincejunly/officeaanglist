#!/bin/bash

alist=".cache/alist-linux-amd64.tar.gz"

if [ -e "$file_path" ]; then
    echo "File exists at $file_path."
else
    wget -P .cache https://github.com/alist-org/alist/releases/download/v3.26.0/alist-linux-amd64.tar.gz 
	tar -xvf .cache/alist-linux-amd64.tar.gz -C /var/www/app1/AList-3.26.0 
fi