# The following file contains: get_player_gexp, get_graph_color_by_rank

from __main__ import bot

from func.utils.request_utils import get_mojang_profile, get_player_guild


# Returns player's gexp history and total
async def get_player_gexp(name: str):
    name, uuid = await get_mojang_profile(name)
    guild_data = await get_player_guild(uuid)

    # Player is in a guild
    if guild_data:
        for member in guild_data["guild"]["members"]:
            if member["uuid"] == uuid:
                return member["expHistory"], sum(member["expHistory"].values())

    # Player is not in a guild
    return None, None


# Returns a color based on player's gexp and their guild rank
async def get_graph_color_by_rank(rank: str, weekly_gexp: int):
    if rank == "Resident":
        # Member meets res reqs
        if weekly_gexp > bot.resident_req:
            return 0x64ffb4, 'rgba(100, 255, 180,0.3)', 'rgba(100, 255, 180,0.3)'

        # Member does not meet res reqs
        return 0xffb464, 'rgba(255, 180, 100,0.3)', 'rgba(255, 180, 100,0.3)'

    else:
        # Member meets active reqs
        if weekly_gexp > bot.active_req:
            return 0x64b4ff, 'rgba(100, 180, 255,0.3)', 'rgba(100, 180, 255,0.3)'

        # Member meets normal reqs
        if weekly_gexp > bot.member_req:
            return 0x64ffff, 'rgba(100, 255, 255,0.3)', 'rgba(100, 255, 255,0.3)'

        # Member is inactive
        return 0xff6464, 'rgba(255, 100, 100,0.3)', 'rgba(255, 100, 100,0.3)'
