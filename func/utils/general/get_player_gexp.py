from func.utils.general.requests.m_profile import m_profile
from func.utils.general.requests.player_guild import player_guild

async def get_player_gexp(name: str):
    name, uuid = await m_profile(name)
    guild_data = await player_guild(uuid)

    # Player is in a guild
    if guild_data != None:
        for member in guild_data["guild"]["members"]:
            if member["uuid"] == uuid:
                return member["expHistory"], sum(member["expHistory"].values())
    
    # Player is not in a guild
    return None, None