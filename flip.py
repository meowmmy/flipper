import json
import requests
from datetime import datetime

lbinavg = requests.get("https://moulberry.codes/auction_averages_lbin/3day.json").json()
webhook_url = "https://discord.com/api/webhooks/1192968012010102864/mJqbylWQujqGs30tzRImKlsNRZ3H55C-iX0Br2TnRtaS4DL0_fuSw4wGgqZoF7bSFyMd"

with open("auction_data.json", 'r') as file:
    auction_data = json.load(file)
with open("bazaar_pricing.json", 'r') as file:
    bazaar_pricing_data = json.load(file)

reforge_prices = {
    "OVERGROWN_GRASS": 0.0,
    "PRECURSOR_GEAR": 0.0,
    "TOIL_LOG": 0.0,
    "JADERALD": 0.0,
    "BURROWING_SPORES": 0.0,
    "DEEP_SEA_ORB": 0.0,
    "GIANT_TOOTH": 0.0,
    "DRAGON_HORN": 0.0,
}
name_mapping = {
    "mossy": "OVERGROWN_GRASS",
    "ancient": "PRECURSOR_GEAR",
    "toil": "TOIL_LOG",
    "jaded": "JADERALD",
    "rooted": "BURROWING_SPORES",
    "submerged": "DEEP_SEA_ORB",
    "giant": "GIANT_TOOTH",
    "renowned": "DRAGON_HORN",
}

for code_name, json_name in name_mapping.items():
    price = bazaar_pricing_data["reforges"].get(json_name, {}).get("price", 0.0)
    reforge_prices[code_name] = price

basePrice = [(item["item_tag"], lbinavg.get(item["item_tag"], 0), item["reforge"]) for item in auction_data]
bin_values = [item["starting_bid"] for item in auction_data]
itemName = [item["item_name"] for item in auction_data]
rarity = [item["rarity"] for item in auction_data]
uuid = [item["uuid"] for item in auction_data]
start = [item["start"] for item in auction_data]
recomb = [item.get("recomb") if item.get("recomb") != 'None' else '0' for item in auction_data]
hpb = [item.get("hpb") if item.get("hpb") != 'None' else '0' for item in auction_data]

for (item_tag, basePrice_text, reforge), starting_bid, recomb_list, hpb_list, itemName, rarity, uuid, start in zip(basePrice, bin_values, recomb, hpb, itemName, rarity, uuid, start):
    extras = 0
    reforge_price = reforge_prices.get(reforge, 0.0)
    if recomb_list is not None and recomb_list == '1':
        recomb_list = 4000000 #recomb value
    if hpb_list is not None and int(hpb_list) > 10:
        hpb_list = int(hpb_list) + 350000 + (int(hpb_list) - 10) * 700000 #fuming value
    else:
        hpb_list = int(hpb_list) * 10000 #hpb value
    extras = reforge_price + (float(recomb_list) if recomb_list else 0) + (float(hpb_list) if hpb_list else 0) #sum of all the extras
    profit = (basePrice_text + extras) - starting_bid - (basePrice_text *.05)
    goal = (basePrice_text + extras) - (basePrice_text *.05)
    start_time_seconds = int(start) / 1000
    start_time_readable = datetime.utcfromtimestamp(start_time_seconds).strftime('%Y-%m-%d %H:%M:%S')
    profit_formatted = '{:,}'.format(int(profit))
    starting_bid_formatted = '{:,}'.format(starting_bid)
    goal_formatted = '{:,}'.format(int(goal))
    message = {
        "content": "",
        "embeds": [
            {
                "title": f"{rarity} {itemName}",
                "description": f"**Profit:** {profit_formatted}\n**Buy Price:** {starting_bid_formatted}\n**Sell Goal:** {goal_formatted}",
                "author": {
                    "name": "@meowmmy",
                    "icon_url": "https://i.imgur.com/2kgwmlZ.png"
                },
                "color": 0x40E0D0,
                "footer": {
                    "text": f"Listed: {start_time_readable} | @glitterow"
                },
                "fields": [
                    {
                        "name": "View Auction",
                        "value": f"`/viewauction {uuid}`",
                        "inline": True
                    }
                ]
            }
        ],
        "username": "meowmmy"
    }
    if int(profit) > 400000:
        response = requests.post(webhook_url, json=message)
    else:
        pass
print("Flips sent.")