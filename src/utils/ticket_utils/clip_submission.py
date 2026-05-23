from __main__ import bot

import discord

from src.utils.consts import CLIP_SUBMISSION_TICKET
from src.utils.ui_utils import DesignerBuilder


async def clip_submission(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member,
                          ign: str):
    await ticket.edit(name=f"YT-clip-{ign}",
                      category=bot.TICKET_CATEGORY_IDS["milestone"])
    await ticket.set_permissions(bot.yt_channel_manager, send_messages=True, read_messages=True,
                                 add_reactions=True, embed_links=True,
                                 attach_files=True,
                                 read_message_history=True, external_emojis=True)
    await ticket.purge(limit=100)
    builder = (
        DesignerBuilder(timeout=None)
        .container()
        .text(CLIP_SUBMISSION_TICKET.format(name=ign))
        .end()
    )
    await ticket.send(view=builder.build())
