from __main__ import bot

import discord
import discord.ui as ui
from discord.ext import tasks

from src.utils.consts import (config, log_channel_id, neutral_color, ticket_categories,
                              guild_handle)
from src.utils.db_utils import check_uuid_in_db
from src.utils.request_utils import get_mojang_profile
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
    discord = player_data["socialMedia"]["links"]["DISCORD"]

    return (discord == str(user)[:-2]) or (discord == (str(user.id) + "#0000") or (discord == str(user)))


async def get_ticket_creator(channel: discord.TextChannel):
    return bot.guild.get_member(int(channel.topic.split("|")[0]))


async def create_ticket(user: discord.Member, ticket_name: str, category_name: str = ticket_categories["generic"]):
    # Create ticket
    ticket: discord.TextChannel = await bot.guild.create_text_channel(ticket_name,
                                                                      category=discord.utils.get(bot.guild.categories,
                                                                                                 name=category_name))
    # Set perms
    await ticket.set_permissions(bot.guild.get_role(bot.guild.id), send_messages=False,
                                 read_messages=False)
    await ticket.set_permissions(bot.discord_mod, send_messages=True, read_messages=True,
                                 add_reactions=True, embed_links=True,
                                 attach_files=True,
                                 read_message_history=True, external_emojis=True)
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
                                 add_reactions=True, embed_links=True,
                                 attach_files=True,
                                 read_message_history=True, external_emojis=True)
    if category_name != ticket_categories["registrees"]:
        # Send the dropdown for ticket creation
        class TicketTypeSelect(ui.Select):
            def __init__(self):
                super().__init__()

                if bot.guest in user.roles:
                    self.add_option(label=f"I want to join {guild_handle}", emoji="<:Misc:540990817872117780>")
                    self.add_option(label=f"I want to organize a GvG with {guild_handle}", emoji="⚔️")
                    self.add_option(label=f"My guild wishes to ally {guild_handle}", emoji="🤝")

                # Add milestone, DNKL application, staff application, GvG application if user is a member
                if bot.member_role in user.roles:
                    self.add_option(label="Register a milestone", emoji="🏆")
                    self.add_option(label="I am going to be inactive", emoji="<:dnkl:877657298703634483>")
                    self.add_option(label="I want to join the GvG team", emoji="⚔️")

                # Add default options
                self.add_option(label="I want to join the staff team", emoji="🤵")
                self.add_option(label="Report a player", emoji="🗒️")
                self.add_option(label="Query/Problem", emoji="🤔")

                # Add "Other" option last
                self.add_option(label="Other", emoji="❓")

            # Override default callback
            async def callback(self, interaction: discord.Interaction):
                ign, uuid = await get_mojang_profile(await name_grabber(interaction.user))
                # Set option var and delete Select so it cannot be used twice
                option = list(interaction.data.values())[0][0]
                await ticket.purge(
                    limit=100)  # Deleting the interaction like this so that we can respond to the interaction later

                # Logic for handling ticket types
                if option == "Report a player":
                    await player_report(ticket, interaction, ign, uuid)
                if option == "Query/Problem":
                    await query(ticket, interaction, ign)
                if option == "Register a milestone":
                    await milestone(ticket, interaction, ign)
                if option == "I am going to be inactive":
                    await dnkl(ticket, interaction, ign, uuid)
                if option == "I want to join the staff team":
                    await staff_application(ticket, interaction, ign)
                if option == "I want to join the GvG team":
                    await gvg_application(ticket, interaction, ign, uuid, user)
                if option == f"I want to join {guild_handle}":
                    await join_guild(ticket, interaction, ign)
                if option == f"I want to organize a GvG with {guild_handle}":
                    await organize_gvg(ticket, interaction, ign, uuid)
                if option == f"My guild wishes to ally  {guild_handle}":
                    await ally_request(ticket, interaction, ign, uuid)
                if option == "Other":
                    await other(ticket, interaction, ign, uuid)

        # Create view and embed, send to ticket
        view = discord.ui.View()
        view.add_item(TicketTypeSelect())
        embed = discord.Embed(title="Why did you make this ticket?",
                              description="Please select your reason from the dropdown given below!",
                              color=neutral_color)
        await ticket.send(embed=embed, view=view)

    # Return ticket for use
    return ticket


async def log_event(title: str, description: str = None):
    embed = discord.Embed(title=title, description=description, color=neutral_color)
    await bot.get_channel(log_channel_id).send(embed=embed)


async def has_tag_perms(user: discord.User):
    return any(role in user.roles for role in bot.tag_allowed_roles)


async def update_recruiter_role(uuid: str, invites: int):
    user_id = await check_uuid_in_db(uuid)
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




@tasks.loop(count=1)
async def after_cache_ready():
    # Set owner id(s) and guild
    bot.owner_ids = config["owner_ids"]
    bot.guild = bot.get_guild(config["guild_id"])

    # Set roles
    bot.admin = discord.utils.get(bot.guild.roles, name="Admin")
    bot.staff = discord.utils.get(bot.guild.roles, name="Staff")
    bot.helper = discord.utils.get(bot.guild.roles, name="Helper")
    bot.discord_mod = discord.utils.get(bot.guild.roles, name="Discord Moderator")
    bot.former_staff = discord.utils.get(bot.guild.roles, name="Former Staff")
    bot.new_member_role = discord.utils.get(bot.guild.roles, name="New Member")
    bot.processing = discord.utils.get(bot.guild.roles, name="Processing")
    bot.guest = discord.utils.get(bot.guild.roles, name="Guest")
    bot.member_role = discord.utils.get(bot.guild.roles, name="Member")
    bot.active_role = discord.utils.get(bot.guild.roles, name="Active")
    bot.ally = discord.utils.get(bot.guild.roles, name="Ally")
    bot.server_booster = discord.utils.get(bot.guild.roles, name="Server Booster")
    bot.rich_kid = discord.utils.get(bot.guild.roles, name="Rich Kid")
    bot.gvg = discord.utils.get(bot.guild.roles, name="GvG Team")
    bot.giveaways_events = discord.utils.get(bot.guild.roles, name="Giveaways/Events")
    bot.veteran = discord.utils.get(bot.guild.roles, name="Veteran")
    bot.tag_allowed_roles = (bot.active_role, bot.staff, bot.former_staff,
                             bot.server_booster, bot.rich_kid, bot.gvg, bot.veteran)

    from src.utils.discord_utils import name_grabber
    bot.staff_names = [(await get_mojang_profile(await name_grabber(member)))[0] for member in bot.staff.members]

    from src.utils.loop_utils import check_giveaways, send_gexp_lb, update_invites
    check_giveaways.start()
    send_gexp_lb.start()
    update_invites.start()


@after_cache_ready.before_loop
async def before_cache_loop():
    print("Waiting for cache...")
    await bot.wait_until_ready()
    print("Cache filled")
