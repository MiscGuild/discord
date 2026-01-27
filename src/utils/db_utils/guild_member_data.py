import json
from __main__ import bot

from .connection import select_one, select_all


async def get_all_guild_members() -> list:
    return await select_all("SELECT uuid from guild_member_data")


async def remove_guild_member(uuid: str) -> None:
    await bot.db.execute("DELETE FROM guild_member_data WHERE uuid = (?)", (uuid,))
    await bot.db.commit()


async def get_member_gexp_history(uuid: str) -> dict:
    history = await select_one("SELECT gexp_history from guild_member_data WHERE uuid = (?)", (uuid,))
    return json.loads(history[0]) if history else None


async def set_member_gexp_history(uuid: str, gexp_history: dict) -> dict:
    current_history: dict = await get_member_gexp_history(uuid)

    if not current_history:
        # Direct insert if no existing history
        await bot.db.execute("INSERT INTO guild_member_data VALUES (?, ?)", (uuid, json.dumps(gexp_history)))
        await bot.db.commit()
        return gexp_history

    current_history.update(gexp_history)

    sorted_history = dict(sorted(current_history.items(), reverse=True))

    # limited_history = dict(list(sorted_history.items())[:365])  # Keeps the 365 most recent entries

    await bot.db.execute("UPDATE guild_member_data SET gexp_history = ? WHERE uuid = ?",
                         (json.dumps(sorted_history), uuid))
    await bot.db.commit()

    return sorted_history
