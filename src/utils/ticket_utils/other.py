import discord

from src.utils.consts import TICKET_CATEGORIES, NEUTRAL_COLOR


async def other(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str,
                uuid: str):
    await ticket.edit(name=f"other-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=TICKET_CATEGORIES["generic"]))
    await ticket.send(embed=discord.Embed(title="This ticket has been created for an unknown reason!",
                                          description="Please specify why you have created this ticket!",
                                          color=NEUTRAL_COLOR))
