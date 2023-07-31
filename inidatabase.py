import os
from database_utils import readjson_sync,writejson_sync

pydith = os.path.dirname(os.path.realpath(__file__))

data = readjson_sync(os.path.join(pydith, '/viewer/data.json'))
data['mysqlHost'] = os.environ.get("DB_HOST")
data['mysqlPort'] = os.environ.get("DB_PORT")
data['mysqlDatabase'] = os.environ.get("DB_NAME")
data['mysqlUser'] = os.environ.get("DB_USER")
data['mysqlPassword'] = os.environ.get("DB_PWD")

data['redisHost'] = os.environ.get("REDIS_SERVER_HOST")
data['redisPort'] = os.environ.get("REDIS_SERVER_PORT")
data['redisPassword'] = os.environ.get("REDIS_PASSWORD")

writejson_sync(os.path.join(pydith, 'data.json'),data)