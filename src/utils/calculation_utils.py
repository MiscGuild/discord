import math
import re
from datetime import datetime, timedelta

from src.utils.consts import ChatColor, active_req, member_req, resident_req
from src.utils.db_utils import check_uuid_in_db, get_db_username_from_uuid
from src.utils.request_utils import get_player_guild, get_name_by_uuid


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


async def generate_lb_text(member_gexp: list, text: str, do_ping):
    # Generate leaderboard text
    count = 0
    for uuid, gexp in member_gexp[:10]:
        count += 1

        discord_id = await check_uuid_in_db(uuid)
        username = await get_db_username_from_uuid(uuid=uuid)
        if discord_id and do_ping:
            name = f"<@{discord_id}>"
        else:
            name = await get_name_by_uuid(uuid) if not username else username

        # rank, _ = await get_hypixel_player_rank(
        #    await get_hypixel_player(uuid=uuid))  # Ignores value without color formatting
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


async def check_tag(tag: str):
    tag = tag.lower()
    with open(r"src/utils/badwords.txt", "r") as f:
        badwords = f.read()

    if tag in badwords.split("\n"):
        return False, "Your tag may not include profanity."
    if not tag.isascii():
        return False, "Your tag may not include special characters unless it's the tag of an ally guild."
    if len(tag) > 6:
        return False, "Your tag may not be longer than 6 characters."
    # Tag is okay to use
    return True, None


async def is_valid_date(date: str):
    # Return False if parsing fails
    try:
        parsed = datetime.strptime(date, "%Y/%m/%d")
        # Validate time is within the last week
        if parsed < datetime.utcnow() - timedelta(days=7):
            return False, None, None, None
        return True, parsed.day, parsed.month, parsed.year
    except ValueError:
        return False, None, None, None


async def extract_usernames(message: str):
    # Define regular expressions for both formats
    format1_pattern = r"🎉 \*\*(?:\[(.*?)\] )?(.*?)\*\* joined the guild! \*\*They weren't invited by anyone\."
    format2_pattern = r"🎉 \*\*(?:\[(.*?)\] )?(.*?)\*\* invited(?: \*\*\[(.*?)\] )?(?:\*\*)? (?:\*\*)?(.*?)\*\* to the guild!"

    # Check if it matches format 1
    match_format1 = re.match(format1_pattern, message)
    if match_format1:
        username1 = match_format1.group(2)
        return username1, None

    # Check if it matches format 2
    match_format2 = re.match(format2_pattern, message)
    if match_format2:
        username1 = match_format2.group(2)
        username2 = match_format2.group(4)
        if username2.startswith('['):  # Check if the second username starts with '[' indicating a rank
            username2 = username2.split('] ')[1]  # Remove the rank from the second username
        return username1, username2.strip('**')  # Remove any leading or trailing '**'

    # If it doesn't match any format, return None for both usernames
    return None, None
