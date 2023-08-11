import ipaddress
import os
import socket
from time import sleep
from database_utils import readjson_sync,writejson_sync

def is_valid_ipv4_address(address):
    try:
        ip = ipaddress.IPv4Address(address)
        return True
    except ipaddress.AddressValueError:
        return False
while True:
    try:
        data = readjson_sync('./viewer/data.json')
        dbhost = os.environ.get("DB_HOST")
        data['mysqlHost'] = dbhost if is_valid_ipv4_address(dbhost) else socket.gethostbyname(dbhost)

        data['mysqlPort'] = os.environ.get("DB_PORT")
        data['mysqlDataBase'] = os.environ.get("DB_NAME")
        data['mysqlUser'] = os.environ.get("DB_USER")
        data['mysqlPassword'] = os.environ.get("DB_PWD")
        REDISHOST = os.environ.get("REDIS_SERVER_HOST")
        data['redisHost'] = REDISHOST if is_valid_ipv4_address(REDISHOST) else socket.gethostbyname(REDISHOST)
        data['redisPort'] = os.environ.get("REDIS_SERVER_PORT")
        data['redisPassword'] = os.environ.get("REDIS_PASSWORD")
        AListHost = os.environ.get("AListHost")
        if AListHost == None:
            AListHost = 'http://127.0.0.1:5244/AList/api'
        elif is_valid_ipv4_address(AListHost):
            AListHost = 'http://' + AListHost + '/AList/api'
        data['AListHost'] = AListHost
        writejson_sync('./viewer/data.json', data)
     
        Adata = readjson_sync('./AList/data/config.json')

        AListdb_host = os.environ.get("AListdb_host")

        Adata['database']['type'] = 'mysql'
        Adata['database']['host'] = AListdb_host if is_valid_ipv4_address(AListdb_host) else socket.gethostbyname(AListdb_host)
        Adata['database']['port'] = os.environ.get("AListdb_port")
        Adata['database']['user'] = os.environ.get("AListdb_us")
        Adata['database']['password'] = os.environ.get("AListdb_pw")
        Adata['database']['name'] = os.environ.get("AListdb_name")
        Adata['site_url'] = os.environ.get("DOMAIN")
        writejson_sync('./AList/data/config.json', Adata)

        break
    except Exception as e:
        sleep(5)
        print('initjson: '+str(e))

