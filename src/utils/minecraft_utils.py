import math
import re
from datetime import datetime

from src.utils.consts import ChatColor, active_req, member_req, resident_req
from src.utils.db_utils import select_one, new_tournament_player, set_weekly_data, select_all, update_recent
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


async def get_hypixel_player_rank(player_data):
    if not isinstance(player_data, dict) and player_data:
        player_data = eval(player_data)
    else:
        player_data = dict(player_data)

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
        text += f"&6{count}. {rank} {name} &2{format(gexp, ',d')} Guild Experience"
        # Add new line
        if count < 10:
            text += "%5Cn"

    # Replace characters for the URL
    text = text.replace("+", "%2B").replace("&", "%26").replace(" ", "%20").replace(",", "%2C")

    # Return image
    return text


async def get_points_from_data(start_data, end_data):
    start_data = eval(start_data)
    if not isinstance(end_data, dict) and end_data:
        end_data = eval(end_data)
    else:
        end_data = dict(end_data)

    games_played = (end_data["games_played_bedwars"] - start_data["games_played_bedwars"])
    wins = (end_data["wins_bedwars"] - start_data["wins_bedwars"])
    bed_breaks_end = int(end_data["eight_one_beds_broken_bedwars"] + end_data["eight_two_beds_broken_bedwars"] +
                      end_data["four_three_beds_broken_bedwars"] + end_data["four_four_beds_broken_bedwars"] +
                      end_data["two_four_beds_broken_bedwars"])
    bed_breaks_start = int(start_data["eight_one_beds_broken_bedwars"] + start_data["eight_two_beds_broken_bedwars"] +
                        start_data["four_three_beds_broken_bedwars"] + start_data["four_four_beds_broken_bedwars"] +
                        start_data["two_four_beds_broken_bedwars"])
    bed_breaks = bed_breaks_end - bed_breaks_start
    losses = games_played - wins
    wlr = round(wins / losses, 2) if losses != 0 else wins

    final_kills = (end_data["final_kills_bedwars"] - start_data["final_kills_bedwars"])
    final_deaths = (end_data["final_deaths_bedwars"] - start_data["final_deaths_bedwars"])
    fkdr = round(final_kills / final_deaths, 2) if final_deaths != 0 else final_kills


    start_points = 0
    start_points += (end_data["total_challenges_completed"] - start_data["total_challenges_completed"]) * 5

    start_points += (end_data["eight_one_final_kills_bedwars"] - start_data["eight_one_final_kills_bedwars"]) * 30
    start_points += (end_data["eight_one_kills_bedwars"] - start_data["eight_one_kills_bedwars"]) * 1
    start_points += (end_data["eight_one_beds_broken_bedwars"] - start_data["eight_one_beds_broken_bedwars"]) * 20
    start_points += (end_data["eight_one_wins_bedwars"] - start_data["eight_one_wins_bedwars"]) * 40

    start_points += (end_data["eight_two_final_kills_bedwars"] - start_data["eight_two_final_kills_bedwars"]) * 15
    start_points += (end_data["eight_two_kills_bedwars"] - start_data["eight_two_kills_bedwars"]) * 1
    start_points += (end_data["eight_two_beds_broken_bedwars"] - start_data["eight_two_beds_broken_bedwars"]) * 20
    start_points += (end_data["eight_two_wins_bedwars"] - start_data["eight_two_wins_bedwars"]) * 40

    start_points += (end_data["four_three_final_kills_bedwars"] - start_data["four_three_final_kills_bedwars"]) * 20
    start_points += (end_data["four_three_kills_bedwars"] - start_data["four_three_kills_bedwars"]) * 1
    start_points += (end_data["four_three_beds_broken_bedwars"] - start_data["four_three_beds_broken_bedwars"]) * 30
    start_points += (end_data["four_three_wins_bedwars"] - start_data["four_three_wins_bedwars"]) * 30

    start_points += (end_data["four_four_final_kills_bedwars"] - start_data["four_four_final_kills_bedwars"]) * 15
    start_points += (end_data["four_four_kills_bedwars"] - start_data["four_four_kills_bedwars"]) * 1
    start_points += (end_data["four_four_beds_broken_bedwars"] - start_data["four_four_beds_broken_bedwars"]) * 30
    start_points += (end_data["four_four_wins_bedwars"] - start_data["four_four_wins_bedwars"]) * 30

    start_points += (end_data["two_four_final_kills_bedwars"] - start_data["two_four_final_kills_bedwars"]) * 20
    start_points += (end_data["two_four_kills_bedwars"] - start_data["two_four_kills_bedwars"]) * 1
    start_points += (end_data["two_four_beds_broken_bedwars"] - start_data["two_four_beds_broken_bedwars"]) * 20
    start_points += (end_data["two_four_wins_bedwars"] - start_data["two_four_wins_bedwars"]) * 20

    return start_points, games_played, wins, wlr, final_kills, fkdr, bed_breaks


async def get_game_data(player_data):
    if not isinstance(player_data, dict) and player_data:
        player_data = eval(player_data)
    else:
        player_data = dict(player_data)

    bedwars_data = player_data["stats"]["Bedwars"]
    total_challenges_completed = bedwars_data[
        "challenges_completed_bedwars"] if "challenges_completed_bedwars" in bedwars_data else 0
    games_played_bedwars = bedwars_data["games_played_bedwars"] if "games_played_bedwars" in bedwars_data else 0
    deaths_bedwars = bedwars_data["deaths_bedwars"] if "deaths_bedwars" in bedwars_data else 0
    wins_bedwars = bedwars_data["wins_bedwars"] if "wins_bedwars" in bedwars_data else 0
    final_kills_bedwars = bedwars_data["final_kills_bedwars"] if "final_kills_bedwars" in bedwars_data else 0
    final_deaths_bedwars = bedwars_data["final_deaths_bedwars"] if "final_deaths_bedwars" in bedwars_data else 0
    eight_one_final_kills_bedwars = bedwars_data[
        "eight_one_final_kills_bedwars"] if "eight_one_final_kills_bedwars" in bedwars_data else 0
    eight_one_kills_bedwars = bedwars_data[
        "eight_one_kills_bedwars"] if "eight_one_kills_bedwars" in bedwars_data else 0
    eight_one_beds_broken_bedwars = bedwars_data[
        "eight_one_beds_broken_bedwars"] if "eight_one_beds_broken_bedwars" in bedwars_data else 0
    eight_one_wins_bedwars = bedwars_data["eight_one_wins_bedwars"] if "eight_one_wins_bedwars" in bedwars_data else 0
    eight_one_games_played_bedwars = bedwars_data[
        "eight_one_games_played_bedwars"] if "eight_one_games_played_bedwars" in bedwars_data else 0
    eight_two_final_kills_bedwars = bedwars_data[
        "eight_two_final_kills_bedwars"] if "eight_two_final_kills_bedwars" in bedwars_data else 0
    eight_two_kills_bedwars = bedwars_data[
        "eight_two_kills_bedwars"] if "eight_two_kills_bedwars" in bedwars_data else 0
    eight_two_beds_broken_bedwars = bedwars_data[
        "eight_two_beds_broken_bedwars"] if "eight_two_beds_broken_bedwars" in bedwars_data else 0
    eight_two_wins_bedwars = bedwars_data["eight_two_wins_bedwars"] if "eight_two_wins_bedwars" in bedwars_data else 0
    eight_two_games_played_bedwars = bedwars_data[
        "eight_two_games_played_bedwars"] if "eight_two_games_played_bedwars" in bedwars_data else 0
    four_three_final_kills_bedwars = bedwars_data[
        "four_three_final_kills_bedwars"] if "four_three_final_kills_bedwars" in bedwars_data else 0
    four_three_kills_bedwars = bedwars_data[
        "four_three_kills_bedwars"] if "four_three_kills_bedwars" in bedwars_data else 0
    four_three_beds_broken_bedwars = bedwars_data[
        "four_three_beds_broken_bedwars"] if "four_three_beds_broken_bedwars" in bedwars_data else 0
    four_three_wins_bedwars = bedwars_data[
        "four_three_wins_bedwars"] if "four_three_wins_bedwars" in bedwars_data else 0
    four_three_games_played_bedwars = bedwars_data[
        "four_three_games_played_bedwars"] if "four_three_games_played_bedwars" in bedwars_data else 0
    four_four_final_kills_bedwars = bedwars_data[
        "four_four_final_kills_bedwars"] if "four_four_final_kills_bedwars" in bedwars_data else 0
    four_four_kills_bedwars = bedwars_data[
        "four_four_kills_bedwars"] if "four_four_kills_bedwars" in bedwars_data else 0
    four_four_beds_broken_bedwars = bedwars_data[
        "four_four_beds_broken_bedwars"] if "four_four_beds_broken_bedwars" in bedwars_data else 0
    four_four_wins_bedwars = bedwars_data["four_four_wins_bedwars"] if "four_four_wins_bedwars" in bedwars_data else 0
    four_four_games_played_bedwars = bedwars_data[
        "four_four_games_played_bedwars"] if "four_four_games_played_bedwars" in bedwars_data else 0
    two_four_final_kills_bedwars = bedwars_data[
        "two_four_final_kills_bedwars"] if "two_four_final_kills_bedwars" in bedwars_data else 0
    two_four_kills_bedwars = bedwars_data["two_four_kills_bedwars"] if "two_four_kills_bedwars" in bedwars_data else 0
    two_four_beds_broken_bedwars = bedwars_data[
        "two_four_beds_broken_bedwars"] if "two_four_beds_broken_bedwars" in bedwars_data else 0
    two_four_wins_bedwars = bedwars_data["two_four_wins_bedwars"] if "two_four_wins_bedwars" in bedwars_data else 0
    two_four_games_played_bedwars = bedwars_data[
        "two_four_games_played_bedwars"] if "two_four_games_played_bedwars" in bedwars_data else 0

    data = {
        "total_challenges_completed": total_challenges_completed,
        "games_played_bedwars": games_played_bedwars,
        "deaths_bedwars": deaths_bedwars,
        "wins_bedwars": wins_bedwars,
        "final_kills_bedwars": final_kills_bedwars,
        "final_deaths_bedwars": final_deaths_bedwars,
        "eight_one_final_kills_bedwars": eight_one_final_kills_bedwars,
        "eight_one_kills_bedwars": eight_one_kills_bedwars,
        "eight_one_beds_broken_bedwars": eight_one_beds_broken_bedwars,
        "eight_one_wins_bedwars": eight_one_wins_bedwars,
        "eight_one_games_played_bedwars": eight_one_games_played_bedwars,
        "eight_two_final_kills_bedwars": eight_two_final_kills_bedwars,
        "eight_two_kills_bedwars": eight_two_kills_bedwars,
        "eight_two_beds_broken_bedwars": eight_two_beds_broken_bedwars,
        "eight_two_wins_bedwars": eight_two_wins_bedwars,
        "eight_two_games_played_bedwars": eight_two_games_played_bedwars,
        "four_three_final_kills_bedwars": four_three_final_kills_bedwars,
        "four_three_kills_bedwars": four_three_kills_bedwars,
        "four_three_beds_broken_bedwars": four_three_beds_broken_bedwars,
        "four_three_wins_bedwars": four_three_wins_bedwars,
        "four_three_games_played_bedwars": four_three_games_played_bedwars,
        "four_four_final_kills_bedwars": four_four_final_kills_bedwars,
        "four_four_kills_bedwars": four_four_kills_bedwars,
        "four_four_beds_broken_bedwars": four_four_beds_broken_bedwars,
        "four_four_wins_bedwars": four_four_wins_bedwars,
        "four_four_games_played_bedwars": four_four_games_played_bedwars,
        "two_four_final_kills_bedwars": two_four_final_kills_bedwars,
        "two_four_kills_bedwars": two_four_kills_bedwars,
        "two_four_beds_broken_bedwars": two_four_beds_broken_bedwars,
        "two_four_wins_bedwars": two_four_wins_bedwars,
        "two_four_games_played_bedwars": two_four_games_played_bedwars
    }

    return data


async def get_week_number(date_string=None):
    # Use today's date if no date is provided
    if date_string is None:
        date_obj = datetime.now()
    else:
        # Define the date format
        date_format = "%Y-%m-%d %H:%M:%S.%f"

        # Parse the input date string
        date_obj = datetime.strptime(date_string, date_format)

    if date_obj.month == 1 and date_obj.day == 16:
        return -1

    # Define the week boundaries
    week_boundaries = [
        (datetime(date_obj.year, 12, 15), datetime(date_obj.year, 12, 21, 23, 59, 59)),
        (datetime(date_obj.year, 12, 22), datetime(date_obj.year, 12, 28, 23, 59, 59)),
        (datetime(date_obj.year, 12, 29), datetime(date_obj.year + (date_obj.month == 12), 1, 4, 23, 59, 59)),
        (datetime(date_obj.year, 1, 5), datetime(date_obj.year, 1, 11, 23, 59, 59))
    ]

    # Determine the week number
    for week_num, (start_date, end_date) in enumerate(week_boundaries, start=1):
        if start_date <= date_obj <= end_date:
            return week_num
    return None  # Return None if the date doesn't fall into any specified week


async def set_tourney_data(uuid):
    week_number = await get_week_number()
    if not week_number:
        return

    player_exists = await select_one("SELECT * FROM tournament WHERE uuid = (?)",
                                     (uuid,))

    if not player_exists:
        player_data = await get_hypixel_player(uuid=uuid)
        start_data = await get_game_data(player_data)

        await new_tournament_player(uuid, start_data, start_data, week_number)

    if player_exists:
        week1_exists = any(await select_one("SELECT week1_data FROM tournament WHERE uuid = (?)",
                                            (uuid,)))
        week2_exists = any(await select_one("SELECT week2_data FROM tournament WHERE uuid = (?)",
                                            (uuid,)))
        week3_exists = any(await select_one("SELECT week3_data FROM tournament WHERE uuid = (?)",
                                            (uuid,)))

        if (week_number == 1) and not week1_exists:
            player_data = await get_hypixel_player(uuid=uuid)
            week1_data = await get_game_data(player_data)
            await set_weekly_data(uuid, week1_data, week_number)

        elif (week_number == 2) and not week2_exists:
            player_data = await get_hypixel_player(uuid=uuid)
            week2_data = await get_game_data(player_data)
            await set_weekly_data(uuid, week2_data, week_number)

        elif (week_number == 3) and not week3_exists:
            player_data = await get_hypixel_player(uuid=uuid)
            week3_data = await get_game_data(player_data)
            await set_weekly_data(uuid, week3_data, week_number)

        elif week_number == 4 and week3_exists:
            player_data = await get_hypixel_player(uuid=uuid)
            week3_end_data = await get_game_data(player_data)
            await set_weekly_data(uuid, week3_end_data, week_number)

        elif week_number == -1:
            player_data = await get_hypixel_player(uuid=uuid)
            end_data = await get_game_data(player_data)
            await set_weekly_data(uuid, end_data, week_number)

async def update_recent_data(uuid):
    player_data = await get_hypixel_player(uuid=uuid)
    if not player_data:
        return None
    await update_recent(uuid, player_data)
