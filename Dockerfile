FROM onlyoffice/documentserver:7.1.1

COPY ./system /system
COPY ./service/* /etc/init.d/
COPY . /var/www/app1

WORKDIR /system

RUN export PIP_CACHE_DIR='/system/.cache/pip' \
	&& echo 'Dir::Cache::Archives /system/.cache/apt;' > /etc/apt/apt.conf \
	&& mkdir -p /system/.cache \
	&& mkdir -p /system/.cache/apt \
	&& mkdir -p /system/.cache/pip \
    && chmod +x /system/* \
	&& mv mc /usr/local/bin/ \
	&& ./minio_upload_download.sh -d .cache.tar.gz \
	&& chmod +x /etc/init.d/* \
	&& update-rc.d alist defaults && update-rc.d aria2c defaults \
	&& update-rc.d viewer defaults && update-rc.d php-fpm defaults \
    && ./update-mirror.sh --apt git python3-pip aria2 pkg-config libmariadb-dev \
	iputils-ping vim psmisc php7.4-fpm php-curl libtesseract-dev tesseract-ocr \
	tesseract-ocr-chi-sim tesseract-ocr-chi-tra lsof \
	&& pip3 install -r requirements.txt \
	&& pip3 install database_utils-0.1-py3-none-any.whl \
	&& ./downloadAList.sh \
	&& ./minio_upload_download.sh -up .cache