import io
import logging
import math
import re
import traceback
from calendar import month_name
from datetime import datetime, timedelta, timezone
from typing import Tuple, List

import discord
from discord.ext import commands

from src.utils.consts import ChatColor, NON_STAFF_RANKS, NOT_OWNER_EMBED, \
    MISSING_ROLES_EMBED, MISSING_PERMS_EMBED, MEMBER_NOT_FOUND_EMBED, BOT_MISSING_PERMS_EMBED, ERR_404_EMBED, \
    ERROR_REPLY_EXCEPTIONS
from src.utils.db_utils import get_do_ping, get_db_uuid_username, get_all_usernames
from src.utils.request_utils import get_player_guild, get_name_by_uuid


async def get_player_gexp(uuid: str, guild_data: dict = None) -> Tuple[dict, int, int] | Tuple[None, None, None]:
    if not guild_data:
        guild_data = await get_player_guild(uuid)

    # Player is in a guild
    if guild_data:
        for member in guild_data["members"]:
            if member["uuid"] == uuid:
                exp_history = member["expHistory"]
                weekly_gexp = sum(exp_history.values())
                days_in_guild = await get_days_in_guild(member["joined"])
                return exp_history, weekly_gexp, days_in_guild

    # Player is not in a guild
    return None, None, None


async def get_days_in_guild(joined: str) -> int:
    joined_ms = int(joined)

    joined_dt = datetime.fromtimestamp(joined_ms / 1000, tz=timezone.utc)

    now = datetime.now(tz=timezone.utc)

    days_in_guild = (now - joined_dt).days

    return days_in_guild


async def get_color_by_gexp(rank: str, weekly_gexp: int) -> Tuple[int, str, str]:
    if rank == NON_STAFF_RANKS[-1].name and weekly_gexp >= NON_STAFF_RANKS[-1].requirement:
        return 0x00fbff, "rgba(0,251,255, 0.3)", "rgba(0,251,255, 0.3)"

    if rank == NON_STAFF_RANKS[-2].name and weekly_gexp >= NON_STAFF_RANKS[-2].requirement:
        return 0x64ffb4, "rgba(100, 255, 180,0.3)", "rgba(100, 255, 180,0.3)"

    if rank == NON_STAFF_RANKS[-3].name and weekly_gexp > NON_STAFF_RANKS[-3].requirement:
        return 0x9c119c, "rgba(156, 17, 156,0.3)", "rgba(156, 17, 156,0.3)"

    return 0xff6464, "rgba(255, 100, 100,0.3)", "rgba(255, 100, 100,0.3)"


async def get_hypixel_player_rank(player_data: dict) -> Tuple[str, str] | Tuple[None, None]:
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


async def calculate_network_level(total_exp: int) -> float:
    return round((math.sqrt((2 * total_exp) + 30625) / 50) - 2.5, 2)


async def get_gexp_sorted(guild_data: dict) -> List[Tuple[str, int]]:
    member_gexp = {}

    # Loop through all guild members' gexp, adding it to dict
    for member in guild_data["members"]:
        member_gexp[member["uuid"]] = sum(
            member["expHistory"].values())
    # Sort member gexp
    member_gexp = sorted(member_gexp.items(), key=lambda item: item[1], reverse=True)

    return member_gexp


async def generate_lb_text(member_gexp: list, text: str, is_automatic) -> str:
    # Generate leaderboard text
    count = 0
    for uuid, gexp in member_gexp[:10]:
        count += 1

        discord_id, do_pings = await get_do_ping(uuid)
        username, uuid = await get_db_uuid_username(uuid=uuid)
        if discord_id and is_automatic and do_pings:
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
    # text = text.replace("+", "%2B").replace("&", "%26").replace(" ", "%20").replace(",", "%2C")

    # Return image
    return text


async def get_guild_level(exp) -> float | None:
    EXP_NEEDED = [100000, 150000, 250000, 500000, 750000, 1000000, 1250000, 1500000, 2000000, 2500000, 2500000, 2500000,
                  2500000, 2500000, 3000000]
    # A list of amount of XP required for leveling up in each of the beginning levels (1-15).

    level = 0

    for i in range(1000):
        if i >= len(EXP_NEEDED):
            need = EXP_NEEDED[len(EXP_NEEDED) - 1]
        else:
            need = EXP_NEEDED[i]

        if (exp - need) < 0:
            return round(((level + (exp / need)) * 100) / 100, 2)

        level += 1
        exp -= need

    return None


async def check_tag(tag: str) -> Tuple[bool, str] | Tuple[bool, None]:
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


async def is_valid_date(date: str) -> Tuple[bool, int, int, int] | Tuple[bool, None, None, None]:
    # Return False if parsing fails
    try:
        parsed = datetime.strptime(date, "%Y/%m/%d")
        # Validate time is within the last week
        if parsed < datetime.now(timezone.utc) - timedelta(days=7):
            return False, None, None, None
        return True, parsed.day, parsed.month, parsed.year
    except ValueError:
        return False, None, None, None


async def extract_usernames(message: str) -> Tuple[str, str] | Tuple[None, str]:
    words = message.split()
    ign_unfiltered = words[1]
    invitee_unfiltered = words[-1][:-1]

    # Define regular expressions for both formats
    bold = r"\*\*(.*?)\*\*"

    ign_format = re.match(bold, ign_unfiltered)
    ign = ign_format.group(1).replace("\\_", "_")

    invitee_format = re.match(bold, invitee_unfiltered)
    if not invitee_format:
        return None, ign
    inviter = invitee_format.group(1).replace("\\_", "_")

    return inviter, ign


async def get_guild_gexp_data(guild_data: dict) -> dict:
    members = {}
    for member in guild_data["members"]:
        members[member["uuid"]] = member["expHistory"]
    return members


async def check_if_mention(message: str) -> int | None:
    if not message:
        return None
    return int(message[2:-1]) if message.startswith("<@") and message.endswith(">") else None


async def get_monthly_gexp(gexp_data: dict) -> int:
    today = datetime.today()
    current_month_str = today.strftime("%Y-%m")  # e.g., "2025-05"

    monthly_gexp = {
        date: gexp for date, gexp in gexp_data.items()
        if date.startswith(current_month_str)
    }

    monthly_gexp_total = sum(monthly_gexp.values())

    return monthly_gexp_total


async def get_username_autocomplete(self, ctx: discord.AutocompleteContext):
    username_list = await get_all_usernames()  # Fetch all usernames (list of tuples)
    query = ctx.value.lower()
    filtered_usernames = [
        (value, name) for value, name in username_list if query in name.lower()
    ]
    return [discord.OptionChoice(name, value) for value, name in filtered_usernames[:25]]


async def get_qotd_day_number() -> Tuple[int, int, str, int]:
    return 473 + (datetime.now(timezone.utc) - datetime.strptime("2022/05/15", "%Y/%m/%d").replace(
        tzinfo=timezone.utc)).days, datetime.now(timezone.utc).day, month_name[
        datetime.now(timezone.utc).month], datetime.now(timezone.utc).year


def classify_error_embed(error: Exception) -> discord.Embed | None:
    """Return an embed appropriate to a known error type, else None."""

    if isinstance(error, commands.NotOwner):
        return NOT_OWNER_EMBED
    if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        return MISSING_ROLES_EMBED
    if isinstance(error, commands.MissingPermissions):
        return MISSING_PERMS_EMBED
    if isinstance(error, commands.MemberNotFound):
        return MEMBER_NOT_FOUND_EMBED
    if isinstance(error, discord.Forbidden):
        return BOT_MISSING_PERMS_EMBED
    if isinstance(error, discord.NotFound):
        return ERR_404_EMBED
    return None


async def safe_reply(ctx, **kwargs):
    """
    Reply in a way that works for both prefix and slash contexts.
    - ApplicationContext: use respond() if not yet responded; else send_followup()
    - commands.Context: use send()
    """
    try:
        if hasattr(ctx, "respond"):  # likely ApplicationContext
            if getattr(ctx, "responded", False):
                return await ctx.send_followup(**kwargs)
            else:
                return await ctx.respond(**kwargs)
        else:  # commands.Context
            return await ctx.send(**kwargs)
    except ERROR_REPLY_EXCEPTIONS:
        return None


def build_usage_embed(ctx) -> discord.Embed:
    """
    Conservative usage message that won’t break on slash commands.
    For prefix commands try to show signature; for slash, show the command mention if available.
    """
    title = "Invalid Syntax"
    try:
        if hasattr(ctx, "command") and hasattr(ctx.command, "signature"):  # commands.Context path
            prefix = getattr(ctx, "clean_prefix", "") or getattr(ctx, "prefix", "")
            usage = f"{prefix}{ctx.command.qualified_name} {ctx.command.signature}".strip()
            desc = f"Command usage:\n`{usage}`"
        else:
            name = getattr(ctx.command, "qualified_name", getattr(ctx.command, "name", "this command"))
            desc = f"Missing required argument(s) for `{name}`."
    except Exception:
        desc = "Missing or invalid arguments."

    return discord.Embed(title=title, description=desc, color=0xDE3163)


async def log_traceback_to_channel(bot: commands.Bot, channel_id: int, ctx, error: Exception):
    tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    channel = bot.get_channel(channel_id)
    if channel is None:
        logging.exception("Error in command %s (channel missing): %s", getattr(ctx, "command", "?"), tb)
        return
    try:
        header = f"Ignoring exception in command {getattr(ctx, 'command', '?')}:"
        if len(tb) <= 1900:
            await channel.send(f"{header}\n```py\n{tb}\n```")
        else:
            fp = io.BytesIO(tb.encode("utf-8"))
            await channel.send(content=header, file=discord.File(fp, filename="traceback.txt"))
    except ERROR_REPLY_EXCEPTIONS:
        logging.exception("Failed to send traceback to error channel:\n%s", tb)
