import json

import aiofiles


async def write_to_file(data):
    async with aiofiles.open("auction_data.json", "w") as json_file:
        await json_file.write(json.dumps(data, indent=2))