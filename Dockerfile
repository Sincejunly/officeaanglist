ARG od_rout
FROM $od_rout

# COPY ./system /system
# COPY ./service/* /etc/init.d/
COPY . /var/www/app1

# WORKDIR /system

# RUN export PIP_CACHE_DIR='/system/.cache/pip' \
# 	&& echo 'Dir::Cache::Archives /system/.cache/apt;' > /etc/apt/apt.conf \
# 	&& mkdir -p /system/.cache \
# 	&& mkdir -p /system/.cache/apt \
# 	&& mkdir -p /system/.cache/pip \
#     && chmod +x /system/* \
# 	&& mv mc /usr/local/bin/ \
# 	&& ./minio_upload_download.sh -d .cache.tar.gz \
# 	&& chmod +x /etc/init.d/* \
# 	&& update-rc.d alist defaults && update-rc.d aria2c defaults \
# 	&& update-rc.d viewer defaults && update-rc.d php-fpm defaults \
#     && ./update-mirror.sh --apt git python3-pip aria2 pkg-config libmariadb-dev \
# 	iputils-ping vim psmisc php7.4-fpm php-curl libtesseract-dev tesseract-ocr \
# 	tesseract-ocr-chi-sim tesseract-ocr-chi-tra lsof \
# 	&& pip3 install -r requirements.txt \
# 	&& pip3 install database_utils-0.1-py3-none-any.whl \
# 	&& ./downloadAList.sh \
# 	&& ./minio_upload_download.sh -up .cache
	
#&& chown -R www-data:root /var/www/aria2 \

RUN mkdir -p /var/www/app1 \
	&& mkdir -p /var/www/app1/aria2 \
	&& chmod -R g=u /var/www/app1/aria2  \
	&& mkdir -p /var/www/app1/aria2/Download \
	&& chmod -R g=u /var/www/app1/aria2/Download \
	&& chmod -R g=u /var/www/app1  \
	&& chown -R root:root /var/www/app1 \
	&& mkdir -p /var/www/onlyoffice/documentserver/web-apps/apps/documenteditor/main/resources/help/zh 
	

RUN touch /var/www/app1/aria2/aria2.session \
	&& { \
		echo 'dir=/var/www/app/aria2/Download'; \
		echo 'enable-rpc=true'; \
		echo 'rpc-allow-origin-all=true'; \
		echo 'rpc-listen-all=true'; \
		echo 'continue=true'; \
		echo 'input-file=/var/www/app/aria2/aria2.session'; \
		echo 'save-session=/var/www/app/aria2/aria2.session'; \
		echo 'max-concurrent-downloads=20'; \
		echo 'save-session-interval=120'; \
		echo 'connect-timeout=120'; \
		echo 'max-connection-per-server=10'; \
		echo 'min-split-size=10M'; \
		echo 'split=10'; \
		echo 'check-certificate=false'; \
		echo 'rpc-secret=QQ943384135'; \
	} > /var/www/app1/aria2/aria2.conf \
	&& rm -r /app/ds/run-document-server.sh
	
WORKDIR /var/www/app1

RUN chmod +rwx /var/www/app1/* \
	&& mv /var/www/app1/AriaNg-1.3.6 /var/www/app1/AriaNg \
	&& cp -r /var/www/app1/Contents.json /var/www/onlyoffice/documentserver/web-apps/apps/documenteditor/main/resources/help/zh \
	&& rm -rf system \
	&& mv ./run-document-server.sh /app/ds/run-document-server.sh \
	&& rm -rf AriaNg-1.3.6 \
	&& rm -rf service \
	&& rm -rf Contents.json \
	&& sed -i 's/;extension=curl/extension=curl/' /etc/php/7.4/cli/php.ini 



# COPY ./AriaNg-1.3.6 /var/www/app1/AriaNg
# COPY ./callback.php /var/www/app1
# COPY ./viewer.html /var/www/app1
# COPY ./alist /var/www/app1/AList
# COPY ./config.json /var/www/app1/AList/data
# COPY ./run-document-server.sh /app/ds/run-document-server.sh
# COPY ./ds.conf /var/www/app1
# COPY ./dsssl.conf /var/www/app1
# COPY ./js /var/www/app1/js
# COPY ./css /var/www/app1/css
# COPY ./img /var/www/app1/img

RUN chmod 777 /app/ds/run-document-server.sh
VOLUME /var/www/app
WORKDIR /var/www/app
ENTRYPOINT ["/app/ds/run-document-server.sh"]
