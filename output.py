import json

import aiofiles


async def write_to_file(data, file):
    async with aiofiles.open(file, "w") as json_file:
        await json_file.write(json.dumps(data, indent=2))

async def append_to_file(data, file):
    async with aiofiles.open(file, "a") as json_file:
        await json_file.write(json.dumps(data, indent=2))