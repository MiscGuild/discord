import math
import re

from src.utils.consts import ChatColor, active_req, member_req, resident_req
from src.utils.request_utils import get_player_guild


async def get_player_gexp(uuid: str):
    guild_data = await get_player_guild(uuid)

    # Player is in a guild
    if guild_data:
        for member in guild_data["members"]:
            if member["uuid"] == uuid:
                return member["expHistory"], sum(member["expHistory"].values())

    # Player is not in a guild
    return None, None

async def get_color_by_gexp(rank: str, weekly_gexp: int):
    if rank == "Resident":
        # Member meets res reqs
        if weekly_gexp > resident_req:
            return 0xFF55FF, "rgba(255,85,255, 0.3)", "rgba(255,85,255, 0.3)"
            # return 0x64ffb4, "rgba(100, 255, 180,0.3)", "rgba(100, 255, 180,0.3)"

        # Member does not meet res reqs
        return 0xffb464, "rgba(255, 180, 100,0.3)", "rgba(255, 180, 100,0.3)"

    else:
        # Member meets active reqs
        if weekly_gexp > active_req:
            return 0x9c119c, "rgba(156, 17, 156,0.3)", "rgba(156, 17, 156,0.3)"
            # return 0x64b4ff, "rgba(100, 180, 255,0.3)", "rgba(100, 180, 255,0.3)"

        # Member meets normal reqs
        if weekly_gexp > member_req:
            return 0xFF55FF, "rgba(255,85,255, 0.3)", "rgba(255,85,255, 0.3)"
            # return 0x64ffff, "rgba(100, 255, 255,0.3)", "rgba(100, 255, 255,0.3)"

        # Member is inactive
        return 0xff6464, "rgba(255, 100, 100,0.3)", "rgba(255, 100, 100,0.3)"

async def get_hypixel_player_rank(player_data: dict):
    if not player_data:
        return None, None

    if "prefix" in player_data and player_data["prefix"] in ["§d[PIG§b+++§d]", "§c[SLOTH]", "§c[OWNER]"]:
        return player_data["prefix"].replace("§", "&"), re.sub(r"(§.)", "", player_data["prefix"])

    if "newPackageRank" in player_data:
        # Player is a youtuber/admin
        if "rank" in player_data:
            if player_data["rank"] == "YOUTUBER":
                return "&c[&fYOUTUBE&c]", "[YOUTUBE]"
            elif player_data["rank"] == "ADMIN":
                return "&c[ADMIN]", "[ADMIN]"
    
        else:
            rank = player_data["newPackageRank"]

            # VIP - MVP+
            if rank == "VIP":
                return "&a[VIP]", "[VIP]"
            elif rank == "VIP_PLUS":
                return "&a[VIP&6+&a]", "[VIP+]"
            elif rank == "MVP":
                return "&b[MVP]", "[MVP]"
            elif rank == "MVP_PLUS":
                if "monthlyPackageRank" in player_data:
                    # Had MVP++ but now is an MVP+
                    if player_data["monthlyPackageRank"] == "NONE":
                        # Custom + color
                        if "rankPlusColor" in player_data:
                            pluscolor = ChatColor[player_data["rankPlusColor"]].value
                            return f"&b[MVP{pluscolor}+&b]", "[MVP+]"
                        # Default + color
                        return "&b[MVP&c+&b]", "[MVP+]"

                    # Player is MVP++
                    else:
                        # Gold/Aqua MVP++
                        if "rankPlusColor" not in player_data:
                            return "&6[MVP&c++&6]" if "monthlyRankColor" not in player_data or player_data["monthlyRankColor"] == "GOLD" else "&b[MVP&c++&b]", "[MVP++]"
                        
                        # MVP++ with custom + color
                        pluscolor = ChatColor[player_data["rankPlusColor"]].value
                        return f"&6[MVP{pluscolor}++&6]" if "monthlyRankColor" not in player_data or player_data["monthlyRankColor"] == "GOLD" else f"&b[MVP{pluscolor}++&b]", "[MVP++]"

                # Player is MVP+
                else: 
                    # Custom + color
                    if "rankPlusColor" in player_data:
                        pluscolor = ChatColor[player_data["rankPlusColor"]].value
                        return f"&b[MVP{pluscolor}+&b]", "[MVP+]"
                    # Default + color
                    return "&b[MVP&c+&b]", "[MVP+]"
    else:
        return "&7", ""

async def calculate_network_level(total_exp: int):
    return round((math.sqrt((2 * total_exp) + 30625) / 50) - 2.5, 2)
