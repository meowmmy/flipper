async def fetch_hyp_auctions(session):
    async with session.get(
            "https://api.hypixel.net/skyblock/auctions") as response:
        return await response.json()
