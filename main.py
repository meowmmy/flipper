import asyncio
import time

import aiohttp

import api_manager
import auctions
import output


# https://moulberry.codes/auction_averages_lbin/auctionLast.json (not sure wat, mite be useful)
# https://moulberry.codes/auction_averages_lbin/1day.json (lbin 1 day averages)
# https://moulberry.codes/auction_averages/3day.json (use for sales)
# https://moulberry.codes/lowestbin.json (current lbin)


async def async_print(*args, **kwargs):
    print(*args, **kwargs)


async def main():
    last_updated = None

    async with aiohttp.ClientSession() as session:
        while True:
            response = await api_manager.fetch_hyp_auctions(session)
            current_last_updated = response.get("lastUpdated")

            if current_last_updated != last_updated:
                present_time = int(time.time() * 1000)
                auction_items = await auctions.process_auctions(response.get("auctions", []), present_time)
                if auction_items:
                    await asyncio.gather(
                        output.write_to_file(auction_items),
                        async_print(
                            "----------------------------------------\n"
                            f"Present Unix Time: {present_time}\n"
                            f"Number of Auctions Added: {len(auction_items)}\n"
                            f"Start Times: {[auction['start'] for auction in auction_items]}\n"
                            f"Data written to auction_data.json\n"
                            "----------------------------------------\n"
                        )
                    )
                    last_updated = current_last_updated
                else:
                    print("No eligible auctions to save.")
            else:
                print("No new auctions")

            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
