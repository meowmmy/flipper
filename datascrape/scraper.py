import asyncio
import time
import time

import aiohttp

import scraper_api_manager
import scraper_ah_data_processor
import scraper_output


# Grabs all auctions of items over 1 mil in price, saves them and then continues to grab new auctions while running



async def async_print(*args, **kwargs):
    print(*args, **kwargs)

#todo: on fresh startup only grab auctions that were put up in between the last time the scraper was run and now
async def main():
    last_updated = None
    #scraper_output.clear_files()
    async with aiohttp.ClientSession() as session:
        response = await scraper_api_manager.fetch_hyp_auctions(session)
        bins = await scraper_ah_data_processor.scrape_all_bins(response.get("auctions", []))
        await scraper_output.write_to_file(bins, "bins.json")
        await async_print(f"found {bins.__sizeof__()} auctions matching parameters")
        last_updated = response.get("lastUpdated")
        await asyncio.sleep(int((last_updated / 1000) + 5 - time.time()))
        #does not work to get new bins, TODO: fix
        while True:
            while True:
                response = await scraper_api_manager.fetch_hyp_auctions(session)
                if response.get("lastUpdated") != last_updated:
                    new_bins = await scraper_ah_data_processor.get_new_bins(response.get("auctions"), int(time.time() * 1000))
                    bins.append(new_bins)
                    await scraper_output.write_to_file(bins, "bins.json")
                    await async_print(f"found {new_bins.__sizeof__()} new auctions matching parameters")
                    last_updated = response.get("lastUpdated")
                    break
                await asyncio.sleep(1)
            await asyncio.sleep(50)




'''
async def main():

    last_updated = None
    output.clear_files()
    async with aiohttp.ClientSession() as session:



        while True:
            response = await api_manager.fetch_hyp_auctions(session)
            current_last_updated = response.get("lastUpdated")

            if current_last_updated != last_updated:
                present_time = int(time.time() * 1000)
                new_bins = await ah_data_processor.get_new_bins(response.get("auctions", []), present_time)
                if new_bins:
                    await asyncio.gather(
                        output.write_to_file(new_bins, "auction_data.json"),
                        async_print(
                            "----------------------------------------\n"
                            f"Present Unix Time: {present_time}\n"
                            f"Number of Auctions Added: {len(new_bins)}\n"
                            f"Start Times: {[auction['start'] for auction in new_bins]}\n"
                            f"Data written to auction_data.json\n"
                            "----------------------------------------\n"
                        )
                    )
                    last_updated = current_last_updated
                else:
                    print("No eligible auctions to save.")
            await asyncio.sleep(1)
'''

if __name__ == "__main__":
    asyncio.run(main())
