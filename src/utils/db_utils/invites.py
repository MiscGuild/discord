from __main__ import bot
from typing import Tuple

from .connection import select_one


async def insert_new_inviter(inviter_uuid: str, invitee_uuid: str) -> None:
    await bot.db.execute("INSERT INTO invites VALUES (?, ?, 0, 0)",
                         (inviter_uuid, invitee_uuid))
    await bot.db.commit()


async def add_invitee(inviter_uuid, invitee_uuid) -> int | None:
    invitees = (await select_one("SELECT current_invitee_uuids FROM invites WHERE inviter_uuid = (?)",
                                 (inviter_uuid,)))[0].split(" ")
    if invitee_uuid in invitees:
        return None

    invitees.append(invitee_uuid)
    count = len(invitees)
    invitees = " ".join([str(invitee) for invitee in invitees])
    await bot.db.execute("UPDATE invites SET current_invitee_uuids = (?) WHERE inviter_uuid = (?)",
                         (invitees, inviter_uuid))
    await bot.db.commit()

    return count


async def get_invites(inviter_uuid) -> Tuple[str, int, int] | None:
    return (await select_one(
        "SELECT current_invitee_uuids, total_invites, total_valid_invites FROM invites WHERE inviter_uuid = (?)",
        (inviter_uuid,)))
