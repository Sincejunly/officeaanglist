import os
import socket
from database_utils import readjson_sync,writejson_sync



data = readjson_sync('./viewer/data.json')
data['mysqlHost'] = socket.gethostbyname(os.environ.get("DB_HOST"))
data['mysqlPort'] = os.environ.get("DB_PORT")
data['mysqlDatabase'] = os.environ.get("DB_NAME")
data['mysqlUser'] = os.environ.get("DB_USER")
data['mysqlPassword'] = os.environ.get("DB_PWD")

data['redisHost'] = socket.gethostbyname(os.environ.get("REDIS_SERVER_HOST"))
data['redisPort'] = os.environ.get("REDIS_SERVER_PORT")
data['redisPassword'] = os.environ.get("REDIS_PASSWORD")

writejson_sync('./viewer/data.json', data)