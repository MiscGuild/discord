# The following file includes: name_grabber, log_event, has_tag_perms, check_tag, get_giveaway_status, roll_giveaway

from datetime import datetime, timedelta
from re import T
import discord
from __main__ import bot

from func.utils.consts import neutral_color


# Return user's displaying name
async def name_grabber(author: discord.User):
    if not author.nick:
        return author.name
    return author.nick.split()[0]


# Log a given event in logging channel
async def log_event(title: str, description: str):
    embed = discord.Embed(title=title, description=description, color=neutral_color)
    await bot.log_channel.send(embed=embed)


# Return if user can change their tag
async def has_tag_perms(user: discord.User):
    return any(role in user.roles for role in bot.tag_allowed_roles)


# Check tag for
async def check_tag(tag: str):
    tag = tag.lower()
    with open("badwords.txt", "r") as f:
        badwords = f.read()

    if tag in badwords.split("\n"):
        return False, "Your tag may not include profanity."
    elif not tag.isascii():
        return False, "Your tag may not include special characters unless it's the tag of an ally guild."
    elif len(tag) > 6:
        return False, "Your tag may not be longer than 6 characters."
    # Tag is okay to use
    return True, None


# Get the activity status of a giveaway
async def get_giveaway_status(id: int):
    cursor = await bot.db.execute("SELECT status FROM giveaways WHERE message_id = (?)", (id,))
    row = await cursor.fetchone()
    await cursor.close()
    return row


# Roll a giveaway
async def roll_giveaway(reroll_target: int = None):
    return True


# Returns if a string is a valid and parseable to a date
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
