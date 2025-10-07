from __main__ import bot
from typing import Optional

import discord
import discord.ui as ui
from discord.ext import tasks

from src.utils.calculation_utils import get_qotd_day_number
from src.utils.consts import (config, log_channel_id, neutral_color, ticket_categories,
                              guest_ticket_reasons, member_ticket_reasons, general_ticket_reasons, guild_handle,
                              qotd_thread_id, geoguessr_thread_id, spoilers_ahead)
from src.utils.db_utils import connect_db, get_db_uuid_username
from src.utils.request_utils import get_uuid_by_name
from src.utils.ticket_utils import *
from src.utils.ticket_utils.tickets import name_grabber


async def is_linked_discord(player_data: dict, user: discord.User) -> bool:
    if not player_data:
        return False
    if "socialMedia" not in player_data:
        return False
    if not player_data["socialMedia"]:
        return False
    if "links" not in player_data["socialMedia"]:
        return False
    if not player_data["socialMedia"]["links"]:
        return False
    if "DISCORD" not in player_data["socialMedia"]["links"]:
        return False
    player_discord = player_data["socialMedia"]["links"]["DISCORD"]

    return (player_discord == str(user)[:-2]) or (
            player_discord == (str(user.id) + "#0000") or (player_discord == str(user)))


async def get_ticket_creator(channel: discord.TextChannel) -> discord.Member:
    return bot.guild.get_member(int(channel.topic.split("|")[0]))


async def create_ticket(user: discord.Member, ticket_name: str,
                        category_name: str = ticket_categories["generic"], reason: str = None,
                        ctx=None) -> discord.TextChannel:
    # Create ticket
    ticket: discord.TextChannel = await bot.guild.create_text_channel(ticket_name,
                                                                      category=discord.utils.get(bot.guild.categories,
                                                                                                 name=category_name))
    # Set perms
    await ticket.set_permissions(bot.guild.get_role(bot.guild.id), send_messages=False,
                                 read_messages=False)
    await ticket.set_permissions(bot.staff, send_messages=True, read_messages=True,
                                 add_reactions=True, embed_links=True,
                                 attach_files=True,
                                 read_message_history=True, external_emojis=True)
    await ticket.set_permissions(bot.helper, send_messages=True,
                                 read_messages=True,
                                 add_reactions=True, embed_links=True,
                                 attach_files=True,
                                 read_message_history=True, external_emojis=True)
    await ticket.set_permissions(user, send_messages=True, read_messages=True,
                                 add_reactions=True, embed_links=True,
                                 attach_files=True,
                                 read_message_history=True, external_emojis=True)
    await ticket.set_permissions(bot.new_member_role, send_messages=False,
                                 read_messages=False,
                                 add_reactions=False, embed_links=False,
                                 attach_files=False,
                                 read_message_history=False, external_emojis=False)
    if reason:
        await handle_ticket_reason(reason, ticket, interaction=None, user=user, ctx=ctx)
    elif category_name != ticket_categories["registrees"]:
        await send_ticket_dropdown(ticket, user, ctx)

    # Return ticket for use
    return ticket


async def send_ticket_dropdown(ticket: discord.TextChannel, user: discord.Member, ctx=None) -> None:
    # Send the dropdown for ticket creation
    class TicketTypeSelect(ui.Select):
        def __init__(self):
            super().__init__()

            if bot.guest in user.roles:
                for key, value in guest_ticket_reasons.items():
                    self.add_option(label=key, emoji=value)

            # Add milestone, DNKL application, staff application, GvG application if user is a member
            if bot.member_role in user.roles:
                for key, value in member_ticket_reasons.items():
                    self.add_option(label=key, emoji=value)

            # Add default options
            for key, value in general_ticket_reasons.items():
                self.add_option(label=key, emoji=value)

        # Override default callback
        async def callback(self, interaction: discord.Interaction):
            ign, uuid = await get_uuid_by_name(await name_grabber(interaction.user))
            # Set option var and delete Select so it cannot be used twice
            option = list(interaction.data.values())[0][0]
            await ticket.purge(
                limit=100)  # Deleting the interaction like this so that we can respond to the interaction later
            await handle_ticket_reason(option, ticket, interaction, user, ctx)

    # Create view and embed, send to ticket
    view = discord.ui.View()
    view.add_item(TicketTypeSelect())
    embed = discord.Embed(title="Why did you make this ticket?",
                          description="Please select your reason from the dropdown given below!",
                          color=neutral_color)
    await ticket.send(embed=embed, view=view)


async def handle_ticket_reason(reason: str, ticket: discord.TextChannel,
                               interaction: Optional[discord.Interaction], user: discord.Member, ctx=None) -> None:
    ign, uuid = await get_uuid_by_name(await name_grabber(user))

    reason = reason.lower().replace(" ", "_").replace("-", "_").replace("'", "").replace("!", "").replace("?", "")

    if "report" in reason:
        if interaction:
            await player_report(ticket, interaction, user, ign, uuid)
        else:
            await ticket.send(
                "⚠️ This ticket reason is only available through the following dropdown.")
            await send_ticket_dropdown(ticket, user, ctx)
    elif "question" in reason:
        await query(ticket, interaction, user, ign)
    elif "milestone" in reason:
        await milestone(ticket, interaction, user, ign)
    elif "inactive" in reason or "dnkl" in reason:
        await dnkl(ticket, interaction, user, ign, uuid)
    elif "rank_upgrade" in reason:
        await rank_upgrade(ticket, interaction, user, ign)
    elif "staff" in reason:
        await staff_application(ticket, interaction, user, ign)
    elif "gvg_team" in reason:
        await gvg_application(ticket, interaction, ign, uuid, user)
    elif "join_guild" in reason or f"join_{guild_handle.lower()}" in reason:
        await join_guild(ticket, interaction, user, ign)
    elif "organize_gvg" in reason or "organize_a_gvg" in reason:
        if interaction:
            await organize_gvg(ticket, interaction, user, ign, uuid)
        else:
            await ticket.send(
                "⚠️ This ticket reason is only available through the following dropdown.")
            await send_ticket_dropdown(ticket, user, ctx)
    elif "ally" in reason:
        if interaction:
            await ally_request(ticket, interaction, user, ign, uuid)
        else:
            await ticket.send(
                "⚠️ This ticket reason is only available through the following dropdown.")
            await send_ticket_dropdown(ticket, user, ctx)
    elif "problem" in reason:
        await problem(ticket, interaction, user, ign)
    elif "other" in reason:
        await other(ticket, interaction, user, ign, uuid)
    else:
        await ticket.send(
            "⚠️ Not a valid ticket reason! Please select a valid reason from the dropdown.")
        await send_ticket_dropdown(ticket, user, ctx)


async def log_event(title: str, description: str = None) -> None:
    embed = discord.Embed(title=title, description=description, color=neutral_color)
    await bot.get_channel(log_channel_id).send(embed=embed)


async def has_tag_perms(member: discord.Member) -> bool:
    return any(role in member.roles for role in bot.tag_allowed_roles)


async def update_recruiter_role(uuid: str, invites: int) -> None:
    _, _, user_id = await get_db_uuid_username(uuid=uuid, get_discord_id=True)
    if not user_id:
        return
    member_ids = [x.id for x in bot.guild.members]
    if user_id not in member_ids:
        return
    user = bot.guild.get_member(user_id)
    if invites > 5:
        await user.add_roles(bot.recruiter)
    else:
        await user.remove_roles(bot.recruiter)
    return


async def send_thread_message(thread: discord.Thread) -> None:
    if thread.parent.id == qotd_thread_id:
        day_number, day, month, year = await get_qotd_day_number()

        embed = discord.Embed(
            title=f"Question of the Day",
            description=f"**Day {day_number}**\n"
                        f"**Date:** {day} {month} {year}\n",
            color=neutral_color)
        await thread.send(f"<@&{bot.qotd.id}>", embed=embed)
    if thread.parent.id == geoguessr_thread_id:
        await thread.send(f"<@&{bot.geoguessr.id}> New GeoGuessr challenge posted!\n"
                          f"{spoilers_ahead}")


@tasks.loop(count=1)
async def after_cache_ready() -> None:
    await connect_db()

    # Set owner id(s) and guild
    bot.owner_ids = config["owner_ids"]
    bot.guild = bot.get_guild(config["guild_id"])
    # Set roles
    bot.admin = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["admin"])
    bot.staff = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["staff"])
    bot.helper = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["helper"])
    bot.former_staff = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["former_staff"])
    bot.new_member_role = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["new_member"])
    bot.processing = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["processing"])
    bot.guest = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["guest"])
    bot.member_role = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["member"])
    bot.active_role = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["active"])
    bot.ally = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["ally"])
    bot.server_booster = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["booster"])
    bot.rich_kid = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["sponsor"])
    bot.gvg = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["gvg_team"])
    bot.giveaways_events = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["giveaways"])
    bot.veteran = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["veteran"])
    bot.recruiter = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["recruiter"])
    bot.qotd = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["qotd_ping"])
    bot.geoguessr = discord.utils.get(bot.guild.roles, id=config["discord_roles"]["geoguessr"])
    bot.tag_allowed_roles = (bot.active_role, bot.staff, bot.former_staff,
                             bot.server_booster, bot.rich_kid, bot.gvg, bot.veteran, bot.recruiter)

    from src.utils.loop_utils import check_giveaways, before_scheduler
    check_giveaways.start()
    await before_scheduler()

    bot.staff_names = [(await get_uuid_by_name(await name_grabber(member)))[0] for member in
                       bot.staff.members]


@after_cache_ready.before_loop
async def before_cache_loop() -> None:
    print("Waiting for cache...")
    await bot.wait_until_ready()
    print("Cache filled")
