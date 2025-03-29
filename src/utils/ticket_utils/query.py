import discord

from src.utils.consts import neutral_color, ticket_categories


async def query(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str):
    await ticket.edit(name=f"query-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["generic"]))
    await ticket.send(embed=discord.Embed(title=f"{ign} has a query!",
                                          description="Please elaborate on your"
                                                      "query so that the staff team can help you out!",
                                          color=neutral_color))
