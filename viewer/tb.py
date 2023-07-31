import io
import json
import os
import random
import string
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
from database_utils import AsyncMysqlPool, readjson, readjson_sync


tracemalloc.start()
pydith = os.path.dirname(os.path.realpath(__file__))

auth_manager = QuartAuth()
userEditFile = {
}
CaptchaPrefix = 'officeaanglist:Captcha:'
def create_app():
    origin = readjson_sync(os.path.join(pydith, 'data.json'))
    app = Quart(__name__, template_folder='auth')
    app.secret_key = "QQ943384135"
    app.config['MYSQL_HOST'] = origin['mysqlHost']
    app.config['MYSQL_USER'] = origin['mysqlUser']
    app.config['MYSQL_PASSWORD'] = origin['mysqlPassword']
    app.config['MYSQL_DB'] = origin['mysqldataBase']
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PROTECTION'] = True
    auth_manager.init_app(app)
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
            或者在宿主机中执行<code>sudo docker exec officeaanglist init.py -d {}</code></p>
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
        int(origin['mysqlPort']), origin['mysqlPort'], origin['mysqlUser'], origin['mysqlPassword'], origin['mysqldataBase'])
    
    domains = await pool.getAllrow('x_domain')

    domains = await getAlltype(domains,'Domain','believe')

    app = cors(app, allow_origin=domains)

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
    else:
        user = await pool.getAllrow(userU['table'])
    
    if user:
        
        return jsonify(user)
    
    return jsonify(user)

@app.route('/AListPath', methods=['GET', 'POST'])
async def AListPath():
    global userEditFile
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)    
    userU = await request.get_json()
    if not userU:
        return jsonify({'Error':"not json"})
    
    userEditFile.setdefault(userU['username'],userU['AListPath'])

    return jsonify({'farewell':"ok"})


async def download_file(url, path_for_save):
    try:
        async with request.client.get(url) as response:
            if response.status == 200:
                with open(path_for_save, "wb") as file:
                    while True:
                        chunk = await response.receive(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                return True
            else:
                return False
    except Exception:
        return False


    
@app.route('/save', methods=['GET', 'POST'])
async def save():
    global userEditFile
    data = await request.get_json()

    if data.get("status") == 2:
        downloadUri = data.get("url")
        path_for_save = userEditFile['users']  # 替换为实际保存路径
        userEditFile.pop('users')
        if await download_file(downloadUri, path_for_save):
            return jsonify({"error": 0})
        else:
            return "Bad Response", 500
    else:
        return "Bad Request", 400
    

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
        


    return jsonify({'farewell':"ok"})


@app.route('/update', methods=['GET', 'POST'])
@login_required
async def update():
    # if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
    #     return html_message.format(request.remote_addr)
    userU = await request.get_json()
    
    if not userU:
        return jsonify({'Error':"not json"})
    
    await pool.update_value(userU['table'], userU['valueName'], userU['value'], userU['columnName'], userU['columnValue']) 

    return jsonify({'farewell':"ok"})

@app.route('/check', methods=['GET', 'POST'])
async def index():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)    
    if await current_user.is_authenticated:
        user = await pool.get_row_by_value('x_user','`id`',current_user._auth_id)
        
        if isinstance(user, dict):
            if 'password' in user:
                user.pop('password')
        else:
            user = {}
        user['empty'] = True
        user['farewell'] = 'ok'
        return jsonify(user)
        #return redirect('/AriaNg')
    
    return jsonify({
        'empty':await pool.is_table_empty('x_user'),
        'farewell':'ok'
        })


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
        
        hashed_password = hashpw(userU['password'].encode(), gensalt()).decode()
        

        #update_data = [('username', 'password', 'type'), (userU['username'], hashed_password, userU['type'])]

        if await pool.is_table_empty('x_user'):
            update_data = [('id', 'username', 'password', 'type'), ('1', userU['username'], hashed_password, 'believe')]
   
            await pool.update('x_user', update_data)
        elif 'reset' in userU:
            update_data = [('id', 'username', 'password', 'type'), ('1', userU['username'], hashed_password, 'believe')]
            await pool.update('x_user', update_data, overwrite=True)
        else:
            update_data = [('username', 'password', 'type'), (userU['username'], hashed_password, userU['type'])]
            await pool.update('x_user', update_data)
                
        user = await pool.get_row_by_value('x_user','username',userU['username'])

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
    return jsonify(hashed_password)

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
                if user['type'] == 'distrust':
                    return jsonify({'Error':"你还没有通过管理员的审批，请联系管理员"})
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


@app.route('/AriaNg/', defaults={'path': 'index.html'}, methods=['GET', 'POST'])
@app.route('/AriaNg/<path:path>', methods=['GET', 'POST'])
async def serve_ariang(path):
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr) 
    if await current_user.is_authenticated:
        ariang_path = 'AriaNg-1.3.6'
        return await send_from_directory(ariang_path,path)
    else:
        return redirect('/viewer/')
    
@app.route('/aria2/jsonrpc', methods=['GET', 'POST'])
async def proxy_aria2_jsonrpc():
    if request.remote_addr in await getAlltype(await pool.getAllrow('x_domain'),'Domain','distrust'):
        return html_message.format(request.remote_addr)    
    if not await current_user.is_authenticated:
        return redirect('/viewer/')
    # Get the request data from the client
    data = await request.get_data()

    # Forward the request to the backend server (Aria2 in this case)
    import httpx
    response = await httpx.post('http://127.0.0.1:6800'+'/aria2/jsonrpc', data=data)

    # Create a response with the data from the backend server
    headers = [(key.encode(), value.encode()) for key, value in response.headers.items()]
    return Response(response.content, status_code=response.status_code, headers=headers)

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

if __name__ == '__main__':
    #asyncio.run()
    app.run(host='127.0.0.1', port=5000, debug=True)


