from __main__ import bot

import discord

from src.utils.consts import NEUTRAL_COLOR


async def milestone(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"milestone-{ign}",
                      category=bot.TICKET_CATEGORY_IDS["milestone"])
    await ticket.send(embed=discord.Embed(title=f"{ign} would like to register a milestone!",
                                          description="Please provide a small description and proof of your milestone!\nIf your milestone is approved, it'll be included in next week's milestone post!",
                                          color=NEUTRAL_COLOR))
