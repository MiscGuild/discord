from __main__ import bot

import discord

from src.utils.consts import neutral_color, ticket_categories


async def join_guild(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    # Edit category and send info embed with requirements
    await ticket.edit(name=f"join-request-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=ticket_categories["registrees"]))
    await ticket.purge(limit=100)
    await ticket.send(
        embed=discord.Embed(title=f"{ign} wishes to join Miscellaneous!",
                            description=f"Please await staff assistance!\nIn the meanwhile, you may explore the Discord!",
                            color=neutral_color))
