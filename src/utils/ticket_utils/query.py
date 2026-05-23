import discord

from src.utils.ui_utils import DesignerBuilder


async def query(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"query-{ign}")

    builder = (
        DesignerBuilder(timeout=None)
        .container()
        .text(f"# <@{user.id}> has a query!")
        .text(f"IGN: `{ign}`")
        .text("## Please elaborate on your query so that the staff team can help you out!")
        .text("-# The staff team will try their best to assist you with your query within a couple hours.")
        .end()
    )
    await ticket.send(view=builder.build())
