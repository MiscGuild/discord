import discord
from discord.ext import commands

class Tickets(commands.Cog, name="Tickets"):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Tickets(bot))