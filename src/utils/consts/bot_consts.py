import discord
import toml

# Define config
CONFIG = toml.load("config.toml")

PREFIX = CONFIG["prefix"]
STATUS = CONFIG["status"]
TOKEN = CONFIG["token"]
API_KEYS = CONFIG["api_keys"]

ERROR_REPLY_EXCEPTIONS = (discord.Forbidden, discord.HTTPException, discord.NotFound)

GUILD_HANDLE = CONFIG["guild_handle"]
ALLIES = CONFIG["allies"]

# Colors
NEG_COLOR = 0xff3333
POS_COLOR = 0x00A86B
NEUTRAL_COLOR = 0x8369ff
ERROR_COLOR = 0xDE3163
