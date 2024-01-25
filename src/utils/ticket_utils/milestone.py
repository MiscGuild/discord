import discord

from src.utils.consts import neutral_color, ticket_categories


async def milestone(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str):
    await ticket.edit(name=f"milestone-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories[
                                                     "milestone"]))
    await ticket.send(embed=discord.Embed(title=f"{ign} would like to register a milestone!",
                                          description="Please provide a small description and proof of your milestone!\nIf your milestone is approved, it'll be included in next week's milestone post!",
                                          color=neutral_color))
