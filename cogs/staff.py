import discord
from discord.ext import commands

class staff(commands.Cog, name="Staff"):
    def __init__(self, client):
        self.client = client


def setup(bot):
    bot.add_cog(staff(bot))