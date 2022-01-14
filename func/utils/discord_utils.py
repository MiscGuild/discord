# The following file includes: name_grabber, log_event, has_tag_perms, check_tag, get_giveaway_status, roll_giveaway

from __main__ import bot
import chat_exporter
from datetime import datetime, timedelta
import discord
from discord.ext import commands, tasks
import toml

from func.utils.consts import neutral_color


# Return user's displaying name
async def name_grabber(author: discord.User):
    if not author.nick:
        return author.name
    return author.nick.split()[0]


# Create a ticket with user's perms
async def create_ticket(category_name: str, ticket_name: str, user: discord.Member):
    # Create ticket
    ticket = await bot.guild.create_text_channel(ticket_name, category=discord.utils.get(bot.guild.categories, name=category_name))

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
                                            add_reactions=True, embed_links=True,
                                            attach_files=True,
                                            read_message_history=True, external_emojis=True)

    # Return ticket for use
    return ticket


# Log a given event in logging channel
async def log_event(title: str, description: str):
    embed = discord.Embed(title=title, description=description, color=neutral_color)
    await bot.log_channel.send(embed=embed)


# Return if user can change their tag
async def has_tag_perms(user: discord.User):
    return any(role in user.roles for role in bot.tag_allowed_roles)


# Check tag for
async def check_tag(tag: str):
    tag = tag.lower()
    with open("badwords.txt", "r") as f:
        badwords = f.read()

    if tag in badwords.split("\n"):
        return False, "Your tag may not include profanity."
    elif not tag.isascii():
        return False, "Your tag may not include special characters unless it's the tag of an ally guild."
    elif len(tag) > 6:
        return False, "Your tag may not be longer than 6 characters."
    # Tag is okay to use
    return True, None


# Roll a giveaway
async def roll_giveaway(reroll_target: int = None):
    return True


# Returns if a string is a valid and parseable to a date
async def is_valid_date(date: str):
    # Return False if parsing fails
    try:
        parsed = datetime.strptime(date, "%Y/%m/%d")
        # Validate time is within the last week
        if parsed < datetime.utcnow() - timedelta(days=7):
            return False, None, None, None
        return True, parsed.day, parsed.month, parsed.year
    except ValueError:
        return False, None, None, None


@tasks.loop(count=1)
async def after_cache_ready():
    config = toml.load("config.toml")

    # Set arbitrary values
    bot.api_tokens = config["hypixel"]["api_keys"]
    bot.owner_id = config["bot"]["ownerID"]
    bot.guild_name = config["bot"]["hypixel_guild_name"]
    bot.resident_req = 50000
    bot.active_req = 285000
    bot.member_req = 115000
    bot.dnkl = bot.member_req * 2
    bot.new_member = 20000

    # Set channels
    bot.error_channel = bot.get_channel(config["bot"]["error_channel_id"])
    bot.dnkl_channel = bot.get_channel(config["bot"]["dnkl_channel_id"])
    bot.ticket_channel = bot.get_channel(config["bot"]["ticket_channel_id"])
    bot.log_channel = bot.get_channel(config["bot"]["log_channel_id"])
    bot.registration_channel = bot.get_channel(config["bot"]["registration_channel_id"])
    bot.guild = bot.get_guild(config["bot"]["guild_id"])

    # Set roles
    bot.guild_master = discord.utils.get(bot.guild.roles, name="Guild Master")
    bot.admin = discord.utils.get(bot.guild.roles, name="Admin")
    bot.staff = discord.utils.get(bot.guild.roles, name="Staff")
    bot.helper = discord.utils.get(bot.guild.roles, name="Helper")
    bot.former_staff = discord.utils.get(bot.guild.roles, name="Former Staff")
    bot.new_member_role = discord.utils.get(bot.guild.roles, name="New Member")
    bot.guest = discord.utils.get(bot.guild.roles, name="Guest")
    bot.member_role = discord.utils.get(bot.guild.roles, name="Member")
    bot.active_role = discord.utils.get(bot.guild.roles, name="Active")
    bot.inactive_role = discord.utils.get(bot.guild.roles, name="Inactive")
    bot.awaiting_app = discord.utils.get(bot.guild.roles, name="Awaiting Approval")
    bot.ally = discord.utils.get(bot.guild.roles, name="Ally")
    bot.server_booster = discord.utils.get(bot.guild.roles, name="Server Booster")
    bot.rich_kid = discord.utils.get(bot.guild.roles, name="Rich Kid")
    bot.giveaways_events = discord.utils.get(bot.guild.roles, name="Giveaways/Events")
    bot.tag_allowed_roles = (bot.active_role, bot.staff, bot.former_staff, bot.server_booster, bot.rich_kid)

    # Set other names
    bot.ticket_categories = ("RTickets", "🎫 Ticket Section", "OTHER", "REPORTS", "MILESTONES", "DNKL")
    bot.misc_allies = ("XL", "Lucid", "Cronos", "OUT", "Betrayed", "Blight", "TheNinjaWarriors")

    from func.utils.discord_utils import name_grabber
    bot.admin_ids = [member.id for member in bot.admin.members]
    bot.admin_names = [await name_grabber(member) for member in bot.admin.members]
    bot.staff_names = [await name_grabber(member) for member in bot.staff.members]

    # Connect database and set tables
    from func.utils.db_utils import connect_db
    await connect_db()

    # Initialise chat_exporter
    chat_exporter.init_exporter(bot)

    # Set help command
    class HelpCommand(commands.MinimalHelpCommand):
        async def send_pages(self):
            destination = self.get_destination()
            for page in self.paginator.pages:
                embed = discord.Embed(description=page, color=neutral_color)
                await destination.send(embed=embed)

        async def send_command_help(self, command):
            embed = discord.Embed(title=self.get_command_signature(command), color=neutral_color)
            embed.add_field(name="Help", value=command.help)
            alias = command.aliases
            if alias:
                embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

            channel = self.get_destination()
            await channel.send(embed=embed)

    bot.help_command = HelpCommand(command_attrs={"hidden": True})

@after_cache_ready.before_loop
async def before_cache_loop():
    print("Waiting for cache...")
    await bot.wait_until_ready()
    print("Cache filled")
