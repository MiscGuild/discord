import discord

from src.utils.consts import NEUTRAL_COLOR, TICKET_CATEGORIES


async def rank_upgrade(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"rank-upgrade-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=TICKET_CATEGORIES[
                                                     "generic"]))
    await ticket.send(embed=discord.Embed(title=f"{ign} claims to have won a rank upgrade.",
                                          description="Please provide a link to a message saying you won a rank upgrade.",
                                          color=NEUTRAL_COLOR).set_footer(
        text="You might have to wait up to a month to receive your rank upgrade!"))
