from __main__ import bot

import discord

from src.utils.ui_utils import DesignerBuilder


async def other(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str,
                uuid: str):
    await ticket.edit(name=f"other-{ign}",
                      category=bot.TICKET_CATEGORY_IDS["other"])
    builder = (
        DesignerBuilder(timeout=None)
        .container()
        .text(f"# <@{user.id}> has created a ticket for an unknown reason!")
        .text(f"IGN: `{ign}`")
        .text("## Please tell us more about your issue or query so that the staff team can help you out!")
        .text("-# The staff team will try their best to assist you with your query within a couple hours.")
        .end()
    )
    await ticket.send(view=builder.build())
