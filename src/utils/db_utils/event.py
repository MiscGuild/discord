import json
from __main__ import bot
from datetime import datetime

from .connection import select_one, select_all


async def get_all_event_members() -> list:
    return await select_all("SELECT uuid from event")


async def get_event_member_gexp_history(uuid: str) -> dict:
    history = await select_one("SELECT gexp_history from event WHERE uuid = (?)", (uuid,))
    return json.loads(history[0]) if history else None


async def set_event_member_gexp_history(uuid: str, gexp_history: dict) -> dict | None:
    # Filter for entries in July
    july_entries = {
        date: value for date, value in gexp_history.items()
        if datetime.strptime(date, "%Y-%m-%d").month == 7
    }

    if not july_entries:
        return None  # Do nothing if no July data

    # Proceed with DB update
    current_history: dict = await get_event_member_gexp_history(uuid)

    if not current_history:
        await bot.db.execute("INSERT INTO event VALUES (?, ?)", (uuid, json.dumps(july_entries)))
        await bot.db.commit()
        return july_entries

    current_history.update(july_entries)
    sorted_history = dict(sorted(current_history.items(), reverse=True))

    await bot.db.execute(
        "UPDATE event SET gexp_history = ? WHERE uuid = ?",
        (json.dumps(sorted_history), uuid)
    )
    await bot.db.commit()

    return sorted_history


async def insert_event_invitee(inviter_uuid: str, invitee_uuid: str) -> None:
    await bot.db.execute(
        "INSERT OR REPLACE INTO event_invites (inviter_uuid, invitee_uuid) VALUES (?, ?)",
        (inviter_uuid, invitee_uuid)
    )
    await bot.db.commit()


async def get_event_invitees(inviter_uuid: str) -> list[str]:
    cursor = await bot.db.execute(
        "SELECT invitee_uuid FROM event_invites WHERE inviter_uuid = ?",
        (inviter_uuid,)
    )
    rows = await cursor.fetchall()
    return [row[0] for row in rows]
