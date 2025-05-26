import discord

import src.utils.ui_utils as uiutils
from src.utils.consts import neutral_color, ticket_categories


async def player_report(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str, uuid: str):
    await ticket.edit(name=f"report-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["generic"]))
    fields = [
        ["What was the username of the accused", "", discord.InputTextStyle.short,
         "Username of the accused"],
        ["What was the offense?", "", discord.InputTextStyle.short, "Offense"],
        ["When did this happen?", "", discord.InputTextStyle.short, "Time of Offense"],
        ["Provide a brief description of what happened.",
         "Answer the question in no more than 100 words.",
         discord.InputTextStyle.long, "Description"]
    ]
    embed = discord.Embed(title="Player Report", color=neutral_color)
    await interaction.response.send_modal(
        modal=uiutils.ModalCreator(embed=embed, fields=fields, ign=ign, uuid=uuid,
                                   title="Player Report"))

    await ticket.edit(name=f"report-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=ticket_categories["generic"]))
