import discord

import src.utils.ui_utils as uiutils
from src.utils.consts import neutral_color, ticket_categories
from src.utils.minecraft_utils import get_guild_level
from src.utils.request_utils import get_player_guild


async def organize_gvg(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str, uuid: str):
    await ticket.edit(name=f"gvg-request-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["generic"]))
    guild = await get_player_guild(uuid)
    fields = []
    if not guild:
        fields.extend(
            [["What is the name of your guild?", "", discord.InputTextStyle.short, "Guild Name"]])
        embed = discord.Embed(title="GvG Request", color=neutral_color)
    else:
        embed = discord.Embed(
            title=f"{ign} wishes to organize a GvG with Miscellaneous on behalf of {guild['name']}",
            description=f"Guild Level: {await get_guild_level(guild['exp'])}",
            color=neutral_color)
    fields.extend(
        [["What are your preferred gamemodes", "", discord.InputTextStyle.short, "Gamemode(s)"],
         ["Do you have any special rules?", "", discord.InputTextStyle.long, "Rule(s)"],
         ["Number of Players", "", discord.InputTextStyle.short, "Number of Players"],
         ["Time & Timezone", "", discord.InputTextStyle.short, "Time & Timezone"]])
    await interaction.response.send_modal(
        modal=uiutils.ModalCreator(embed=embed, fields=fields, ign=ign, title="GvG Request"))
