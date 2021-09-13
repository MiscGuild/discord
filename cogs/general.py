import chat_exporter
import discord
from discord.ext import commands


class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot




def setup(bot):
    bot.add_cog(General(bot))
