import ipaddress
import os
import socket
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

        writejson_sync('./viewer/data.json', data)
        break
    except Exception as e:
        print('error':str(e))
        pass
