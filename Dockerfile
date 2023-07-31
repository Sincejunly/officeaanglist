FROM onlyoffice/documentserver:7.1.1

COPY ./system /system

WORKDIR /system

RUN chmod +x /system/* \
    && ./update-mirror.sh --apt python3-pip pkg-config libmariadb-dev aria2c\
	&& pip3 install -r requirements.txt \
	&& pip3 install database_utils-0.1-py3-none-any.whl
	
#&& chown -R www-data:root /var/www/aria2 \

RUN mkdir -p /var/www/app1 \
	&& mkdir -p /var/www/app1/aria2 \
	&& chmod -R g=u /var/www/app1/aria2  \
	&& mkdir -p /var/www/app1/aria2/Download \
	&& chmod -R g=u /var/www/app1/aria2/Download \
	&& mkdir -p /var/www/app1/AList \
	&& chmod -R g=u /var/www/app1/AList \
	&& mkdir -p /var/www/app1/AList/data \
	&& chmod -R g=u /var/www/app1/AList/data \
	&& chmod -R g=u /var/www/app1  \
	&& chown -R root:root /var/www/app1 


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
COPY . /var/www/app1
RUN mv /var/www/app1/AriaNg-1.3.6 /var/www/app1/AriaNg \
	&& rm -rf system \
	&& mv ./run-document-server.sh /app/ds/run-document-server.sh \
	&& rm -rf AriaNg-1.3.6


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

