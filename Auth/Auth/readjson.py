import json
import aiofiles

async def read_json(filename, mode='r', encoding='utf-8'):
    async with aiofiles.open(filename, mode=mode, encoding=encoding) as file:
        data = await file.read()
        json_data = json.loads(data)
        return json_data