import discord

from src.utils.consts import NEUTRAL_COLOR, TICKET_CATEGORIES


async def problem(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"problem-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=TICKET_CATEGORIES["generic"]))
    await ticket.send(embed=discord.Embed(title=f"{ign} has a problem!",
                                          description="Please elaborate on your"
                                                      "problem so that the staff team can help you out!",
                                          color=NEUTRAL_COLOR))
