from __main__ import bot
from typing import Tuple

from .connection import select_one


async def insert_new_giveaway(msg_id: int, channel_id: int, prize: str, number_winners: int, time_of_finish: str,
                              req_gexp: int, all_roles_required: bool, req_roles: str, sponsors: str) -> None:
    await bot.db.execute("INSERT INTO Giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
        msg_id, channel_id, prize, number_winners, time_of_finish, req_gexp, all_roles_required, req_roles, sponsors,
        True))
    await bot.db.commit()


async def get_giveaway_status(id: int) -> Tuple[bool] | None:
    return await select_one("SELECT is_active FROM giveaways WHERE message_id = (?)", (id,))


async def set_giveaway_inactive(id: int) -> None:
    await bot.db.execute(f"Update giveaways SET is_active = 0 WHERE message_id = (?)", (id,))
    await bot.db.commit()
