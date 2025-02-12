from __main__ import bot
from datetime import datetime, timedelta, timezone
from math import exp
from random import shuffle, choice
from typing import List

from src.utils.calculation_utils import get_player_gexp, get_gexp_sorted
from src.utils.consts import guild_handle, member_req, active_req, rank_upgrade_channel, \
    rank_upgrade_winner_announcement
from src.utils.db_utils import select_one, insert_new_inviter, add_invitee, get_db_uuid_username
from src.utils.request_utils import get_player_guild, get_guild_by_name, get_name_by_uuid, get_uuid_by_name


async def validate_invites(inviter_ign, invitee_ign) -> str:
    invitee_ign, invitee_uuid = await get_uuid_by_name(invitee_ign) if invitee_ign else (None, None)
    inviter_ign, inviter_uuid = await get_uuid_by_name(inviter_ign) if inviter_ign else (None, None)

    if not inviter_uuid or not inviter_ign:
        return f"{inviter_ign} is not a valid minecraft username.\nThis reference will not count."
    if not invitee_uuid or not invitee_ign:
        return f"Bot broke. \n{invitee_ign} is not a valid minecraft username.\nThis reference will not count."

    guild_data = await get_player_guild(inviter_uuid)
    guild_name = "Guildless" if not guild_data else guild_data["name"]

    if guild_name != guild_handle:
        return f"{inviter_ign} is a member of {guild_name}\nThis reference will not count."

    inviter = await select_one("SELECT current_invitee_uuids FROM invites WHERE inviter_uuid = (?)",
                               (inviter_uuid,))

    if not inviter:
        await insert_new_inviter(inviter_uuid, invitee_uuid)
        return f"{inviter_ign}'s invites have been updated!"

    count = await add_invitee(inviter_uuid, invitee_uuid)
    if not count:
        return f"{inviter_ign} has already invited {invitee_ign} in the past. No duplicate entries!"
    return f"{inviter_ign} has invited {count} members to the guild this week!"


async def check_invitation_validity(invitations: list) -> List[str]:
    guild_data = await get_guild_by_name(guild_handle)
    members = {}
    for member in guild_data["members"]:
        members[member["uuid"]] = member["joined"]

    weekly_valid_invites = []
    for invitee_uuid in invitations:
        if invitee_uuid not in members.keys():
            continue

        _, weekly_gexp = await get_player_gexp(invitee_uuid, guild_data)

        # Player earns more than double the member requirement
        if weekly_gexp > (member_req * 2):
            weekly_valid_invites.append(invitee_uuid)
            continue

        # Player has joined less than 7 days ago. Their gexp scaled up is double the member requirement.
        days_since_join = (datetime.now(timezone.utc) - datetime.fromtimestamp(members[invitee_uuid] / 1000.0,
                                                                               tz=timezone.utc)).days
        if days_since_join <= 7 and ((weekly_gexp * 2) > ((member_req / 7) * days_since_join)):
            weekly_valid_invites.append(invitee_uuid)

    return weekly_valid_invites


async def get_entries(gexp) -> int:
    if gexp >= active_req:
        return round(50 * (1 - exp(-gexp / 500000)))
    elif gexp >= member_req:
        return 1
    return 0


async def generate_rank_upgrade(weekly_invites: list) -> None:
    guild_data = await get_guild_by_name(guild_handle)
    members = await get_gexp_sorted(guild_data)
    entries = {}
    total_gexp = sum([gexp for uuid, gexp in members])

    for uuid, gexp in members:
        entries[uuid] = await get_entries(gexp)

    # A player gets 7 entries for every valid invite they have made
    total_invitations = 0
    for uuid, invitations in weekly_invites:
        entries[uuid] = entries[uuid] + (len(invitations) * 12) if uuid in entries else (len(invitations) * 12)
        total_invitations += len(invitations)

    weighted_entries = [uuid for uuid, weight in entries.items() for _ in range(weight)]
    shuffle(weighted_entries)
    winner_uuid = choice(weighted_entries)

    username, uuid, discord_id = await get_db_uuid_username(uuid=winner_uuid, get_discord_id=True)
    if discord_id:
        winner = f"<@{discord_id}>"
    else:
        winner = await get_name_by_uuid(winner_uuid)

    winner_gexp = None
    for uuid, gexp in members:
        if uuid == winner_uuid:
            winner_gexp = gexp
            break

    winner_invites = None
    for uuid, invites in weekly_invites:
        if uuid == winner_uuid:
            winner_invites = invites
            break

    start_date = datetime.strptime('16/09/2023', '%d/%m/%Y').replace(tzinfo=timezone.utc)

    current_date = datetime.now(timezone.utc)

    week_number = int(round((current_date - start_date).days / 7))

    date = (
        f"__Week {week_number}__\n"
        f"**{(current_date - timedelta(days=7)).strftime('%d %b %Y')} "
        f"- {current_date.strftime('%d %B %Y')}**"
    )

    announcement = rank_upgrade_winner_announcement.format(
        date=date,
        winner=winner,
        winner_gexp=format(winner_gexp, ',d'),
        winner_invites=format(len(winner_invites), ',d') if winner_invites else 0,
        winner_entries=format(entries[winner_uuid], ',d') if winner_uuid in entries else 0,
        total_gexp=format(total_gexp, ',d'),
        total_invites=format(total_invitations, ',d'),
        total_entries=format(sum(entries.values()), ',d')
    )

    await bot.get_channel(rank_upgrade_channel).send(announcement)
