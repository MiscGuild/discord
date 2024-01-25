import discord

from src.utils.consts import neutral_color, ticket_categories, neg_color, unknown_ign_embed, dnkl_creation_embed, \
    dnkl_req
from src.utils.minecraft_utils import get_player_gexp


async def dnkl(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str, uuid: str):
    # Edit channel name and category
    await ticket.edit(name=f"dnkl-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["dnkl"]))

    # Notify user if they don't meet gexp req, however ask questions anyway
    _, weekly_gexp = await get_player_gexp(uuid)
    if weekly_gexp is None:
        return await ticket.send(embed=unknown_ign_embed)
    await ticket.send(embed=dnkl_creation_embed)
    if weekly_gexp < dnkl_req:
        await ticket.send(
            embed=discord.Embed(title="You do not meet the do-not-kick-list requirements!",
                                description=f"Even though you do not meet the requirements, "
                                            f"your application may still be accepted.\n"
                                            f"You have {format(weekly_gexp, ',d')} weekly guild experience!",
                                color=neg_color))
    else:
        await ticket.send(embed=discord.Embed(title="You meet the do-not-kick-list requirements!",
                                              description=f"You have {format(weekly_gexp, ',d')} weekly guild experience!",
                                              color=neutral_color))

    return weekly_gexp
