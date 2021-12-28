from func.utils.requests.get_hyapi_key import get_hyapi_key
import aiohttp

async def get_gtag(name):
    api = await get_hyapi_key()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/guild?key={api}&name={name}") as resp:
            req = await resp.json(content_type=None)
            await session.close()
    if len(req["guild"]) < 2:
        return (" ")
    if req["guild"]["tag"] is None:
        return (" ")
    else:
        gtag = req["guild"]["tag"]
        return (f"[{gtag}]")