from __main__ import bot

import discord

import src.utils.ui_utils as uiutils
from src.utils.calculation_utils import get_player_gexp
from src.utils.consts import neutral_color, ticket_categories, neg_color, unknown_ign_embed, dnkl_creation_embed, \
    dnkl_req, missing_permissions_embed, dnkl_channel_id
from src.utils.db_utils import insert_new_dnkl, update_dnkl, select_one, delete_dnkl
from src.utils.ticket_utils.tickets import close_ticket


async def dnkl_application(ign: str, uuid: str, channel: discord.TextChannel, author: discord.User,
                           weekly_gexp: int = None):
    YearView = discord.ui.View()
    buttons = (("Approve", "DNKL_Approve", discord.enums.ButtonStyle.green, dnkl_approve),
               ("Deny", "DNKL_Deny", discord.enums.ButtonStyle.red, dnkl_deny),
               ("Error", "DNKL_Error", discord.enums.ButtonStyle.gray, dnkl_error))
    YearView.add_item(uiutils.StartYearSelect(channel=channel, ign=ign, uuid=uuid,
                                              weekly_gexp=weekly_gexp, buttons=buttons))  # Year Selection Dropdown
    embed = discord.Embed(title=f"In which year will {ign}'s inactivity begin?",
                          color=neutral_color)
    await channel.send(embed=embed, view=YearView)


async def dnkl_error(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                     interaction: discord.Interaction):
    if bot.staff not in interaction.user.roles:
        await channel.send(embed=missing_permissions_embed)
        return None

    await interaction.response.send_message(embed=discord.Embed(
        title="Your application has been accepted, however there was an error!",
        description="Please await staff assistance!",
        color=neutral_color))
    return True


async def dnkl_deny(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                    interaction: discord.Interaction, self_denial: bool = False):
    if bot.staff not in interaction.user.roles and not self_denial:
        await channel.send(embed=missing_permissions_embed)
        return None

    if not self_denial:
        await interaction.response.send_message("**This user's do-not-kick-list application has been denied!.**\n"
                                                "If you didn't mean to hit deny, you can add them using `/dnkl_add`.",
                                                ephemeral=True)

        embed = discord.Embed(title="Your do-not-kick-list application has been denied!",
                              description=f"You do not meet the DNKL requirements of {format(dnkl_req, ',d')} weekly guild experience.",
                              color=neg_color)
        embed.set_footer(
            text="If don't you think you can meet the requirements, you may rejoin the guild once your inactivity period has ended.")

    closeView = discord.ui.View(timeout=None)  # View for staff members to approve/deny the DNKL
    button = ("Close This Ticket", "close_ticket", discord.enums.ButtonStyle.red)
    closeView.add_item(
        uiutils.Button_Creator(channel=channel, author=author, ign=ign, uuid=uuid, button=button,
                               function=close_ticket))
    await channel.send(embed=embed, view=closeView)
    await delete_dnkl(ign)

    return True


async def dnkl_approve(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                       interaction: discord.Interaction):
    if bot.staff not in interaction.user.roles:
        await channel.send(embed=missing_permissions_embed)
        return None

    msg = await bot.get_channel(dnkl_channel_id).send(embed=embed)

    # Check if user is already on DNKL
    current_message = await select_one("SELECT message_id FROM dnkl WHERE uuid = (?)",
                                       (uuid,))
    # User is not currently on DNKL
    if not current_message:
        await insert_new_dnkl(msg.id, uuid, ign)
        return await interaction.response.send_message("**This user has been added to the do-not-kick-list!**")

    # User is already on DNKl
    # Try to delete current message
    try:
        current_message = await bot.get_channel(dnkl_channel_id).fetch_message(
            current_message)
        await current_message.delete()
    except discord.NotFound:
        pass

    await update_dnkl(msg.id, uuid)
    await interaction.response.send_message(
        "**Since this user was already on the do-not-kick-list, their entry has been updated.**")

    return True



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

    await dnkl_application(ign, uuid, ticket, interaction.user, weekly_gexp)
