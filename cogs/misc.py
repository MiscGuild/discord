import discord
from discord.ext import commands

class Misc(commands.Cog, name="Misc"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Misc(bot))