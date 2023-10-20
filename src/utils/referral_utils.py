from __main__ import bot
from datetime import datetime, timedelta
from math import ceil
from random import shuffle, choice

from src.utils.consts import guild_handle, member_req, active_req, rank_upgrade_channel
from src.utils.db_utils import select_one, insert_new_inviter, add_invitee
from src.utils.minecraft_utils import get_player_gexp, get_gexp_sorted
from src.utils.request_utils import get_mojang_profile, get_player_guild, get_guild_by_name, get_name_by_uuid


async def validate_reference(ctx, invitee_uuid, inviter_ign):
    inviter_ign, inviter_uuid = await get_mojang_profile(inviter_ign) if inviter_ign else (None, None)
    if not inviter_uuid:
        return f"{inviter_ign} is not a valid minecraft username.\nThis reference will not count."

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
        return f"{inviter_ign} has already invited you in the past. No duplicate entries!"
    return f"{inviter_ign} has invited {count} members to the guild this week!"


async def check_invitation_validity(invitations: list):
    guild_data = await get_guild_by_name(guild_handle)
    members = []
    for member in guild_data["members"]:
        members.append(member["uuid"])

    weekly_valid_invites = []
    for invitee_uuid in invitations:
        if invitee_uuid not in members:
            continue

        _, weekly_gexp = await get_player_gexp(invitee_uuid, guild_data)
        if weekly_gexp > (member_req * 2):
            weekly_valid_invites.append(invitee_uuid)

    return weekly_valid_invites


async def generate_rank_upgrade(weekly_invites: list):
    guild_data = await get_guild_by_name(guild_handle)
    members = await get_gexp_sorted(guild_data)
    entries = {}
    total_gexp = sum([gexp for uuid, gexp in members])

    # 1) Active req is subtracted from the player's weekly guild experience
    # 2) The difference is divided by 50,000 and rounded up
    # 3) The quotient is multiplied by 10 and added to the player's entries
    for uuid, gexp in members[:10]:
        if gexp < active_req:
            break
        gexp = gexp - active_req
        entry_multiplier = ceil(gexp / 50000)
        entries[uuid] = 10 * entry_multiplier

    # A player gets 1 entry for every valid invite they have made
    total_invitations = 0
    for uuid, invitations in weekly_invites:
        entries[uuid] = entries[uuid] + len(invitations) if uuid in entries else len(invitations)
        total_invitations += len(invitations)

    weighted_entries = [uuid for uuid, weight in entries.items() for _ in range(weight)]
    shuffle(weighted_entries)
    winner_uuid = choice(weighted_entries)
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

    date = (f"__Week {int(0 + round((datetime.utcnow() - datetime.strptime('16/09/2023', '%d/%m/%Y')).days / 7))}__\n"
            f"**{(datetime.utcnow() - timedelta(days=7)).strftime('%d %b %Y')} "
            f"-"
            f" {datetime.utcnow().strftime('%d %B %Y')}**")

    announcement = f'''# RANK UPGRADE
{date}

**The winner is....**
## {winner}
> Total Guild Experience:- `{format(winner_gexp, ',d')}`
> Invites:- `{format(len(winner_invites), ',d')}`
> Total Entries:- `{format(entries[winner_uuid], ',d') if winner_uuid in entries else 0}`


### Here are some statistics for the past week
- Total unscaled guild experience earned - `{format(total_gexp, ',d')}`
- Total players invited - `{format(total_invitations, ',d')}`

*To know how the winner is picked, go here https://discord.com/channels/522586672148381726/1152480866585554994/1152521488356872222*'''

    await bot.get_channel(rank_upgrade_channel).send(announcement)