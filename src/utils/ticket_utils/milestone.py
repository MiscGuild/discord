import discord

from src.utils.consts import NEUTRAL_COLOR, TICKET_CATEGORIES


async def milestone(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"milestone-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=TICKET_CATEGORIES[
                                                     "milestone"]))
    await ticket.send(embed=discord.Embed(title=f"{ign} would like to register a milestone!",
                                          description="Please provide a small description and proof of your milestone!\nIf your milestone is approved, it'll be included in next week's milestone post!",
                                          color=NEUTRAL_COLOR))
