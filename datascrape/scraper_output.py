import json

import aiofiles


import scraper_nbt_handler as nbt


# Custom JSON Encoder
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, nbt.NBTData):
            return str(obj)  # Convert NBTData to string
        return json.JSONEncoder.default(self, obj)

# Updated write_to_file function
async def write_to_file(data, file):
    async with aiofiles.open(file, "w") as json_file:
        await json_file.write(json.dumps(data, indent=2, cls=CustomEncoder))

# Updated append_to_file function
async def append_to_file(data, file):
    async with aiofiles.open(file, "a") as json_file:
        await json_file.writelines(json.dumps(data, indent=2, cls=CustomEncoder))


def clear_files(files):
    for file in files:
        with open(file, "w") as json_file:
            json_file.write("")
