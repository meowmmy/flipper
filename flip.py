import json
import requests

lbinavg = requests.get("https://moulberry.codes/auction_averages_lbin/3day.json").json()

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
    print(f"Reforge: {code_name}, Price: {price}")

basePrice = [(item["item_tag"], lbinavg.get(item["item_tag"], 0), item["reforge"]) for item in auction_data]
bin_values = [item["starting_bid"] for item in auction_data]

for (item_tag, basePrice_text, reforge), starting_bid in zip(basePrice, bin_values):
    extras = reforge_prices.get(reforge, 0.0)
    print(f"Item Tag: {item_tag}, Base Price: {basePrice_text}, Reforge: {reforge}, Extras: {extras}, Starting Bid: {starting_bid}")

    if int(basePrice_text) != 0 and int(basePrice_text) + int(extras) > int(starting_bid):
        print(f"Item Tag: {item_tag}, Value: {basePrice_text}", f"Starting Bid: {starting_bid}")



#def filter():

#print("Items Filtered, Sending to webhook.")

#if __name__ == "__main__":
#filter()
