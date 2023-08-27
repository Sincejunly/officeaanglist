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
import threading
import websockets
import sys
tracemalloc.start()
pydith = os.path.dirname(os.path.realpath(__file__))

auth_manager = QuartAuth()
userEditFile = {
}
outAList = True
CaptchaPrefix = 'officeaanglist:Captcha:'
def create_app():
    global AListHost,outAList,origin
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
@app.after_request
async def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # 允许所有域访问，也可以指定特定域
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response
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
    
    domains = await pool.getAllrow('x_domain')

    domains = await getAlltype(domains, 'Domain', 'believe')

    app = cors(app, allow_origin=domains)
    app.config['SESSION_REDIS'] = cache
    Session(app)

    await registerUser()

@app.route('/checkUser',methods=['GET', 'POST'])
async def checkUser():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)
    await block()
    userU = await request.get_json()
    if 'username' in userU:
        user = await pool.get_row_by_value('x_user', 'username', userU['username'])
        if user:
            return jsonify({'whether':True})
        else:
            return jsonify({'whether':False})
    elif 'id' in userU:
        id = await pool.getMaxid('x_user')
        return jsonify({'id':id})

@app.route('/query', methods=['GET', 'POST'])
@login_required
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
#@login_required
async def AListPath():
    global userEditFile,outAList
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'), 'Domain', 'distrust'):
        return html_message.format(request.remote_addr)    
    userU = await request.get_json()
    if not userU:
        return jsonify({'Error': "not json"})
    user = await pool.get_row_by_value('x_users','username',userU['username'])
    
  
    
    RowADD = await pool.get_row_by_value('x_storages', 'mount_path', userU['AListPath'])

    if RowADD['driver'] == 'Local':
        root_folder_path = json.loads(RowADD['addition'])['root_folder_path'] + '/'
        create_directory(root_folder_path)
    else:
        outAList = True
        create_directory('fileCahe')
        root_folder_path = 'fileCahe/'

    fileTask = await pool.get_row_by_value('x_fileTask','fileName',userU['fileName'])
    
    key = await generate_document_key(userU['fileName'])
    
    fileType = userU['fileName'][userU['fileName'].rfind('.'):]
    
    
    
    #truePath = "{}/{}".format(root_folder_path, userU['fileName']) if root_folder_path else ''
    if not (user['id'] in userEditFile):
        if outAList:
            alisttoken = await getToken(AListHost, user['username'], user['password'])
        else:
            alisttoken = {'data':{'token':''}}
        userEditFile.setdefault(user['id'],{
            'userAgent':request.headers.get('User-Agent'),                   
            'Authorization':alisttoken['data']['token'],
            'File-Path':{userU['fileName']:parse.quote("{}/{}".format(userU['AListPath'], userU['fileName']))},
            'Password':user['password'],
            'Content-Length':str(os.path.getsize("{}/{}".format(root_folder_path, userU['fileName']))),
            'truePath':{userU['fileName']:root_folder_path},
            #'fileName':{userU['fileName']:}
            })
    else:
        userEditFile[user['id']]['File-Path'][userU['fileName']] = parse.quote("{}/{}".format(userU['AListPath'], userU['fileName']))
        userEditFile[user['id']]['Password'] = user['password']
        userEditFile[user['id']]['Content-Length']=str(os.path.getsize("{}/{}".format(root_folder_path, userU['fileName'])))
        userEditFile[user['id']]['truePath'][userU['fileName']]=root_folder_path
        #userEditFile[user['id']]['fileName'] = userU['fileName']
    
    if await pool.is_table_empty('x_fileTask'):
        await pool.update(
        'x_fileTask',{
            '`id`':1,
            'fileName':userU['fileName'],
            '`key`':key,'history':{},
            'users':[],'actions':[],
            "lastsave":"", \
            "notmodified":False,"filetype":fileType,
            'truePath':root_folder_path},True)
    else:
        await pool.update(
        'x_fileTask',{
            'fileName':userU['fileName'],
            '`key`':key,'history':{},
            'users':[],'actions':[],
            "lastsave":"", \
            "notmodified":False,"filetype":fileType,
            'truePath':root_folder_path},True)


    return jsonify({'key':key,'farewell':"ok"})


async def runCmd(cmd):
    try:
  
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, _ = await proc.communicate()  
        print(cmd)
        return proc.returncode == 0
    except Exception as e:
        print(e)
        return False

async def Upload(url, UserAgent, Authorization, localPath, FilePath, password=''):

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
    global userEditFile,outAList
    data = await request.get_json()
    if data.get("status") == 2:
        downloadUri = data.get("url")
        key = await extract_part_from_url(downloadUri, 4)
        
        fileTask = await pool.get_row_by_value('x_fileTask','`key`',key[:key.rfind('_')])
        fileName = fileTask['fileName']
        truePath = fileTask['truePath']
        key = await generate_document_key(fileName)

        path_for_save = truePath + fileName  # 替换为实际保存路径

        if await runCmd(f"wget -O {path_for_save} -q -N '{downloadUri}'"):
            #key = await generate_document_key(userEditFile[int(data['users'][0])]['fileName'])
            history = data.get("history") if data.get("history") else {}
            users = data.get('users') if data.get('users') else []
            actions = data.get('actions') if data.get('actions') else []
            lastsave = data.get("lastsave") if data.get("lastsave") else ""
            notmodified = data.get("notmodified") if data.get("notmodified") else False
            filetype = data.get("filetype") if data.get("filetype") else ""


            await pool.update(
                'x_fileTask',{
                'fileName': fileName, \
                '`key`':key,'history':history, \
                'users':users,'actions':actions,
                "lastsave":lastsave, \
                "notmodified":notmodified,"filetype":filetype, \
                'truePath':truePath},True)
            
            # await pool.update('x_fileTask',{'fileName': \
            # fileName, '`key`':key,'truePath':path_for_save},True)

            if outAList:

                await Upload(AListHost, userEditFile[int(data['users'][0])]['userAgent'], 
                userEditFile[int(data['users'][0])]['Authorization'], path_for_save, 
                userEditFile[int(data['users'][0])]['File-Path'][fileName])

            #userEditFile.pop(data['users'][0])
        else:
            print("Failed to download the file.")

    return jsonify({'farewell':"ok"})

async def read_stream_and_display(stream, display,websocket):
    """Read from stream line by line until EOF, display, and capture the lines."""
    output = []
    while True:
        line = await stream.readline()
        #line = await stream.read(1)
        if not line:
            break
        output.append(line)
        display(line)
        try:
            await websocket.send(line)
        except:pass
    return b''.join(output)

async def run_command_as_string(command,websocket):
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.gather(
            read_stream_and_display(process.stdout, sys.stdout.buffer.write,websocket),
            read_stream_and_display(process.stderr, sys.stderr.buffer.write,websocket),
        )
    except Exception:
        process.kill()
        raise
    finally:
        rc = await process.wait()

    return rc, stdout, stderr

# async def echo(websocket, path):
#     async for message in websocket:
#         print(f"收到消息: {message}")
#         await websocket.send(f"服务器回复: {message}")

#@app.websocket('/orc')
#@login_required
async def orc(websocket, path):
    # if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
    #     return html_message.format(request.remote_addr)    
    #userU = await websocket.receive_json()
    await websocket.send('转换中！')
    
    async for userU in websocket:
        if not userU:
            return jsonify({'Error':"not json"})
        
        userU = json.loads(userU)
        truPath = userEditFile[userU['id']]['truePath'][userU['fileName']]
      
        fileNameP = userU['fileName'][:userU['fileName'].rfind('.')]

        filePath = truPath + userU['fileName'] 
        orcFilePath = truPath + fileNameP+'_orc'+userU['fileType']

        await run_command_as_string(f"ocrmypdf {userU['cmd']} {filePath}  {orcFilePath} ",websocket)
        if outAList:
            await Upload(AListHost, userEditFile[userU['id']]['userAgent'], 
            userEditFile[userU['id']]['Authorization'], 
            orcFilePath, 
            parse.quote("{}/{}".format(userU['AListPath'], fileNameP+'_orc'+userU['fileType']))
            )
        try:
            await websocket.close()
        except:pass

    #     return jsonify({'message': "ok"})

    # else:
    #     return jsonify({'Error': "失败"})

@app.route('/delete', methods=['GET', 'POST'])
@login_required
async def deletet():
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

    if await current_user.is_authenticated:
        
        user = await pool.get_row_by_value('x_user','`id`',current_user._auth_id)
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
      
   
        if isinstance(user, dict):
            if 'password' in user:
                user.pop('password')
            user['empty'] = False
            user['farewell'] = 'ok'
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
    showViewer=False
    if 'showViewer' in userU:
        showViewer = userU.pop('showViewer')
    if 'init' in userU:
        userU.pop('init')
        userU['password'] = hashed_password
        userU['showViewer'] = showViewer
        #update_data = [('username', 'password', 'type'), (userU['username'], hashed_password, userU['type'])]
        await pool.update('x_user', userU)
    else:
        userU['base_path'] = '/'
        await pool.update('x_users', userU,True)
        userU['password'] = hashed_password
        userU['showViewer'] = showViewer
        userU.pop('base_path')
        await pool.update('x_user', userU)
        
    

    user = await pool.get_row_by_value('x_user','id',userU['id'])

    return user

@app.route('/ChangeUser', methods=['GET', 'POST'])
@login_required
async def ChangeUser():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)
    userU = await request.get_json()
    if 'password' in userU:
        hashed_password = hashpw(userU['password'].encode(), gensalt()).decode()
    
    if 'reset' in userU:
        userU.pop('reset')
        
        userU['base_path'] = (await pool.get_row_by_value('x_users','`id`',userU['id']))['base_path']

        if userU['username']:
            await pool.update('x_users', userU, overwrite=True)

            userU['password'] = hashed_password

            userU.pop('base_path')
            await pool.update('x_user', userU, overwrite=True)
        elif 'showViewer' in userU:
            await pool.update_value('x_user','`id`',userU['id'],'showViewer',userU['showViewer'])
        elif 'permission' in userU:
            await pool.update_value('x_users', '`id`', userU['id'], 'disabled', userU['disabled'])
            await pool.update_value('x_users', '`id`', userU['id'], 'permission', userU['permission'])

            userU['password'] = hashed_password

            userU.pop('base_path')
            await pool.update_value('x_user', '`id`', userU['id'], 'disabled', userU['disabled'])
            await pool.update_value('x_user', '`id`', userU['id'], 'permission', userU['permission'])
        user = await pool.get_row_by_value('x_user','id',userU['id'])
    else:
        user = await upRegister(userU)

    user['farewell'] = 'ok'
    return jsonify(user)
   

@app.route('/register', methods=['GET', 'POST'])
async def register():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)
    
    if request.method == 'POST':
        userU = await request.get_json()
        if not userU:
            return jsonify({'Error':"Invalid username or password."})

        await block()

        cache: SessionInterface = app.session_interface

        Captcha = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'Captcha')
        
        #IPLock = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'Lock')

        # if IPLock:
        #     return jsonify({'Error':"你尝试的次数过多，IP已锁定,一小时后解锁"})
        
        if 'Captcha' in userU and Captcha:
            if Captcha.lower() != userU['Captcha'].lower():
                return jsonify({'Error':"验证码错误，你可以点击验证码刷新，也可以不刷新"})
            userU.pop('Captcha')
        elif not Captcha and 'Captcha' in userU:
            return jsonify({'Error':"验证码已过期，点击验证码刷新"})            
        elif not 'Captcha' in userU:
            return jsonify({'Captcha':"ON",'Error':"请输入验证码",'Refresh':True})

        
        
    
        user = await upRegister(userU)
        
        #await runCmd('service alist restart')

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
            if PWNum >= 4 and PWNum < 10:
                return jsonify({'Captcha':"ON",'Error':"用户名或密码错误！"})
            elif PWNum == 10:
                await cache.set(CaptchaPrefix+request.remote_addr+":"+user['username']+":"+'Lock',json.dumps("True"), expiry=3600)
                return jsonify({'Error':"你尝试的次数过多，账户已被锁定,一小时后解锁"})
            elif user and inlogin:
                user.pop('password')
                if user['disabled'] == 0:
                    login_user(AuthUser(user['id']))
                else:
                    return jsonify({'Error':"你的账户还未激活！"})
                return jsonify(user)
 
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

async def block():
    cache: SessionInterface = app.session_interface
    CaptchaNum = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'CaptchaNum')
    if CaptchaNum is not None:
        CaptchaNum = CaptchaNum + 1
    else:
        CaptchaNum = 0
    await cache.set(CaptchaPrefix+request.remote_addr+":"+'CaptchaNum', json.dumps(CaptchaNum), expiry=3600)
    if CaptchaNum >= 20:
        if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','believe'):
            await cache.set(CaptchaPrefix+request.remote_addr+":"+'CaptchaNum', json.dumps(0), expiry=3600)
            return
        if request.remote_addr != '127.0.0.1' :
            await pool.update('x_domain',{'domain':request.remote_addr,'type':'distrust'})

@app.route('/generate_code')
async def generate_code():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)    
    # username = request.args.get("username")
    
    # # 验证用户名或其他必要的验证步骤
    # if not username:
    #     return jsonify({'error': "Invalid username."})
    await block()
        # await cache.set(CaptchaPrefix+request.remote_addr+":"+'Lock', json.dumps(True), expiry=3600)
        # return jsonify({'Error':"你尝试的次数过多，IP已锁定，一小时后解锁"})
    cache: SessionInterface = app.session_interface
    CaptchaNum = await get_cached_value(cache, CaptchaPrefix+request.remote_addr+":"+'CaptchaNum')
    code = await generate_verification_code()
    image_captcha = ImageCaptcha(fonts=[os.path.join(pydith, 'MiSans-Light.ttf')], width=150, height=50)
    image = image_captcha.generate_image(str(code))

    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    await cache.set(CaptchaPrefix+request.remote_addr+":"+'Captcha', json.dumps(code), expiry=180)
    

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
    while True:
        try:
            # origin = await readjson(os.path.join(pydith, 'data.json'))
            # pool = await AsyncMysqlPool.initialize_pool(
            #     origin['mysqlHost'], int(origin['mysqlPort']), origin['mysqlUser'], origin['mysqlPassword'], origin['mysqlDataBase'])
            
            users = await pool.getAllrow('x_users')

            for item in users:
                item.pop('base_path')
                item['init']=True
                if item['username'] == 'guest':
                    item['showViewer']=True
                else:
                    item['showViewer']=False
            
                await upRegister(item)
            break
        except Exception as e:
            await asyncio.sleep(5)
            print(e)
            return False


# async def echo(websocket, path):
#     async for message in websocket:
#         print(f"收到消息: {message}")
#         await websocket.send(f"服务器回复: {message}")

def websocket_server():
    loop = asyncio.new_event_loop()  
    asyncio.set_event_loop(loop)  

    start_server = websockets.serve(orc, "0.0.0.0", 5001)
    loop.run_until_complete(start_server)
    loop.run_forever()

    
if __name__ == '__main__':
  
    websocket_thread = threading.Thread(target=websocket_server)
    websocket_thread.start()
    app.run(host='127.0.0.1', port=5000, debug=True)


