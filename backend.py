import json
import random
import string
from quart import Quart, request, jsonify, send_file, session
from captcha.image import ImageCaptcha
from quart_session import Session
import aioredis
import io
from quart_session.sessions import SessionInterface
import mysql.connector
from quart_cors import cors
import requests
import urllib.parse
import asyncio
import aiofiles
app = Quart(__name__)
app = cors(app)

dbConfig = {
    "host": "192.168.5.4",
    "port": 3306,
    "database": "AList",
    "user": "root",
    "password": "123456"
}
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PROTECTION'] = True
app.secret_key = "QQ943384135"
# 配置Redis连接
@app.before_serving
async def setup():
    cache = await aioredis.Redis(
        host="192.168.5.4",
        port=6379,
        password="159756"
    )
    
    app.config['SESSION_REDIS'] = cache
    Session(app)

def get_database_connection():
    return mysql.connector.connect(**dbConfig)

def create_table(connection):
    create_table_query = "CREATE TABLE IF NOT EXISTS x_key (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), value VARCHAR(255))"
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()

def add_name_column(connection):
    add_column_query = "ALTER TABLE x_key ADD COLUMN IF NOT EXISTS name VARCHAR(255)"
    cursor = connection.cursor()
    cursor.execute(add_column_query)
    connection.commit()
    cursor.close()

@app.route("/insert", methods=["POST"])
async def insert_data():
    data = await request.get_json()
    name = data["name"]
    value = data["value"]

    connection = get_database_connection()
    insert_query = "INSERT INTO x_key (name, value) VALUES (%s, %s)"
    cursor = connection.cursor()
    cursor.execute(insert_query, (name, value))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Data inserted successfully"})

@app.route("/delete/<name>", methods=["DELETE"])
async def delete_data(name):
    connection = get_database_connection()
    delete_query = "DELETE FROM x_key WHERE name = %s"
    cursor = connection.cursor()
    cursor.execute(delete_query, (name,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"message": "Data deleted successfully"})

@app.route("/query", methods=["POST"])
async def query_data():
    data = await request.get_json()
    table = data.get("table")
    column = data.get("column")
    value = data.get("value")

    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    select_query = f"SELECT * FROM {table} WHERE {column} = %s"
    cursor.execute(select_query, (value,))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify(result)

@app.route("/login", methods=["POST"])
async def update_data():
    

async def get_path_from_url(url, range):
    base_url = urllib.parse.unquote(url[:url.rfind('?')] if '?' in url else url)
    base_url = base_url.replace('/p/', '/')
    segments = base_url.split('/')
    if range == 'none':
        return base_url
    elif range == 'front':
        full_path = '/'.join(segments[:4])
    elif range == 'back':
        full_path = '/'.join(segments[:-1])
    elif range == 'fileName':
        full_path = segments[-1]
    elif range == 'AListPath':
        full_path = '/'+'/'.join(segments[5:-1])
    else:
        raise ValueError("Invalid range value")

    return full_path

async def save_file(path, data, mode='wb', encode='utf-8'):
    async with aiofiles.open(path, mode, encoding=encode) as file:
        await file.write(data)

@app.route("/save", methods=["POST"])
async def handle_request():
    global fileFullName
    data = await request.get_json()
    if not data:
        return "Bad Request", 400

    if data["status"] == 2:
        download_uri = data["url"]
        response = requests.get(download_uri)
        AlistPath = await get_path_from_url(download_uri, 'AListPath')
        if response.status_code != 200:
            return "Bad download", 500
        if AlistPath in fileFullName:
            new_data = response.content
            await save_file(fileFullName[AlistPath], new_data)
            print("save success at %s" % fileFullName[AlistPath])
        else:
            return "Bad save", 401

    return "{\"error\":0}"

@app.route("/AListPath", methods=["POST"])
async def FilePath():
    global fileFullName
    data = await request.get_json()
    if not data or "AListPath" not in data or "fileName" not in data:
        return "Bad Request", 400

    AListPath = data["AListPath"]
    fileName = data["fileName"]

    table = 'x_storages'
    column = 'mount_path'

    connection = get_database_connection()
    select_query = f"SELECT * FROM {table} WHERE {column} = %s"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(select_query, (AListPath,))
    results = cursor.fetchone()

    dictionary_string = results['addition']
    dictionary = json.loads(dictionary_string)
    fileFullName.setdefault(AListPath, dictionary["root_folder_path"] + fileName)
    return "Success"

async def generate_verification_code(length=4):
    """生成随机验证码"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

@app.route('/generate_code')
async def generate_code():
    global session
    code = await generate_verification_code()
    image_captcha = ImageCaptcha(width=150, height=50)
    image = image_captcha.generate_image(code)

    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    #session["Captcha"] = code
    cache: SessionInterface = app.session_interface
    jc = json.dumps({session['_addr']:
                     {
                      'Captcha': code, 
                      'Captcha_valid': False
                      }
                     })
    await cache.set("officeaanglist:Captcha",jc, expiry=180)

    return await send_file(img_io, mimetype='image/png')


@app.route('/verify_code', methods=['POST'])
async def verify_code():
    global session
    data = await request.get_json()
    user_code = data.get('code', '').lower()
  
    cache: SessionInterface = app.session_interface
    Captcha = await cache.get("officeaanglist:Captcha")
 
    Captcha = json.loads(Captcha)
    
    code_valid = user_code == Captcha[session['_addr']]['Captcha'].lower()

    if code_valid:
        Captcha[session['_addr']]['Captcha_valid'] = True
        await cache.set("officeaanglist:Captcha",json.dumps(Captcha), expiry=180)

    return jsonify({'valid': code_valid})

async def run_app():
    await app.run_task(host='localhost', port=5000)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_app())
