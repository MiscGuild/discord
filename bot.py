from src.utils.discord_utils import after_cache_ready
import sys

import discord
from discord.ext import bridge

from src.utils.consts import config

if __name__ != "__main__":
    sys.exit("Bot.py is not the __main__ file. Please run it from the bot.py file.")

# Create bot
intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.message_content = True
bot = bridge.Bot(command_prefix=config["prefix"], intents=intents,
                 status=discord.Status.idle, activity=discord.Game(config["status"]), case_insensitive=True)

# Load all bot vars once cache is ready

bot.remove_command("help")
after_cache_ready.start()
# Load extensions
for extension in ["src.cogs.general", "src.cogs.giveaways", "src.cogs.guild", "src.cogs.hypixel",
                  "src.cogs.listeners", "src.cogs.menus", "src.cogs.moderation", "src.cogs.staff",
                  "src.cogs.tickets", "src.cogs.help"]:
    try:
        bot.load_extension(extension)
        print(f"Loaded {extension}")
    except Exception as e:
        print(
            f"WARNING: Failed to load extension {extension}\n{e}", file=sys.stderr)

# Run bot
bot.run(config["token"])
