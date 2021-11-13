import logging
import sys
import traceback

import aiosqlite
import chat_exporter
import discord
import toml
from discord.ext import commands, tasks

from cogs.utils import utilities as hypixel

logging.basicConfig(level=logging.INFO)

config = toml.load('config.toml')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['bot']['prefix']), intents=intents,
                   status=discord.Status.idle, activity=discord.Game(config['bot']['status']), case_insensitive=True)

bot.config = config
bot.token = config['bot']['token']
bot.api_tokens = config['hypixel']['api_keys']
bot.owner_id = config['bot']['ownerID']
bot.resident_req = int(50000)
bot.active = int(285000)
bot.inactive = int(115000)
bot.dnkl = (bot.inactive * 2)
bot.new_member = int(20000)


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


bot.help_command = HelpCommand(command_attrs={'hidden': True})

initial_extensions = ['cogs.fun', 'cogs.hypixel', 'cogs.mod', 'cogs.staff', 'cogs.tickets', 'cogs.owner',
                      'cogs.buttons', 'cogs.giveaways', 'cogs.general', 'cogs.events']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'{extension} Loaded!')
        except Exception as e:
            print(f'Failed to load extention {extension}', file=sys.stderr)


@bot.event
async def on_ready():
    print('The Miscellaneous Bot is ONLINE!\n\n')


@bot.event
async def on_command_error(ctx, error):
    # Prevents commands with local handlers or cogs with overwrritten on_command_errors being handled here
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title=f'Invalid Command!',
                              descrption='Use `,help` to view a list of all commands!', color=0xDE3163)
        await ctx.send(embed=embed)
        return
    elif ctx.command.has_error_handler() or ctx.cog.has_error_handler():
        return

    # Checks for the original exception raised and send to CommandInvokeError
    error = getattr(error, 'original', error)

    if isinstance(error, commands.NotOwner):
        embed = discord.Embed(title=f'Your soul lacks the strength to utilize this command!',
                              description="You are not the owner of this bot!", color=0xDE3163)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(title=f'Your soul lacks the strength to utilize this command!',
                              description="You do not have the required roles to access this restricted command!",
                              color=0xDE3163)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title=f'Your soul lacks the strength to utilize this command!',
                              description="You do not have the required permissions to access this restricted command!",
                              color=0xDE3163)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(title=f"Member not found",
                                description="This member doesn't seem to exist.\nCheck you have their ID or tag's capitalization and spelling correct!",
                                color=0xDE3163)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        usage = f"{ctx.prefix}{ctx.command.name}"
        for key, value in ctx.command.clean_params.items():
            if value.default == None:
                usage += " [" + key + "]"
            else:
                usage += " <" + key + ">"
        embed = discord.Embed(title=f" arguments",
                              description=f"Command usage:\n`{usage}`\nFor more help, see `{ctx.prefix}help {ctx.command}`",
                              color=0xDE3163)
        await ctx.send(embed=embed)

    else:
        # All other errors get sent to the error channel
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        if len(tb) <= 2000:
            await bot.error_channel.send(f"Ignoring exception in command {ctx.command}:\n```py\n{tb}\n```")
            embed = discord.Embed(title=f"Error",description=str(error).split(":")[2],color=0xDE3163)
            await ctx.send(embed=embed)
        else:
            await bot.error_channel.send(f"```An error occurred in command '{ctx.command}' that could not be sent in this channel, check the console for the traceback. \n\n'{error}'```")
            print("The below exception could not be sent to the error channel.")
            print(tb)


@bot.event
async def on_error(event, *args, **kwargs):
    # Grabs the error being handled, formats it and sends it to the error channel
    tb = traceback.format_exc()
    await bot.error_channel.send(f"Ignoring exception in event {event}:\n```py\n{tb}\n```")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(714882620001091585)
    role = discord.utils.get(member.guild.roles, name="New Member")
    await member.add_roles(role)

    embed = discord.Embed(title=f"Welcome to the Miscellaneous Discord, {member.name}", color=0x8368ff)
    embed.add_field(name="Register using the following command:", value="**,register** `Your Minecraft Name`",
                    inline=False)
    embed.set_footer(text="Example:\n,register John")

    await channel.send(embed=embed)


async def connect_db():
    bot.db = await aiosqlite.connect('database.db')
    print("db connected")
    await bot.db.execute('''CREATE TABLE IF NOT EXISTS event(
        uuid TEXT PRIMARY KEY NOT NULL,
        points NUMERIC NOT NULL,
        completed INTEGER NOT NULL,
        scaled_challenge_score NUMERIC NOT NULL)''')
    await bot.db.execute('''CREATE TABLE IF NOT EXISTS event_challenge(
        date TEXT PRIMARY KEY NOT NULL,
        scaled_challenge TEXT NOT NULL,
        hard_challenge TEXT NOT NULL,
        easy_challenge TEXT NOT NULL,
        member_challenge TEXT NOT NULL)''')
    await bot.db.commit()


bot.loop.run_until_complete(connect_db())


@tasks.loop(count=1)
async def after_cache_ready():
    bot.error_channel = bot.get_channel(config['bot']['error_channel_id'])
    bot.dnkl_channel = bot.get_channel(config['bot']['dnkl_channel_id'])
    bot.ticket_channel = bot.get_channel(config['bot']['ticket_channel_id'])
    bot.log_channel = bot.get_channel(config['bot']['log_channel_id'])
    bot.events_channel = bot.get_channel(config['bot']['event_channel_id'])
    bot.guild = bot.get_guild(config['bot']['guild_id'])

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
    bot.christmas_event = discord.utils.get(bot.guild.roles, name="Christmas Event")
    bot.tag_allowed_roles = (bot.active_role, bot.staff, bot.former_staff, bot.server_booster, bot.rich_kid)

    bot.ticket_categories = ('RTickets', '🎫 Ticket Section', 'OTHER', 'REPORTS', 'MILESTONES', 'DNKL')
    bot.misc_allies = ("XL", "Lucid", "Cronos", "OUT", "Betrayed", "Blight","TheNinjaWarriors")
    bot.admin_ids = [member.id for member in bot.admin.members]
    bot.admin_names = [await hypixel.name_grabber(member) for member in bot.admin.members]
    bot.staff_names = [await hypixel.name_grabber(member) for member in bot.staff.members]

    chat_exporter.init_exporter(bot)

    print("Cache filled and task complete.")


@after_cache_ready.before_loop
async def before_cache_loop():
    print("Waiting for cache...")
    await bot.wait_until_ready()


after_cache_ready.start()
bot.run(bot.token)
