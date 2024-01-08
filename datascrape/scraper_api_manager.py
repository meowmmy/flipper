async def fetch_hyp_auctions(session):
    async with session.get(
            "https://api.hypixel.net/skyblock/auctions") as response:
        return await response.json()


async def fetch_average_bin(session):
    async with session.get(
            "https://moulberry.codes/auction_averages/3day.json") as response:
        return await response.json()


async def fetch_hyp_auctions_page(session, page):
    url = f"https://api.hypixel.net/skyblock/auctions?page={page}"
    async with session.get(url) as response:
        return await response.json()

