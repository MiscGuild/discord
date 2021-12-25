import discord

from __main__ import bot
from func.utils.consts import neutral_color

async def log_event(title: str, description: str):
    embed = discord.Embed(title=title, description=description, color=neutral_color)
    await bot.log_channel.send(embed=embed)