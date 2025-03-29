from __main__ import bot
from typing import Tuple

from .connection import select_one
from .users import check_and_update_username, get_username_from_uuid, get_uuid_from_username


async def get_uuid_from_discord_id(discord_id: int) -> str | None:
    res = await select_one("SELECT uuid from members WHERE discord_id = (?)", (discord_id,))
    if res:
        uuid = res[0]
        if uuid == "0":
            return None
        return uuid


async def get_discord_id_from_uuid(uuid: str) -> int | None:
    if uuid == "0":
        return None
    res = await select_one("SELECT discord_id from members WHERE uuid = (?)", (uuid,))
    return int(res[0]) if res else None


async def insert_new_member(discord_id: int, uuid: str, username: str) -> None:
    await bot.db.execute("INSERT INTO members VALUES (?, ?, ?)", (discord_id, uuid, 1))
    await bot.db.commit()
    await check_and_update_username(uuid, username)


async def update_member(discord_id: int, uuid: str, username: str) -> None:
    discord_record = await select_one("SELECT uuid FROM members WHERE discord_id = ?", (discord_id,))
    existing_uuid_record = await select_one("SELECT discord_id FROM members WHERE uuid = ?", (uuid,))

    if existing_uuid_record and existing_uuid_record[0] != "0":
        existing_discord_id = existing_uuid_record[0]
        if discord_id != existing_discord_id:
            await bot.db.execute("UPDATE members SET uuid = '0' WHERE uuid = ?", (uuid,))
            await bot.db.commit()
            discord_record = await select_one("SELECT uuid FROM members WHERE discord_id = ?", (discord_id,))

    if discord_record:
        await bot.db.execute("UPDATE members SET uuid = ? WHERE discord_id = ?", (uuid, discord_id))
        await bot.db.commit()
        await check_and_update_username(uuid, username)
    else:
        await insert_new_member(discord_id, uuid, username)


async def get_do_ping(uuid: str) -> Tuple[int, bool]:
    res = await select_one("SELECT discord_id, do_pings from members WHERE uuid = (?)", (uuid,))
    return (res[0], res[1]) if res else (0, 0)


async def set_do_ping_db(discord_id: int, do_pings: int) -> str:
    await bot.db.execute("UPDATE members set do_pings = ? WHERE discord_id = ?", (do_pings, discord_id))
    await bot.db.commit()

    return (await get_db_uuid_username(discord_id=discord_id))[0]


async def get_db_uuid_username(discord_id: int = None, username: str = None, uuid: str = None,
                               get_discord_id: bool = False) -> Tuple[
                                                                    str, str] | Tuple[str, str, int] | Tuple[
                                                                    None, None] | Tuple[None, str] | Tuple[str, None] | \
                                                                Tuple[None, str, int]:
    if uuid and uuid == "0":
        return None, None
    if uuid:
        username, uuid = await get_username_from_uuid(uuid)
        if not username and not get_discord_id:
            return None, uuid

        if get_discord_id:
            discord_id = await get_discord_id_from_uuid(uuid)
            if not username:
                return None, uuid, discord_id

            return username, uuid, discord_id

        return username, uuid
    if discord_id:
        uuid = await get_uuid_from_discord_id(discord_id)
        return await get_username_from_uuid(uuid)
    if username:
        username, uuid = await get_uuid_from_username(username)
        if not uuid:
            return username, None
        if get_discord_id:
            discord_id = await get_discord_id_from_uuid(uuid)
            return username, uuid, discord_id
        return username, uuid

    return None, None
