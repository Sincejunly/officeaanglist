from quart import Quart, request, make_response
from itsdangerous import URLSafeSerializer

app = Quart(__name__)
from quart_cors import cors
cors(app, allow_origin="*")
# 用于加密和解密的密钥，请确保保密并不要泄露
SECRET_KEY = 'your_secret_key_here'

# 创建一个序列化器
serializer = URLSafeSerializer(SECRET_KEY)

# 持久化 Cookie 的过期时间（30天）
EXPIRATION_DAYS = 30


@app.route('/')
async def index():
    # 从请求中获取 cookie
    encrypted_cookie = request.cookies.get('my_cookie')
    if encrypted_cookie:
        try:
            # 解密 cookie 中的信息
            decrypted_data = serializer.loads(encrypted_cookie)
        except Exception as e:
            return f"Error decoding cookie: {str(e)}"
        else:
            return f"Decrypted data from cookie: {decrypted_data}"
    else:
        return "No encrypted cookie found."


@app.route('/set_cookie')
async def set_cookie():
    # 要存储的信息
    data_to_store = {'username': 'john_doe', 'role': 'admin'}

    # 加密信息并创建 cookie
    encrypted_cookie = serializer.dumps(data_to_store)
    response = make_response("Cookie has been set.")
    response.headers["Set-Cookie"] = f"my_cookie={encrypted_cookie}; Max-Age={EXPIRATION_DAYS * 24 * 60 * 60}; Path=/"

    return response


if __name__ == '__main__':
    app.run()
