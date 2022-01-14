import aiohttp
import discord
from io import BytesIO
import random
import re
import toml

api_keys = toml.load("config.toml")["hypixel"]["api_keys"]


# Returns a random Hypixel API key for requests
async def get_hyapi_key():
    return random.choice(api_keys)

# Base JSON-getter for all JSON based requests. Catches Invalid API Key errors
async def get_json_response(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp = await resp.json(content_type=None)
            await session.close()

    # Check for invalid API keys
    if "cause" in resp and resp["cause"] == "Invalid API key":
        print(f"WARNING: The API key {re.search(r'(?<=key=)(.*?)(?=&)', url).group(0)} is invalid!")

    # Return JSON response
    return resp


# Returns the Mojang profile of a player
async def get_mojang_profile(name: str):
    resp = await get_json_response(f"https://api.mojang.com/users/profiles/minecraft/{name}")

    # If player and request is valid
    if resp and "error" not in resp:
        return resp["name"], resp["id"]
    
    # Player does not exist
    return None, None


# Returns the Mojang profile of a player (including skin)
async def get_name_by_uuid(uuid: str):
    resp = await get_json_response(f"https://api.mojang.com/user/profiles/{uuid}/names")

    # If player and request is valid
    if resp and "error" not in resp:
        return resp[-1]["name"]
    
    # Player does not exist
    return None


# Returns a player's guild if they're in one
async def get_player_guild(uuid):
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&player={uuid}")

    # Player is not in a guild
    if "guild" not in resp or not resp["guild"]:
        return None

    # Player is in a guild
    return resp["guild"]


# Returns guild data by name
async def get_guild_by_name(name):
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&name={name}")

    # Player is not in a guild
    if "guild" not in resp or not resp["guild"]:
        return None

    # Player is in a guild
    return resp["guild"]


# Returns the tag of a given guild
async def get_gtag(name):
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&name={name}")

    if len(resp["guild"]) < 2:
        return (" ")
    if not resp["guild"]["tag"]:
        return (" ")
    else:
        gtag = resp["guild"]["tag"]
        return (f"[{gtag}]")


# Returns Hypixel player data
async def get_hypixel_player(name: str):
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/player?key={api_key}&name={name}")

    # Player doesn't exist
    if "player" not in resp or not resp["player"]:
        return None

    # Player exists
    return resp["player"]


# Returns the value of a given url
async def get_gtop(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp = BytesIO(await resp.read())
            await session.close()
    return discord.File(resp, "gtop.jpg")
