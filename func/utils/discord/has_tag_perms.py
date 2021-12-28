from __main__ import bot
import discord

async def has_tag_perms(user: discord.User):
    return any(role in user.roles for role in bot.tag_allowed_roles)
