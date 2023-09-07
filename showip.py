# app.py
from quart import Quart, request

app = Quart(__name__)
app.reverse_proxy = True

@app.route('/check')
async def get_visitor_info():
    user_agent = request.headers.get('User-Agent')
    client_ip = request.remote_addr
    return f'User-Agent: {user_agent}, Client IP: {client_ip}'

if __name__ == '__main__':
    app.run()

