from quart import Quart
from quart_cors import cors
from quart.static import StaticFiles
from tusserver.quart import create_api_router

app = Quart(__name__)
app = cors(app, allow_origin='*')

app.static('/static', './static')

def on_upload_complete(file_path: str):
    print('上传完成')
    print(file_path)

app.register_blueprint(
    create_api_router(
        files_dir='/tmp/different_dir',  # 可选
        location='http://127.0.0.1:5000/files',  # 可选
        max_size=128849018880,  # 可选
        on_upload_complete=on_upload_complete  # 可选
    ),
    url_prefix='/files',
)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
