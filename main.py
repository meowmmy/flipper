import aiohttp
import asyncio
import json
import time
import aiofiles
import io
import base64
import nbt.nbt
import requests

async def fetch_auction_page(session):
    async with session.get("https://api.hypixel.net/skyblock/auctions") as response:
        return await response.json()

async def process_auctions(auctions, present_time):
    decoded_auctions = []
    for auction in auctions:
        if auction.get("bin") and present_time - 60000 <= auction.get("start"):
            decoded_item_info, reforge, enchants = await decodeItem(auction["item_bytes"])
            item_tag = decoded_item_info
            decoded_auction = {
                "item_name": auction["item_name"],
                "starting_bid": auction["starting_bid"],
                "start": auction["start"],
                "item_tag": item_tag,
                "category": auction["category"],
                "rarity": auction["tier"],
                "reforge": str(reforge),
                "enchantments": str(enchants)
            }
            decoded_auctions.append(decoded_auction)
    return decoded_auctions

async def write_to_file(data, filename):
    def convert_to_json_serializable(item):
        if isinstance(item, nbt.nbt.TAG_String):
            return str(item)
        return item

    serializable_data = json.dumps(data, default=convert_to_json_serializable, indent=2, ensure_ascii=False)
    async with aiofiles.open(filename, "w", encoding='utf-8') as json_file:
        await json_file.write(serializable_data)

async def print_details(present_time, auction_items):
    print(f"Present Unix Time: {present_time}\nNumber of Auctions Added: {len(auction_items)}\nStart Times: {[auction['start'] for auction in auction_items]}\nData written to auction_data.json")

async def decodeItem(raw_data):
    def tier_to_numeric(tier):
        tier_mapping = {
            'COMMON': 0,
            'UNCOMMON': 1,
            'RARE': 2,
            'EPIC': 3,
            'LEGENDARY': 4,
            'MYTHIC': 5
        }
        return tier_mapping.get(tier, None)

    def extract_attributes(attributes_compound):
        attributes = []
        for key in attributes_compound:
            attributes.append(f"ATTRIBUTE_{key.upper()}")
        return attributes

    data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(raw_data)))
    first_compound = data['i'][0]
    extra_attributes = first_compound['tag']['ExtraAttributes']
    id_value = extra_attributes['id'].value
    reforge = extra_attributes.get('modifier', None)
    enchants = [
        f"ENCHANTMENT_{key.upper()}_{value}"
        for key, value in extra_attributes.get('enchantments', {}).items()
    ]
    attributes = extra_attributes.get('attributes')
    pet_info = extra_attributes.get('petInfo')
    result = f'{id_value}'
    if attributes:
        try:
            attributes = extract_attributes(attributes)
            result = f"{id_value}+{'+'.join(attributes)}"
        except json.JSONDecodeError:
            pass
    if pet_info:
        try:
            pet_info_dict = json.loads(pet_info.value)
            if 'type' in pet_info_dict and 'tier' in pet_info_dict:
                numeric_tier = tier_to_numeric(pet_info_dict['tier'])
                result = f"{pet_info_dict['type']};{numeric_tier}"
        except json.JSONDecodeError:
            pass
    print("Decoded Item:", result, reforge, enchants)
    return result, reforge, enchants

async def update_bazaar_pricing():
    response = requests.get("https://api.hypixel.net/v2/skyblock/bazaar")
    data = response.json()

    if response.status_code == 200:
        bazaar_pricing = {
            "reforges": {},
            "enchants": {}
        }

        for product_id, product_data in data['products'].items():
            if any(keyword in product_id.lower() for keyword in ["toil_log", "precursor_gear", "giant_tooth", "dragon_horn", "deep_sea_orb", "overgrown_grass", "jaderald", "burrowing_spores"]):
                bazaar_pricing["reforges"][product_id] = {"price": (product_data['quick_status']['sellPrice'] + product_data['quick_status']['buyPrice']) / 2}
            elif "enchantment" in product_id.lower():
                bazaar_pricing["enchants"][product_id] = {"price": (product_data['quick_status']['sellPrice'] + product_data['quick_status']['buyPrice']) / 2}

        await write_to_file(bazaar_pricing, 'bazaar_pricing.json')
        print("Filtered data saved to bazaar_pricing.json")
    else:
        print(f"Error: {data['cause']}")

async def main():
    last_updated = None
    async with aiohttp.ClientSession() as session:
        while True:
            response = await fetch_auction_page(session)
            current_last_updated = response.get("lastUpdated")
            if current_last_updated != last_updated:
                present_time = int(time.time() * 1000)
                auction_items = await process_auctions(response.get("auctions", []), present_time)
                if auction_items:
                    await asyncio.gather(
                        write_to_file(auction_items, 'auction_data.json'),
                        update_bazaar_pricing(),
                        print_details(present_time, auction_items)
                    )
                    last_updated = current_last_updated
                else:
                    print("No eligible auctions to save.")
            else:
                print("No new auctions")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())