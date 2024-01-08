import base64
import io
import json


import nbt
import nbt_handler


# auctions is an array with elements auction, auction is a dictionary with key item_bytes being the nbt data


def raw_decoded_auction(auction):
    decoded_nbt = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(auction["item_bytes"])))
    decoded_nbt_data = nbt_handler.nbt_to_python(decoded_nbt)
    rawdecodedauction = {field: auction[field] for field in auction if field != "item_bytes"}
    rawdecodedauction["item_bytes"] = decoded_nbt_data
    return rawdecodedauction


async def get_new_bins(auctions, present_time):
    excluded_tags = []  # ["rune",
    # "travel_scroll"]  # very small filter
    decoded_auctions = []
    raw_decoded_auctions = []
    for auction in auctions:
        if auction.get("bin") and present_time - 59000 <= auction.get("start") and auction.get('starting_bid') >= 1000000:
            item_tag = await decode_item(auction["item_bytes"])
            raw_decoded_auctions.append(raw_decoded_auction(auction))
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
    return raw_decoded_auctions


async def process_auctions(auctions, present_time):
    raw_decoded_auctions = []
    for auction in auctions:
        if auction.get("bin") and present_time - 59000 <= auction.get("start") and auction.get('starting_bid') >= 1000000:
            item_tag = await decode_item(auction["item_bytes"])
            raw_decoded_auctions.append(raw_decoded_auction(auction))
    return raw_decoded_auctions


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
