from __main__ import bot

import discord

from src.utils.ui_utils import DesignerBuilder


async def milestone(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"milestone-{ign}",
                      category=bot.TICKET_CATEGORY_IDS["milestone"])
    builder = (
        DesignerBuilder(timeout=None)
        .container()
        .text(f"# <@{user.id}> would like to register a milestone!")
        .text(f"IGN: `{ign}`")
        .text("## Please tell us more about your milestone so that we can give you the recognition you deserve!")
        .text("Ensure to provide proof of your milestone (screenshots, links, etc.)!")
        .text(
            "-# Milestones can be anything from reaching a certain rank, winning a tournament, achieving a personal best, or any other significant achievement on Hypixel or in real-life!")
        .end()
    )
    await ticket.send(view=builder.build())
