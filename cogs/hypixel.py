import discord
from discord.ext import commands
from utils import hypixel

class Hypixel(commands.Cog, name="Hypixel"):
    def __init__(self, client):
        self.client = client

def setup(bot):
    bot.add_cog(Hypixel(bot))