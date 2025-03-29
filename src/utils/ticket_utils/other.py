import discord

from src.utils.consts import ticket_categories, neutral_color


async def other(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str, uuid: str):
    await ticket.edit(name=f"other-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["generic"]))
    await ticket.send(embed=discord.Embed(title="This ticket has been created for an unknown reason!",
                                          description="Please specify why you have created this ticket!",
                                          color=neutral_color))
