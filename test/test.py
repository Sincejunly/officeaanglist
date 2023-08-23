import io
import sys
from quart import Quart, websocket
import asyncio

app = Quart(__name__)

async def read_stream_and_display(stream, display):
    """Read from stream line by line until EOF, display, and capture the lines."""
    output = []
    while True:
        line = await stream.readline()
        #line = await stream.read(1)
        if not line:
            break
        output.append(line)
        display(line)
        await websocket.send(line)
    return b''.join(output)

async def run_command_as_string(command):
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.gather(
            read_stream_and_display(process.stdout, sys.stdout.buffer.write),
            read_stream_and_display(process.stderr, sys.stderr.buffer.write),
        )
    except Exception:
        process.kill()
        raise
    finally:
        rc = await process.wait()

    return rc, stdout, stderr

@app.websocket('/run_command')
async def run_command():
    try:
        cmd = "pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117"
        print(await websocket.receive_json())
        await run_command_as_string(cmd)

        await websocket.close()
    except Exception as e:
        await websocket.send(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    # import hypercorn.asyncio
    # from hypercorn.config import Config

    # config = Config()
    # config.bind = ["0.0.0.0:8765"]
    # asyncio.run(hypercorn.asyncio.serve(app, config))
    app.run(host='127.0.0.1', port=8765, debug=True)
