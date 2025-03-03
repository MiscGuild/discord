import discord

from src.utils.consts import neutral_color, ticket_categories


async def rank_upgrade(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str):
    await ticket.edit(name=f"rank-upgrade-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories[
                                                     "generic"]))
    await ticket.send(embed=discord.Embed(title=f"{ign} claims to have won a rank upgrade.",
                                          description="Please provide a link to a message saying you won a rank upgrade.",
                                          color=neutral_color).set_footer(
        text="You might have to wait up to a month to receive your rank upgrade!"))
