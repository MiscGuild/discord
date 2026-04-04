from __main__ import bot

import discord

from src.utils.consts import NEUTRAL_COLOR


async def other(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str,
                uuid: str):
    await ticket.edit(name=f"other-{ign}",
                      category=bot.TICKET_CATEGORY_IDS["other"])
    await ticket.send(embed=discord.Embed(title="This ticket has been created for an unknown reason!",
                                          description="Please specify why you have created this ticket!",
                                          color=NEUTRAL_COLOR))
