import math
import re

from src.utils.consts import ChatColor, active_req, member_req, resident_req
from src.utils.request_utils import get_player_guild, get_name_by_uuid, get_hypixel_player


async def get_player_gexp(uuid: str, guild_data: dict = None):
    if not guild_data:
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
                # Gold/Aqua MVP++
                if "rankPlusColor" not in player_data:
                    return "&6[MVP&c++&6]" if "monthlyRankColor" not in player_data or player_data[
                        "monthlyRankColor"] == "GOLD" else "&b[MVP&c++&b]", "[MVP++]"

                # MVP++ with custom + color
                pluscolor = ChatColor[player_data["rankPlusColor"]].value
                return f"&6[MVP{pluscolor}++&6]" if "monthlyRankColor" not in player_data or player_data[
                    "monthlyRankColor"] == "GOLD" else f"&b[MVP{pluscolor}++&b]", "[MVP++]"

            # Player is MVP+
            # Custom + color
            if "rankPlusColor" in player_data:
                pluscolor = ChatColor[player_data["rankPlusColor"]].value
                return f"&b[MVP{pluscolor}+&b]", "[MVP+]"
            # Default + color
            return "&b[MVP&c+&b]", "[MVP+]"

    return "&7", ""


async def calculate_network_level(total_exp: int):
    return round((math.sqrt((2 * total_exp) + 30625) / 50) - 2.5, 2)


async def get_gexp_sorted(guild_data: dict):
    member_gexp = {}

    # Loop through all guild members' gexp, adding it to dict
    for member in guild_data["members"]:
        member_gexp[member["uuid"]] = sum(
            member["expHistory"].values())
    # Sort member gexp
    member_gexp = sorted(member_gexp.items(), key=lambda item: item[1], reverse=True)

    return member_gexp


async def generate_lb_text(member_gexp: list, text: str):
    # Generate leaderboard text
    count = 0
    for uuid, gexp in member_gexp[:10]:
        count += 1
        name = await get_name_by_uuid(uuid)
        rank, _ = await get_hypixel_player_rank(
            await get_hypixel_player(uuid=uuid))  # Ignores value without color formatting

        # Add new entry to image content
        ##text += f"&6{count}. {rank} {name} &2{format(gexp, ',d')} Guild Experience"
        text += f"> {count}. {name} - {format(gexp, ',d')} Guild Experience"
        # Add new line
        if count < 10:
            # text += "%5Cn"
            text += "\n"

    # Replace characters for the URL
    #text = text.replace("+", "%2B").replace("&", "%26").replace(" ", "%20").replace(",", "%2C")

    # Return image
    return text


async def get_guild_level(exp):
    EXP_NEEDED = [100000, 150000, 250000, 500000, 750000, 1000000, 1250000, 1500000, 2000000, 2500000, 2500000, 2500000,
                  2500000, 2500000, 3000000]
    # A list of amount of XP required for leveling up in each of the beginning levels (1-15).

    level = 0

    for i in range(1000):
        # Increment by one from zero to the level cap.
        need = 0
        if i >= len(EXP_NEEDED):
            need = EXP_NEEDED[len(EXP_NEEDED) - 1]
        else:
            need = EXP_NEEDED[i]
        # Determine the current amount of XP required to level up,
        # in regards to the "i" variable.

        if (exp - need) < 0:
            return round(((level + (exp / need)) * 100) / 100, 2)
        # If the remaining exp < the total amount of XP required for the next level,
        # return their level using this formula.

        level += 1
        exp -= need
        # Otherwise, increase their level by one,
        # and subtract the required amount of XP to level up,
        # from the total amount of XP that the guild had.
