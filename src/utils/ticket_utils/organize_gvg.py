import discord

import src.utils.ui_utils as uiutils
from src.utils.calculation_utils import get_guild_level
from src.utils.consts import NEUTRAL_COLOR, TICKET_CATEGORIES, GUILD_HANDLE
from src.utils.request_utils import get_player_guild


async def organize_gvg(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str,
                       uuid: str):
    guild = await get_player_guild(uuid)
    fields = []
    if not guild:
        fields.extend(
            [["What is the name of your guild?", "", discord.InputTextStyle.short, "Guild Name"]])
        embed = discord.Embed(title="GvG Request", color=NEUTRAL_COLOR)
    else:
        embed = discord.Embed(
            title=f"{ign} wishes to organize a GvG with {GUILD_HANDLE} on behalf of {guild['name']}",
            description=f"Guild Level: {await get_guild_level(guild['exp'])}",
            color=NEUTRAL_COLOR)
    fields.extend(
        [["What are your preferred gamemodes", "", discord.InputTextStyle.short, "Gamemode(s)"],
         ["Do you have any special rules?", "", discord.InputTextStyle.long, "Rule(s)"],
         ["Number of Players", "", discord.InputTextStyle.short, "Number of Players"],
         ["Time & Timezone", "", discord.InputTextStyle.short, "Time & Timezone"]])
    await interaction.response.send_modal(
        modal=uiutils.ModalCreator(embed=embed, fields=fields, ign=ign, title="GvG Request", uuid=uuid))

    await ticket.edit(name=f"gvg-request-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=TICKET_CATEGORIES["generic"]))
