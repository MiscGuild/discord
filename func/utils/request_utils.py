import aiohttp
import toml
import random

api_keys = toml.load("config.toml")["hypixel"]["api_keys"]


# Returns a random Hypixel API key for requests
async def get_hyapi_key():
    return random.choice(api_keys)


# Returns the Mojang profile of a player
async def get_mojang_profile(name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
            resp = await resp.json(content_type=None)
            await session.close()

    # If player and request is valid
    if resp != None and "error" not in resp:
        return resp["name"], resp["id"]
    
    # Player does not exist
    return None, None


# Returns a player's guild if they're in one
async def get_player_guild(uuid):
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


# Returns the tag of a given guild
async def get_gtag(name):
    api_key = await get_hyapi_key()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/guild?key={api_key}&name={name}") as resp:
            resp = await resp.json(content_type=None)
            await session.close()

    if len(resp["guild"]) < 2:
        return (" ")
    if resp["guild"]["tag"] is None:
        return (" ")
    else:
        gtag = resp["guild"]["tag"]
        return (f"[{gtag}]")