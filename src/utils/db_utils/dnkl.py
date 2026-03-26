from __main__ import bot

from .connection import select_all
from .users import check_and_update_username
from ..data_classes import RegisteredDiscordMember


async def insert_new_dnkl(message_id: int, uuid: str, username: str) -> None:
    await bot.db.execute("INSERT INTO dnkl VALUES (?, ?)", (message_id, uuid))
    await bot.db.commit()
    await check_and_update_username(uuid, username)


async def update_dnkl(message_id: int, uuid: str) -> None:
    await bot.db.execute("UPDATE dnkl SET message_id = (?) WHERE uuid = (?)", (message_id, uuid,))
    await bot.db.commit()


async def delete_dnkl(uuid: str) -> None:
    await bot.db.execute("DELETE FROM dnkl WHERE uuid = (?)", (uuid,))
    await bot.db.commit()


async def get_dnkl_list() -> list:
    # Fetch all rows
    rows = await select_all("SELECT * FROM dnkl")
    if not rows:
        return []
    players = []
    for row in rows:
        member_lookup = RegisteredDiscordMember()
        member = await member_lookup.from_uuid(row[1])
        players.append((member.ign, member.uuid))
    return players
