from __main__ import bot

import discord

from src.utils.consts import REQUIREMENTS_TEXT
from src.utils.ui_utils import DesignerBuilder


async def join_guild(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    # Edit category and send info embed with requirements
    await ticket.edit(name=f"join-request-{ign}",
                      category=bot.TICKET_CATEGORY_IDS["registrees"])
    await ticket.purge(limit=100)
    builder = (
        DesignerBuilder(timeout=None)
        .container()
        .text(f"# <@{user.id}> wishes to join Miscellaneous!")
        .text(f"IGN: `{ign}`")
        .text("## Requirements")
        .text(REQUIREMENTS_TEXT)
        .text(
            "If you don't think you can meet the requirements, we'd recommend still applying. Worst case scenario, you get kicked for inactivity after a week or so, and you can always reapply later when you think you meet the requirements.")
        .text(
            "-# Please be patient while the staff team reviews your request. We will try to get back to you within a couple hours, but it may take longer during busy periods.")
        .end()
    )
    await ticket.send(view=builder.build())
