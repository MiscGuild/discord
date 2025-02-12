import asyncio
import random
import re
from __main__ import bot
from functools import wraps
from io import BytesIO
from typing import Tuple, List, Callable, Any

import aiohttp
import discord
import requests

from src.utils.consts import config, error_channel_id
from src.utils.db_utils import get_db_uuid_username, check_and_update_username


def async_retry(max_attempts: int = 5, delay: float = 0.5):
    """Decorator to retry an async function on failure."""

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    if result:
                        return result
                except Exception as e:
                    pass
                if attempt < max_attempts:
                    await asyncio.sleep(delay)

            return None

        return wrapper

    return decorator



async def get_hyapi_key() -> str:
    return random.choice(config["api_keys"])


async def update_usernames(uuid: str, username: str) -> None:
    db_username, uuid = await get_db_uuid_username(uuid=uuid)
    if db_username is None:
        return
    elif db_username != username:
        await check_and_update_username(uuid, username)


# Base JSON-getter for all JSON based requests. Catches Invalid API Key errors
async def get_json_response(url: str) -> dict | None:
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


@async_retry()
async def get_mojang_profile_from_name(name: str) -> Tuple[str, str] | Tuple[None, None]:
    url = f"https://api.mojang.com/users/profiles/minecraft/{name}"
    resp = await get_json_response(url)

    return resp["name"], resp["id"] if resp and "name" in resp else None


async def get_uuid_by_name(name: str) -> Tuple[str, str] | Tuple[None, None]:
    username, uuid = await get_mojang_profile_from_name(name)
    if username and uuid:
        await update_usernames(uuid=uuid, username=username)
        return username, uuid

    resp = await get_hypixel_player(name=name)
    if resp and "uuid" in resp:
        await update_usernames(uuid=resp["uuid"], username=resp["displayname"])
        return resp["displayname"], resp["uuid"]

    return None, None


@async_retry()
async def get_mojang_profile_from_uuid(uuid: str) -> Tuple[str, str] | Tuple[None, None]:
    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    resp = await get_json_response(url)
    return resp["name"], uuid if resp and "name" in resp else None


async def get_name_by_uuid(uuid: str) -> str | None:
    username = await get_db_username_from_uuid(uuid)
    if username:
        return username

    username, uuid = await get_mojang_profile_from_uuid(uuid)
    if username and uuid:
        await update_usernames(uuid=uuid, username=username)
        return username

    resp = await get_hypixel_player(uuid=uuid)
    if resp and "displayname" in resp:
        await update_usernames(uuid=uuid, username=resp["displayname"])
        return resp["displayname"]

    return None


async def get_hypixel_player(name: str = None, uuid: str = None) -> dict | None:
    api_key = await get_hyapi_key()
    if name:
        resp = await get_json_response(f"https://api.hypixel.net/player?key={api_key}&name={name}")
    else:
        resp = await get_json_response(f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}")

    if not resp:
        return None
    # Player doesn't exist
    if "player" not in resp or not resp["player"]:
        return None

    # Player exists
    await update_usernames(uuid=resp["player"]["uuid"], username=resp["player"]["displayname"])
    return resp["player"]


def session_get_name_by_uuid(session: requests.Session, uuid: str) -> str | None:
    with session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as resp:
        data = resp.json()

        if resp.status_code != 200:
            return None
        return data["name"]


async def get_player_guild(uuid: str) -> dict | None:
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&player={uuid}")

    # Player is not in a guild
    if "guild" not in resp or not resp["guild"]:
        return None

    # Player is in a guild
    return resp["guild"]


async def get_guild_by_name(name: str) -> dict | None:
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&name={name}")

    if not resp:
        return None

    # Player is not in a guild
    if "guild" not in resp or not resp["guild"]:
        return None

    # Player is in a guild
    return resp["guild"]


async def get_guild_uuids(guild_name: str) -> List[str] | None:
    resp = await get_guild_by_name(guild_name)
    if not resp:
        return None
    return [member["uuid"] for member in resp["members"]]


async def get_gtag(name: str) -> str:
    api_key = await get_hyapi_key()
    resp = await get_json_response(f"https://api.hypixel.net/guild?key={api_key}&name={name}")

    if len(resp["guild"]) < 2:
        return " "
    if not resp["guild"]["tag"]:
        return " "
    gtag = resp["guild"]["tag"]
    return f"[{gtag}]"


async def get_jpg_file(url: str) -> discord.File | None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            resp = BytesIO(await resp.read())
            await session.close()
    return discord.File(resp, "image.jpg")


async def get_rank(uuid: str) -> str | None:
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
