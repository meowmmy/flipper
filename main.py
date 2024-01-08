import aiohttp
import asyncio
import json
import time
import aiofiles
import io
import base64
import nbt.nbt


#https://moulberry.codes/auction_averages_lbin/auctionLast.json (not sure wat, mite be useful)
#https://moulberry.codes/auction_averages_lbin/1day.json (lbin 1 day averages)
#https://moulberry.codes/auction_averages/3day.json (use for sales)
#https://moulberry.codes/lowestbin.json (current lbin)
async def fetch_auction_page(session):
  async with session.get(
      "https://api.hypixel.net/skyblock/auctions") as response:
    return await response.json()


async def process_auctions(auctions, present_time):
  decoded_auctions = []

  for auction in auctions:
    if auction.get("bin") and present_time - 59000 <= auction.get("start"):
      item_tag = await decodeItem(auction["item_bytes"])

      decoded_auctions.append({
          "item_name": auction["item_name"],
          "starting_bid": auction["starting_bid"],
          "start": auction["start"],
          "item_tag": item_tag,
          "category": auction["category"],
          "rarity": auction["tier"]
      })

  return decoded_auctions


async def write_to_file(data):
  async with aiofiles.open("auction_data.json", "w") as json_file:
    await json_file.write(json.dumps(data, indent=2))


async def print_details(present_time, auction_items):
  print(
      f"Present Unix Time: {present_time}\nNumber of Auctions Added: {len(auction_items)}\nStart Times: {[auction['start'] for auction in auction_items]}\nData written to auction_data.json"
  )


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
  pet_info = extra_attributes.get('attributes')
  if pet_info:
    try:
      attributes = extract_attributes(pet_info)
      return f"{id_value}+{'+'.join(attributes)}"
    except json.JSONDecodeError:
      pass
  return id_value


async def main():
  last_updated = None

  async with aiohttp.ClientSession() as session:
    while True:
      response = await fetch_auction_page(session)
      current_last_updated = response.get("lastUpdated")

      if current_last_updated != last_updated:
        present_time = int(time.time() * 1000)
        auction_items = await process_auctions(response.get("auctions", []),
                                               present_time)

        if auction_items:
          await asyncio.gather(write_to_file(auction_items),
                               print_details(present_time, auction_items))
          last_updated = current_last_updated
        else:
          print("No eligible auctions to save.")
      else:
        print("No new auctions")

      await asyncio.sleep(1)


if __name__ == "__main__":
  asyncio.run(main())
