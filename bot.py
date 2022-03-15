import sys

import discord
from discord.ext import commands

from func.utils.consts import config

if __name__ != "__main__":
    sys.exit("Bot.py is not the __main__ file. Please run it from the bot.py file.")

# Create bot
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config["prefix"]), intents=intents,
                status=discord.Status.idle, activity=discord.Game(config["status"]), case_insensitive=True)

# Load all bot vars once cache is ready
from func.utils.discord_utils import after_cache_ready

after_cache_ready.start()

# Load extensions
for extension in ["func.cogs.general", "func.cogs.giveaways", "func.cogs.guild", "func.cogs.hypixel",
                  "func.cogs.listeners", "func.cogs.menus", "func.cogs.moderation", "func.cogs.staff",
                  "func.cogs.tickets"]:
    try:
        bot.load_extension(extension)
        print(f"Loaded {extension}")
    except Exception as e:
        print(f"WARNING: Failed to load extension {extension}", file=sys.stderr)
        print(e)

# Run bot
bot.run(config["token"])
