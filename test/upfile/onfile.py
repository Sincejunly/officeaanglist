import os
import quart
import aiofiles
from quart import Quart, request, jsonify
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="*")  # 允许任何来源的跨域请求

@app.route('/')
async def index():
    return await quart.render_template('index.html')

@app.route('/upload', methods=['POST'])
async def upload():
    form_data = await request.files  # 使用await来获取文件对象
    file = form_data.get('file')

    if file is None:
        return jsonify({'error': 'No file part'})

    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    print(file.filename)
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    async def save_file():
        async with aiofiles.open(file_path, 'wb') as f:
            while True:
                chunk = file.read(1024)  # 读取文件块
                if not chunk:
                    break
                await f.write(chunk)

    await save_file()  # 异步保存文件

    return jsonify({'message': 'File uploaded successfully'})

if __name__ == '__main__':
    app.run()
