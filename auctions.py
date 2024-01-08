import base64
import io
import json

import nbt.nbt


async def process_auctions(auctions, present_time):
    excluded_tags = ["rune",
                     "travel_scroll"]  # very small filter
    decoded_auctions = []

    for auction in auctions:
        if auction.get("bin") and present_time - 59000 <= auction.get("start"):
            item_tag = await decode_item(auction["item_bytes"])

            if all(excluded_tag.lower() not in item_tag.lower()
                   for excluded_tag in excluded_tags):
                decoded_auctions.append({
                    "item_name": auction["item_name"],
                    "starting_bid": auction["starting_bid"],
                    "start": auction["start"],
                    "item_tag": item_tag,
                    "category": auction["category"],
                    "rarity": auction["tier"]
                })
    return decoded_auctions




async def decode_item(raw_data):
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
    pet_info = extra_attributes.get('attributes')
    if pet_info:
        try:
            pet_attributes = extract_attributes(pet_info)
            return f"{id_value}+{'+'.join(pet_attributes)}"
        except json.JSONDecodeError:
            pass
    return id_value
