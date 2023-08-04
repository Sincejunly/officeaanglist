from codecs import register_error
import io
import json
import os
import random
import string
import aiofiles
import aiohttp
import aioredis
from fastapi import Response
from quart import Quart, jsonify, redirect, request, send_file, send_from_directory
from quart_auth import QuartAuth, login_required, current_user, login_user, logout_user, AuthUser
from quart_cors import cors
from quart_session import Session
from bcrypt import checkpw, gensalt, hashpw
import tracemalloc
from quart_session.sessions import SessionInterface
from captcha.image import ImageCaptcha
from database_utils import AsyncMysqlPool, readjson, readjson_sync,writejson
from urllib import parse
import asyncio
import re
import time

tracemalloc.start()
pydith = os.path.dirname(os.path.realpath(__file__))

auth_manager = QuartAuth()
userEditFile = {
}
outAList = True
CaptchaPrefix = 'officeaanglist:Captcha:'
def create_app():
    global AListHost,outAList
    origin = readjson_sync(os.path.join(pydith, 'data.json'))
    app = Quart(__name__, template_folder='auth')
    app.secret_key = "QQ943384135"
    app.config['MYSQL_HOST'] = origin['mysqlHost']
    app.config['MYSQL_USER'] = origin['mysqlUser']
    app.config['MYSQL_PASSWORD'] = origin['mysqlPassword']
    app.config['MYSQL_DB'] = origin['mysqlDataBase']
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PROTECTION'] = True
    auth_manager.init_app(app)
    AListHost = origin['AListHost']
    if AListHost == 'http://127.0.0.1:5244/AList/api':
        outAList = False
    
    return app
app = create_app()

html_message = '''
    <html>
        <head>
            <title>Locked Message</title>
        </head>
        <body>
            <p>你已被锁定，请联系管理员。<br>
            如果你是管理员，请登录管理账号解除IP限制。<br>
            或者在宿主机中执行<code>sudo docker exec officeaanglist python3 init.py -t {}</code></p>
        </body>
    </html>
    '''


async def getAlltype(domains,key,types):
    domains = [d[key] for d in domains if d['type'] == types]
    return domains

# 配置Redis连接
@app.before_serving
async def setup():
    global app,pool,origin
    origin = await readjson(os.path.join(pydith, 'data.json'))
    cache = await aioredis.Redis(
        host=origin['redisHost'],
        port=int(origin['redisPort']),
        password=origin['redisPassword']
    )
    pool = await AsyncMysqlPool.initialize_pool(
        origin['mysqlHost'], int(origin['mysqlPort']), origin['mysqlUser'], origin['mysqlPassword'], origin['mysqlDataBase'])
    
    #domains = await pool.getAllrow('x_domain')

    #domains = await getAlltype(domains, 'Domain', 'believe')

    app = cors(app, allow_origin='0.0.0.0')

    app.config['SESSION_REDIS'] = cache
    Session(app)


@app.route('/query', methods=['GET', 'POST'])
async def query():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)    
    userU = await request.get_json()
    user = None
    if not userU:
        return jsonify({'Error':"not json"})
    
    if(len(userU) == 2):
        for key, value in userU.items():
            if key == 'table':
                continue
            elif key == 'id':
                user = await pool.getMaxid(userU['table'])
            else:
                arrange = key

        if not user:
            user = await pool.get_row_by_value(userU['table'], arrange, userU[arrange])
    elif(len(userU) == 3 and 'id' in userU):
        user = await pool.get_row_by_value(userU['table'], 'id', userU['id'])
    else:
        user = await pool.getAllrow(userU['table'])
    
    if user:
        
        return jsonify(user)
    
    return jsonify(user)

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        #print(f"目录 {path} 创建成功")
    else:
        pass
        #print(f"目录 {path} 已存在")



async def generate_document_key(file_name):
    allowed_chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    seconds_timestamp = str(time.time())
    key = parse.quote(file_name + seconds_timestamp)[:20]
    key = ''.join(char for char in key if char in allowed_chars)
    return key

@app.route('/AListPath', methods=['GET', 'POST'])
async def AListPath():
    global userEditFile
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'), 'Domain', 'distrust'):
        return html_message.format(request.remote_addr)    
    userU = await request.get_json()
    if not userU:
        return jsonify({'Error': "not json"})
    user = await pool.get_row_by_value('x_users','username',userU['username'])

  
    
    RowADD = await pool.get_value_by_value('x_storages', 'mount_path', userU['AListPath'], 'addition')
    
    root_folder_path = json.loads(RowADD['addition'])['root_folder_path']
    create_directory(root_folder_path)

    fileTask = await pool.get_row_by_value('x_fileTask','fileName',userU['fileName'])
    if not fileTask:
        key = await generate_document_key(userU['fileName'])
    else:key = fileTask['key']

    
    
    
    truePath = "{}/{}".format(root_folder_path, userU['fileName'])
    if not (user['id'] in userEditFile):
        alisttoken = await getToken(AListHost, user['username'], user['password'])
        userEditFile.setdefault(user['id'],{
            'userAgent':request.headers.get('User-Agent'),                   
            'Authorization':alisttoken['data']['token'],
            'File-Path':parse.quote("{}/{}".format(userU['AListPath'], userU['fileName'])),
            'Password':user['password'],
            'Content-Length':str(os.path.getsize("{}/{}".format(root_folder_path, userU['fileName']))),
            'truePath':truePath,
            'fileName':userU['fileName']
            })
    else:
        userEditFile[user['id']]['File-Path'] = parse.quote("{}/{}".format(userU['AListPath'], userU['fileName']))
        userEditFile[user['id']]['Password'] = user['password']
        userEditFile[user['id']]['Content-Length']=str(os.path.getsize("{}/{}".format(root_folder_path, userU['fileName'])))
        userEditFile[user['id']]['truePath']=truePath

    if await pool.is_table_empty('x_fileTask'):
        await pool.update('x_fileTask',{'`id`':1,'fileName':userU['fileName'],'`key`':key,'truePath':truePath},True)
    else:
        await pool.update('x_fileTask',{'fileName':userU['fileName'],'`key`':key,'truePath':truePath},True)


    return jsonify(key)


async def download_file(url, path_for_save):
    try:
  
        down = f"wget -O {path_for_save} -q -N '{url}'"
        proc = await asyncio.create_subprocess_shell(down, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, _ = await proc.communicate()  # Wait for the process to complete

        return proc.returncode == 0
    except Exception:
        return False

async def Upload(url,UserAgent,Authorization,localPath, FilePath, password=''):

    upload_header = {
        'UserAgent': UserAgent,
        'Authorization': Authorization,
        'File-Path': FilePath,
        'Password': password,
        'Content-Length': str(os.path.getsize(localPath))
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(localPath, 'rb',encoding='utf-8') as file:
                data = await file.read()
                async with session.put(f'{url}/fs/put', headers=upload_header, data=data) as response:
                    return await response.json()
    except Exception as e:
        return {'code': -1, 'message': str(e)}


async def extract_part_from_url(url, position=0):
    # Regular expression pattern to find the desired part
    pattern = r'([^/]+)'

    # Extract all parts separated by "/"
    parts = re.findall(pattern, url)

    # Return the part at the specified position (default: 0)
    return parts[position]

@app.route('/save', methods=['GET', 'POST'])
async def save():
    global userEditFile
    data = await request.get_json()
    if data.get("status") == 2:
        downloadUri = data.get("url")
        path_for_save = userEditFile[int(data['users'][0])]['truePath']  # 替换为实际保存路径

        if await download_file(downloadUri, path_for_save):
            #key = await extract_part_from_url(downloadUri,4)
            key = await generate_document_key(userEditFile[int(data['users'][0])]['fileName'])

            await pool.update('x_fileTask',{'fileName': \
            userEditFile[int(data['users'][0])]['fileName'],'`key`':key,'truePath':path_for_save},True)

            if outAList:

                await Upload(AListHost, userEditFile[int(data['users'][0])]['userAgent'], 
                userEditFile[int(data['users'][0])]['Authorization'], path_for_save, 
                userEditFile[int(data['users'][0])]['File-Path'])

            #userEditFile.pop(data['users'][0])
        else:
            print("Failed to download the file.")

    return jsonify("{\"error\":0}")

    

@app.route('/delete', methods=['GET', 'POST'])
@login_required
async def delete():
    # if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
    #     return html_message.format(request.remote_addr)    
    userU = await request.get_json()
    
    if not userU:
        return jsonify({'Error':"not json"})
    
    if(len(userU) == 2):
        for key, value in userU.items():
            if key == 'table':
                continue
            else:
                arrange = key
        await pool.delete_row(userU['table'], arrange, userU[arrange])
        if userU['table'] == 'x_user':
            await pool.delete_row('x_users', arrange, userU[arrange])
    return jsonify({'farewell':"ok"})


@app.route('/update', methods=['GET', 'POST'])
@login_required
async def update():
    # if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
    #     return html_message.format(request.remote_addr)
    userU = await request.get_json()
    
    if not userU:
        return jsonify({'Error':"not json"})
    if 'Domain' in userU or 'user' in userU:
        table = userU.pop('table',None)
        user = userU.pop('user') if 'user' in userU else userU.pop('Domain')
        await pool.update(table, user)
    else:
        await pool.update_value(userU['table'], userU['valueName'], userU['value'], userU['columnName'], userU['columnValue']) 

    return jsonify({'farewell':"ok"})

@app.route('/check', methods=['GET', 'POST'])
async def index():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)
    await registerUser()    
    if await current_user.is_authenticated:
        
        user = await pool.get_row_by_value('x_users','`id`',current_user._auth_id)
        # alisttoken = await getToken(AListHost, user['username'], user['password'])
        # userEditFile.setdefault(user['id'],{
        #         'userAgent':request.headers.get('User-Agent'),                   
        #         'Authorization':alisttoken['data']['token'],
        #         'File-Path':'',
        #         'Password':'',
        #         'Content-Length':'',
        #         'truePath':''
        #         })
        
        if isinstance(user, dict):
            if 'password' in user:
                user.pop('password')
        else:
            user = {}

        user['empty'] = False
        user['farewell'] = 'ok'
        return jsonify(user)
        #return redirect('/AriaNg')
    else:
        user = await pool.get_row_by_value('x_user','username','guest')

        if user['disabled'] == 0:
            if isinstance(user, dict):
                if 'password' in user:
                    user.pop('password')
            else:
                user = {}
            return jsonify(user)
        

    return jsonify({
        'empty':await pool.is_table_empty('x_user'),
        'farewell':'ok'
        })

async def upRegister(userU):
    hashed_password = hashpw(userU['password'].encode(), gensalt()).decode()
    # if await pool.is_table_empty('x_user'):
    #     if 'init' in userU:
    #         userU.pop('init')
    #     #update_data = [('id', 'username', 'password', 'type'), ('1', userU['username'], hashed_password, 'believe')]
    #     userU['password'] = hashed_password
    #     await pool.update('x_user', userU, overwrite=True)

    # el
    if 'reset' in userU:
        userU.pop('reset')
        userU['base_path'] = '/'
        if userU['username']:
            await pool.update('x_users', userU, overwrite=True)

            userU['password'] = hashed_password

            userU.pop('base_path')
            await pool.update('x_user', userU, overwrite=True)
        else:

            await pool.update_value('x_users', '`id`', userU['id'], 'disabled', userU['disabled'])
            await pool.update_value('x_users', '`id`', userU['id'], 'permission', userU['permission'])

            userU['password'] = hashed_password

            userU.pop('base_path')
            await pool.update_value('x_user', '`id`', userU['id'], 'disabled', userU['disabled'])
            await pool.update_value('x_user', '`id`', userU['id'], 'permission', userU['permission'])
        
    else:
        if 'init' in userU:
            userU.pop('init')
            userU['password'] = hashed_password
            #update_data = [('username', 'password', 'type'), (userU['username'], hashed_password, userU['type'])]
            await pool.update('x_user', userU, overwrite=True)
        else:
            userU['base_path'] = '/'
            await pool.update('x_users', userU)
            userU['password'] = hashed_password
            userU.pop('base_path')
            await pool.update('x_user', userU)

    user = await pool.get_row_by_value('x_user','id',userU['id'])

    return user

@app.route('/register', methods=['GET', 'POST'])
async def register():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)
    
    if request.method == 'POST':
        userU = await request.get_json()
        if not userU:
            return jsonify({'Error':"Invalid username or password."})

        cache: SessionInterface = app.session_interface

        Captcha = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'Captcha')
        #IPLock = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'Lock')

        # if IPLock:
        #     return jsonify({'Error':"你尝试的次数过多，IP已锁定,一小时后解锁"})
        if not('NoCaptcha' in userU):
            if 'Captcha' in userU and Captcha:
                if Captcha.lower() != userU['Captcha'].lower():
                    return jsonify({'Error':"验证码错误，你可以点击验证码刷新，也可以不刷新"})
            elif not Captcha and 'Captcha' in userU:
                return jsonify({'Error':"验证码已过期，点击验证码刷新"})            
            elif not 'Captcha' in userU:
                return jsonify({'Captcha':"ON",'Error':"请输入验证码",'Refresh':True})
        else:
            userU.pop('NoCaptcha')
        
        
    
        user = await upRegister(userU)


        return jsonify(user)

async def get_cached_value(cache, key):
    try:
        value = await cache.get(key)
        return json.loads(value) if value else None
    except (ValueError, TypeError):
        return None
    
@app.route('/count', methods=['GET', 'POST'])
async def count():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)
    userU = await request.get_json()
    hashed_password = hashpw(userU['password'].encode(), gensalt()).decode()
    await writejson(os.path.join(pydith, 'pd'), {'password':userU['password'],
                            'hashed_password':hashed_password}
                            )
    return jsonify(hashed_password)

async def getToken(url, username, password):
    data = {
        'username': username,
        'password': password
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{url}/auth/login', json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {'code': response.status, 'message': await response.text()}
    except Exception as e:
        return {'code': -1, 'message': str(e)}
    
@app.route('/login', methods=['GET', 'POST'])
async def login():
    global pool
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)
    if request.method == 'POST':
        userU = await request.get_json()
        cache: SessionInterface = app.session_interface
        if not userU:
            return jsonify({'Error':"Invalid username or password."})
        
        user = await pool.get_row_by_value('x_user','username',userU['username'])
       
        #try:
        if user:
            PWNum = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'PWNum')
            Captcha = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'Captcha')
            Lock = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'Lock')
            #IPLock = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'Lock')
            if not PWNum:
                PWNum = 0
                Captcha = None
                Lock = False
                #IPLock = False
                await cache.set(CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'PWNum',json.dumps(0), expiry=3600)
                await cache.set(CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'Lock',json.dumps(False), expiry=3600)
                await cache.set(CaptchaPrefix+request.remote_addr+":"+'Captcha',json.dumps(Captcha), expiry=180)

                await cache.set(CaptchaPrefix+request.remote_addr+":"+'Lock',json.dumps(False), expiry=3600)

            # if IPLock:
            #     return jsonify({'Error':"你尝试的次数过多，IP已锁定,一小时后解锁"})
            if Lock:
                return jsonify({'Error':"你尝试的次数过多，账户已被锁定,一小时后解锁"})
            
            
            if 'Captcha' in userU and PWNum < 20 and Captcha:
                if Captcha.lower() != userU['Captcha'].lower():
                    PWNum = PWNum + 1
                    await cache.set(CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'PWNum',json.dumps(PWNum), expiry=3600)
                    return jsonify({'Error':"验证码错误，你可以点击验证码刷新，也可以不刷新"})
            elif not Captcha and 'Captcha' in userU:
                return jsonify({'Error':"验证码已过期，点击验证码刷新"})            
            elif not 'Captcha' in userU and PWNum >= 4:
                return jsonify({'Captcha':"ON",'Error':"请输入验证码",'Refresh':True})

            inlogin = checkpw(userU['password'].encode(),user['password'].encode())

            if not inlogin:
                PWNum = PWNum + 1
                await cache.set(CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'PWNum',json.dumps(PWNum), expiry=3600)
            if user and inlogin:
                user.pop('password')
                if user['disabled'] == 0:
                    login_user(AuthUser(user['id']))
 

                
                return jsonify(user)
            elif PWNum >= 4 and PWNum < 10:
                return jsonify({'Captcha':"ON",'Error':"用户名或密码错误！"})
            elif PWNum == 10:
                await cache.set(CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'Lock',json.dumps("True"), expiry=3600)
                return jsonify({'Error':"你尝试的次数过多，账户已被锁定,一小时后解锁"})
            elif PWNum > 20:
                if request.remote_addr != '127.0.0.1':
                    await pool.update('x_domain',{'domain':request.remote_addr, 'type':'distrust'})
                    return jsonify({'Error':'你的IP已被锁定'})

            # elif PWNum > 20:
            #     await cache.set(CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'Lock',json.dumps("True"), expiry=3600)
            #     return jsonify({'Error':"你尝试的次数过多，IP已锁定,一小时后解锁"})

        else:
            return jsonify({'Error':"用户不存在"})

        return jsonify({'Error':"用户名或密码错误"})
    
    return jsonify(404)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
async def logout():
    logout_user()
    return jsonify({'message': "You have been logged out."})

@app.route('/protected', methods=['GET', 'POST'])
@login_required
async def protected():
    return request.host

async def generate_verification_code(length=4):
    """生成随机验证码"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

@app.route('/generate_code')
async def generate_code():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)    
    # username = request.args.get("username")
    
    # # 验证用户名或其他必要的验证步骤
    # if not username:
    #     return jsonify({'error': "Invalid username."})
    cache: SessionInterface = app.session_interface
    CaptchaNum = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'CaptchaNum')
    if CaptchaNum is not None:
        CaptchaNum = CaptchaNum + 1
    else:
        CaptchaNum = 0
    if CaptchaNum >= 20:
        if request.remote_addr != '127.0.0.1':
            await pool.update('x_domain',{'domain':request.remote_addr,'type':'distrust'})
        # await cache.set(CaptchaPrefix+request.remote_addr+":"+'Lock', json.dumps(True), expiry=3600)
        # return jsonify({'Error':"你尝试的次数过多，IP已锁定，一小时后解锁"})

    code = await generate_verification_code()
    image_captcha = ImageCaptcha(fonts=[os.path.join(pydith, 'MiSans-Light.ttf')], width=150, height=50)
    image = image_captcha.generate_image(str(code))

    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    await cache.set(CaptchaPrefix+request.remote_addr+":"+'Captcha', json.dumps(code), expiry=180)
    await cache.set(CaptchaPrefix+request.remote_addr+":"+'CaptchaNum', json.dumps(CaptchaNum), expiry=3600)

    return await send_file(img_io, mimetype='image/png')


# @app.route('/AriaNg', defaults={'path': 'index.html'}, methods=['GET', 'POST'])
# @app.route('/AriaNg/<path:path>', methods=['GET', 'POST'])
# async def serve_ariang(path):
#     if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
#         return html_message.format(request.remote_addr) 
#     if await current_user.is_authenticated:
#         ariang_path = 'AriaNg-1.3.6'
#         return await send_from_directory(ariang_path,path)
#     else:
#         return redirect('/viewer/')
    
# @app.route('/aria2/jsonrpc', methods=['GET', 'POST'])
# async def proxy_aria2_jsonrpc():
#     if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
#         return html_message.format(request.remote_addr)    
#     if not await current_user.is_authenticated:
#         return redirect('/viewer/')
#     # Get the request data from the client
#     data = await request.get_data()

#     # Forward the request to the backend server (Aria2 in this case)
#     import httpx
#     response = await httpx.post('http://127.0.0.1:6800'+'/aria2/jsonrpc', data=data)

#     # Create a response with the data from the backend server
#     headers = [(key.encode(), value.encode()) for key, value in response.headers.items()]
#     return Response(response.content, status_code=response.status_code, headers=headers)

#@app.route('/verify_code', methods=['POST'])
async def verify_code(user_code):
    # username = (await request.form)['username']
    # user_code = (await request.form)['code']
    # data = await request.get_json()
    # user_code = data.get('code', '').lower()
    
    cache: SessionInterface = app.session_interface
    Captcha = await cache.get(CaptchaPrefix+request.remote_addr+":"+'Captcha')

    #code_valid = 
    # if code_valid:
    #     await cache.set(CaptchaPrefix+request.remote_addr+":"+username+":"+'Captcha',json.dumps(None), expiry=180)
    return user_code.lower() == Captcha.lower()

async def registerUser():

    users = await pool.getAllrow('x_users')
    for item in users:
        item.pop('base_path')
        item['init']=True
        await upRegister(item)
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)


