async def fetch_hyp_auctions(session):
    async with session.get(
            "https://api.hypixel.net/skyblock/auctions") as response:
        return await response.json()


async def fetch_average_bin(session):
    async with session.get(
            "https://moulberry.codes/auction_averages/3day.json") as response:
        return await response.json()


async def fetch_all_hyp_auctions(session):
    first_page = await fetch_hyp_auctions_page(session, 0)
    total_pages = first_page['totalPages']

    all_auctions = first_page['auctions']

    for page in range(1, total_pages):
        page_data = await fetch_hyp_auctions_page(session, page)
        all_auctions.extend(page_data['auctions'])

    return all_auctions


async def fetch_hyp_auctions_page(session, page):
    url = f"https://api.hypixel.net/skyblock/auctions?page={page}"
    async with session.get(url) as response:
        return await response.json()
