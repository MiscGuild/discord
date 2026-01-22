from __main__ import bot

import discord

import src.utils.ui_utils as uiutils
from src.utils.calculation_utils import get_player_gexp
from src.utils.consts import NEUTRAL_COLOR, TICKET_CATEGORIES, NEG_COLOR, UNKNOWN_IGN_EMBED, DNKL_CREATION_EMBED, \
    DNKL_REQ, MISSING_PERMS_EMBED, DNKL_CHANNEL_ID
from src.utils.db_utils import insert_new_dnkl, update_dnkl, select_one, delete_dnkl
from src.utils.ticket_utils.tickets import close_ticket


async def dnkl_application(ign: str, uuid: str, channel: discord.TextChannel, author: discord.User,
                           weekly_gexp: int = None, days_in_guild: int = None):
    YearView = discord.ui.View()
    buttons = (("Approve", "DNKL_Approve", discord.enums.ButtonStyle.green, dnkl_approve),
               ("Deny", "DNKL_Deny", discord.enums.ButtonStyle.red, dnkl_deny),
               ("Error", "DNKL_Error", discord.enums.ButtonStyle.gray, dnkl_error))
    YearView.add_item(uiutils.StartYearSelect(channel=channel, ign=ign, uuid=uuid,
                                              weekly_gexp=weekly_gexp, days_in_guild=days_in_guild,
                                              buttons=buttons))  # Year Selection Dropdown
    embed = discord.Embed(title=f"In which year will {ign}'s inactivity begin?",
                          color=NEUTRAL_COLOR)
    await channel.send(embed=embed, view=YearView)


async def dnkl_error(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                     interaction: discord.Interaction):
    if bot.staff not in interaction.user.roles:
        await channel.send(embed=MISSING_PERMS_EMBED)
        return None

    await interaction.response.send_message(embed=discord.Embed(
        title="Your application has been accepted, however there was an error!",
        description="Please await staff assistance!",
        color=NEUTRAL_COLOR))
    return True


async def dnkl_deny(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                    interaction: discord.Interaction, self_denial: bool = False):
    if bot.staff not in interaction.user.roles and not self_denial:
        await channel.send(embed=MISSING_PERMS_EMBED)
        return None

    if not self_denial:
        await interaction.response.send_message("**This user's do-not-kick-list application has been denied!.**\n"
                                                "If you didn't mean to hit deny, you can add them using `/dnkl_add`.",
                                                ephemeral=True)

        embed = discord.Embed(title="Your do-not-kick-list application has been denied!",
                              description=f"You do not meet the DNKL requirements of {format(DNKL_REQ, ',d')} weekly guild experience.",
                              color=NEG_COLOR)
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
        await channel.send(embed=MISSING_PERMS_EMBED)
        return None
    message = await interaction.response.send_message("Processing...")
    msg = await bot.get_channel(DNKL_CHANNEL_ID).send(embed=embed)

    # Check if user is already on DNKL
    current_message = (await select_one("SELECT message_id FROM dnkl WHERE uuid = (?)",
                                        (uuid,)))

    # User is not currently on DNKL
    if not current_message:
        await insert_new_dnkl(msg.id, uuid, ign)
        return await interaction.edit_original_response(content="**This user has been added to the do-not-kick-list!**")

    current_message = current_message[0]

    # User is already on DNKl
    # Try to delete current message
    try:
        current_message = await bot.get_channel(DNKL_CHANNEL_ID).fetch_message(
            current_message)
        await current_message.delete()
    except discord.NotFound:
        pass

    await update_dnkl(msg.id, uuid)
    await interaction.edit_original_response(
        content="**Since this user was already on the do-not-kick-list, their entry has been updated.**")

    return True


async def dnkl(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member, ign: str,
               uuid: str):
    # Edit channel name and category
    await ticket.edit(name=f"dnkl-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=TICKET_CATEGORIES["dnkl"]))

    # Notify user if they don't meet gexp req, however ask questions anyway
    _, weekly_gexp, days_in_guild = await get_player_gexp(uuid)
    if weekly_gexp is None:
        return await ticket.send(embed=UNKNOWN_IGN_EMBED)
    await ticket.send(embed=DNKL_CREATION_EMBED)
    if weekly_gexp < DNKL_REQ:
        await ticket.send(
            embed=discord.Embed(title="You do not meet the do-not-kick-list requirements!",
                                description=f"Even though you do not meet the requirements, "
                                            f"your application may still be accepted.\n"
                                            f"You have {format(weekly_gexp, ',d')} weekly guild experience!",
                                color=NEG_COLOR))
    else:
        await ticket.send(embed=discord.Embed(title="You meet the do-not-kick-list requirements!",
                                              description=f"You have {format(weekly_gexp, ',d')} weekly guild experience!",
                                              color=NEUTRAL_COLOR))

    await dnkl_application(ign, uuid, ticket, (interaction.user if interaction else user), weekly_gexp, days_in_guild)
