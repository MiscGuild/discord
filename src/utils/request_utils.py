import random
import re
from __main__ import bot
from io import BytesIO

import aiohttp
import discord

from src.utils.consts import config, error_channel_id


async def get_hyapi_key():
    return random.choice(config["api_keys"])


# Base JSON-getter for all JSON based requests. Catches Invalid API Key errors
async def get_json_response(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            resp = await resp.json(content_type=None)
            await session.close()

    if not resp:
        return None

    # Check for invalid API keys
    if "cause" in resp and resp["cause"] == "Invalid API key":
        await bot.get_channel(error_channel_id).send(
            f"WARNING: The API key {re.search(r'(?<=key=)(.*?)(?=&)', url).group(0)} is invalid!")

    # Return JSON response
    return resp


async def get_mojang_profile(name: str):
    resp = await get_json_response(f"https://api.mojang.com/users/profiles/minecraft/{name}")

    # If player and request is valid
    if resp and ("errorMessage" not in resp) and ("name" in resp):
        return resp["name"], resp["id"]

    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/player?key={api_key}&name={name}")
    if resp and 'player' in resp and resp['player']:
        return resp['player']['displayname'], resp['player']['uuid']

    # Player does not exist
    return None, None


async def get_hypixel_player(name: str = None, uuid: str = None):
    api_key = await get_hyapi_key()
    if name:
        resp = await get_json_response(f"https://api.hypixel.net/player?key={api_key}&name={name}")
    else:
        resp = await get_json_response(f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}")

    # Player doesn't exist
    if "player" not in resp or not resp["player"]:
        return None

    # Player exists
    return resp["player"]


async def get_name_by_uuid(uuid: str):
    i = 0
    while i < 5:
        i += 1
        resp = await get_json_response(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        # Player does not exist
        if not resp:
            continue
        if "name" not in resp:
            continue
        return resp["name"]
    api_key = await get_hyapi_key()
    # If the Mojang API fails to return a name, the bot checks using the hypixel API
    resp = await get_json_response(f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}")
    if "player" not in resp:
        return None
    return resp['player']['displayname']


def session_get_name_by_uuid(session, uuid):
    with session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as resp:
        data = resp.json()

        if resp.status_code != 200:
            return None
        return data["name"]


async def get_player_guild(uuid):
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&player={uuid}")

    # Player is not in a guild
    if "guild" not in resp or not resp["guild"]:
        return None

    # Player is in a guild
    return resp["guild"]


async def get_guild_by_name(name):
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&name={name}")

    if not resp:
        return None

    # Player is not in a guild
    if "guild" not in resp or not resp["guild"]:
        return None

    # Player is in a guild
    return resp["guild"]


async def get_guild_uuids(guild_name: str):
    resp = await get_guild_by_name(guild_name)
    if not resp:
        return None
    return [member["uuid"] for member in resp["members"]]


async def get_gtag(name):
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&name={name}")

    if len(resp["guild"]) < 2:
        return (" ")
    if not resp["guild"]["tag"]:
        return (" ")
    gtag = resp["guild"]["tag"]
    return (f"[{gtag}]")


async def get_jpg_file(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            resp = BytesIO(await resp.read())
            await session.close()
    return discord.File(resp, "image.jpg")


async def get_rank(uuid):
    player = await get_hypixel_player(uuid=uuid)
    if player is None:
        return None
    if "newPackageRank" in player:
        rank = (player["newPackageRank"])
        if rank == 'MVP_PLUS':
            if "monthlyPackageRank" in player:
                mvp_plus_plus = (player["monthlyPackageRank"])
                if mvp_plus_plus == "NONE":
                    return '[MVP+]'
                return "[MVP++]"
            return "[MVP+]"
        if rank == 'MVP':
            return '[MVP]'
        if rank == 'VIP_PLUS':
            return 'VIP+'
        if rank == 'VIP':
            return '[VIP]'

    return None
