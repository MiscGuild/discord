from __main__ import bot

import discord

from src.utils.consts import JOIN_REQUEST_EMBED


async def join_guild(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    # Edit category and send info embed with requirements
    await ticket.edit(name=f"join-request-{ign}",
                      category=bot.TICKET_CATEGORY_IDS["registrees"])
    await ticket.purge(limit=100)
    await ticket.send(
        embed=JOIN_REQUEST_EMBED.set_author(name=f"{ign} wishes to join Miscellaneous"))
