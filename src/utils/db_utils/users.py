from __main__ import bot
from typing import Tuple

from .connection import select_one, select_all


async def check_and_update_username(uuid: str, username: str) -> None:
    cursor = await bot.db.execute(
        "INSERT OR REPLACE INTO users (uuid, username) VALUES (?, ?)",
        (uuid, username)
    )

    if cursor.rowcount == 0:
        await bot.db.execute(
            "INSERT INTO users (uuid, username) VALUES (?, ?)",
            (uuid, username)
        )

    await bot.db.commit()


async def get_username_from_uuid(uuid: str) -> Tuple[str, str] | Tuple[None, str] | Tuple[None, None]:
    if uuid == "0" or not uuid:
        return None, None
    res = await select_one("SELECT username from users WHERE uuid = (?)", (uuid,))
    if res:
        return res[0], uuid
    return None, uuid


async def get_all_usernames() -> list:
    rows = await select_all("SELECT uuid, username FROM users")
    return rows


async def get_uuid_from_username(username: str) -> Tuple[str, str] | Tuple[str, None]:
    res = await select_one("SELECT uuid from users WHERE username = (?)", (username,))
    if res:
        uuid = res[0]
        if uuid == "0":
            return username, None
        return username, res[0]
    return username, None
