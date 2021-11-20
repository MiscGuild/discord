import aiohttp

from func.utils.general.requests.get_hyapi_key import get_hyapi_key

async def player_guild(uuid):
    api_key = await get_hyapi_key()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/guild?key={api_key}&player={uuid}") as resp:
            resp = await resp.json()
            await session.close()

    # Player is not in a guild
    if "guild" not in resp or resp["guild"] == None:
        return None

    # Player is in a guild
    return resp
