import requests, json, os
from urllib import parse

url = 'https://office.homura.top:82/AList/api'
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
Authorization = ''

headers = {
    'UserAgent': UserAgent,
    'Authorization': Authorization
}
ct_json = {
    'Content-Type': 'application/json'
}

# 获取当前用户信息（目录、权限等）
def getMyProfile():
    try:
        return json.loads(requests.get(f'{url}/me', headers=headers).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 通过用户名、密码获取 token
def getToken(username, password):
    data = {
        'username': username,
        'password': password
    }
    try:
        return json.loads(requests.post(f'{url}/auth/login', data=json.dumps(data), headers={'Content-Type': 'application/json'}).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 获取一个目录下的对象
def getObjectList(path, password = ''):
    data = {
        # 'page': 1,
        'password': password,
        'path': path,
        # 'per_page': 100,
        # 'refresh': False
    }
    try:
        return json.loads(requests.post(f'{url}/fs/list', data=data, headers=headers).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 获取一个对象的信息
def getObjectInfo(path, password = ''):
    data = {
        'password': password,
        'path': path
    }
    try:
        return json.loads(requests.post(f'{url}/fs/get', data=data, headers=headers).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 新建文件夹
def MakeDir(path):
    data = { 'path': path }
    try:
        return json.loads(requests.post(f'{url}/fs/mkdir', data=json.dumps(data), headers=dict(headers, **ct_json)).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 上传文件
def Upload(localPath, remotePath, fileName, password = ''):
    upload_header = {
        'UserAgent': UserAgent,
        'Authorization': Authorization,
        'File-Path': parse.quote(f'{remotePath}/{fileName}'),
        'Password': password,
        'Content-Length': f'{os.path.getsize(localPath)}'
    }
    try:
        return json.loads(requests.put(f'{url}/fs/put', headers=upload_header, data=open(localPath, 'rb').read()).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 删除文件
def Remove(dir, names):
    data = {
        'dir': dir,
        'names': names
    }
    try:
        return json.loads(requests.post(f'{url}/fs/remove', data=json.dumps(data), headers=dict(headers, **ct_json)).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 复制文件
def Copy(srcDir, dstDir, names):
    data = {
        'src_dir': srcDir,
        'dst_dir': dstDir,
        'names': names
    }
    try:
        return json.loads(requests.post(f'{url}/fs/copy', data=json.dumps(data), headers=dict(headers, **ct_json)).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 移动文件
def Move(srcDir, dstDir, names):
    data = {
        'src_dir': srcDir,
        'dst_dir': dstDir,
        'names': names
    }
    try:
        return json.loads(requests.post(f'{url}/fs/move', data=json.dumps(data), headers=dict(headers, **ct_json)).text)
    except Exception as e:
        return {'code': -1, 'message': e}

# 更改文件名
def Rename(path, newName):
    data = {
        'path': path,
        'name': newName
    }
    try:
        return json.loads(requests.post(f'{url}/fs/rename', data=json.dumps(data), headers=dict(headers, **ct_json)).text)
    except Exception as e:
        return {'code': -1, 'message': e}
    
# Authorization = getToken('admin', 'admin')['data']['token']
# print(Upload('./tempCodeRunnerFile.py', '/ALists', 'tempCodeRunnerFile.py', 'admin'))
print(os.environ.get("AListHost"))