import discord

from src.utils.consts import NEUTRAL_COLOR


async def query(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str):
    await ticket.edit(name=f"query-{ign}")
    await ticket.send(embed=discord.Embed(title=f"{ign} has a query!",
                                          description="Please elaborate on your "
                                                      "query so that the staff team can help you out!",
                                          color=NEUTRAL_COLOR))
