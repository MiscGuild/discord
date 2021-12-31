import aiosqlite
import chat_exporter
import discord
import logging
import sys
import toml
from discord.ext import commands, tasks

logging.basicConfig(level=logging.INFO)
config = toml.load("config.toml")

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config["bot"]["prefix"]), intents=intents,
                   status=discord.Status.idle, activity=discord.Game(config["bot"]["status"]), case_insensitive=True)

bot.config = config
bot.token = config["bot"]["token"]
bot.api_tokens = config["hypixel"]["api_keys"]
bot.owner_id = config["bot"]["ownerID"]
bot.guild_name = config["bot"]["hypixel_guild_name"]
bot.resident_req = 50000
bot.active_req = 285000
bot.member_req = 115000
bot.dnkl = bot.member_req * 2
bot.new_member = 20000


class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=0x8368ff)
            await destination.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=0x8368ff)
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


bot.help_command = HelpCommand(command_attrs={"hidden": True})

initial_extensions = ["func.cogs.general", "func.cogs.giveaways", "func.cogs.guild", "func.cogs.hypixel",
                      "func.cogs.listeners", "func.cogs.moderation", "func.cogs.owner"]

if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f"Loaded {extension}")
        except Exception as e:
            print(f"WARNING: Failed to load extention {extension}", file=sys.stderr)
            print(e)


async def connect_db():
    bot.db = await aiosqlite.connect("database.db")


bot.loop.run_until_complete(connect_db())


@tasks.loop(count=1)
async def after_cache_ready():
    bot.error_channel = bot.get_channel(config["bot"]["error_channel_id"])
    bot.dnkl_channel = bot.get_channel(config["bot"]["dnkl_channel_id"])
    bot.ticket_channel = bot.get_channel(config["bot"]["ticket_channel_id"])
    bot.log_channel = bot.get_channel(config["bot"]["log_channel_id"])
    bot.registration_channel = bot.get_channel(config["bot"]["registration_channel_id"])
    bot.guild = bot.get_guild(config["bot"]["guild_id"])

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

    bot.ticket_categories = ("RTickets", "🎫 Ticket Section", "OTHER", "REPORTS", "MILESTONES", "DNKL")
    bot.misc_allies = ("XL", "Lucid", "Cronos", "OUT", "Betrayed", "Blight", "TheNinjaWarriors")

    from func.utils.discord_utils import name_grabber
    bot.admin_ids = [member.id for member in bot.admin.members]
    bot.admin_names = [await name_grabber(member) for member in bot.admin.members]
    bot.staff_names = [await name_grabber(member) for member in bot.staff.members]

    chat_exporter.init_exporter(bot)

    print("Cache filled")


@after_cache_ready.before_loop
async def before_cache_loop():
    print("Waiting for cache...")
    await bot.wait_until_ready()


after_cache_ready.start()
bot.run(bot.token)
