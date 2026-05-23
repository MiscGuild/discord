import discord

from src.utils.ui_utils import DesignerBuilder


async def rank_upgrade(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"rank-upgrade-{ign}")

    builder = (
        DesignerBuilder(timeout=None)
        .container()
        .text(f"# <@{user.id}> claims to have won a rank upgrade!")
        .text(f"IGN: `{ign}`")
        .text("## Please provide the following information to help us verify your claim:")
        .text("- The date you won the rank upgrade (if you remember).")
        .text("- The name of the event or competition where you won the rank upgrade (if applicable).")
        .text("- Any screenshots or evidence you have of winning the rank upgrade.")
        .text(
            "-# The staff team will review your claim and the provided information. If everything checks out, you will receive your rank upgrade within a month!")
        .end()
    )

    await ticket.send(view=builder.build())
