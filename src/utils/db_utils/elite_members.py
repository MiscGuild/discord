from __main__ import bot
from typing import Tuple

from .connection import select_one


async def get_all_elite_members() -> list[Tuple[str, str, str]] | None:
    return await select_one(
        "SELECT uuid, is_booster, is_sponsor, is_gvg, is_creator, is_indefinite, expiry FROM elite_members")


async def get_elite_member(uuid: str) -> Tuple[str, str] | None:
    return await select_one(
        "SELECT is_booster, is_sponsor, is_gvg, is_creator, is_indefinite, expiry from elite_members WHERE uuid = (?)",
        (uuid,))


async def insert_elite_member(uuid: str, reason: str, is_indefinite: bool, expiry: str = None) -> None:
    await bot.db.execute("INSERT INTO elite_members VALUES (?, ?, ?, ?)", (uuid, reason, is_indefinite, expiry))
    await bot.db.commit()
