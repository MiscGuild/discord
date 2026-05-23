import discord

from src.utils.ui_utils import DesignerBuilder


async def problem(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"problem-{ign}")
    builder = (
        DesignerBuilder(timeout=None)
        .container()
        .text(f"# <@{user.id}> has a problem!")
        .text(f"IGN: `{ign}`")
        .text("## Please elaborate on your problem so that the staff team can help you out!")
        .text("-# The staff team will try their best to assist you with your query within a couple hours.")
        .end()
    )
    await ticket.send(view=builder.build())
