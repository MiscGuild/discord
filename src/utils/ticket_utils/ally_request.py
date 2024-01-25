import discord

import src.utils.ui_utils as uiutils
from src.utils.calculation_utils import get_guild_level
from src.utils.consts import neutral_color, ticket_categories
from src.utils.request_utils import get_player_guild


async def ally_request(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str, uuid: str):
    await ticket.edit(name=f"alliance-request-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["generic"]))
    guild = await get_player_guild(uuid)
    fields = []

    if not guild:
        fields.extend(
            [["What is the name of your guild?", "", discord.InputTextStyle.short, "Guild Name"],
             ["What is your guild's level?", "", discord.InputTextStyle.short, "Guild Level"]])
        embed = discord.Embed(title="Alliance Request Request", color=neutral_color)
    else:
        embed = discord.Embed(
            title=f"{ign} wishes to ally with Miscellaneous on behalf of {guild['name']}",
            description=f"Guild Level: {await get_guild_level(guild['exp'])}",
            color=neutral_color)
    embed.set_footer(text="Please provide:\nGuild Logo\nGuild Advertisement Message")
    fields.extend(
        [["What is the IGN of your guild master?", "", discord.InputTextStyle.short, "Guild Master"],
         ["What is your guild's preferred gamemode?", "If you don't have one, just say 'None'",
          discord.InputTextStyle.short, "Guild's Preferred Gamemodes"],
         [f"Why should we ally with you guys?", "", discord.InputTextStyle.long,
          f"Benefits of allying with {guild['name']}"]])
    await interaction.response.send_modal(
        modal=uiutils.ModalCreator(embed=embed, fields=fields, ign=ign, uuid=uuid,
                                   title="Alliance Request"))
