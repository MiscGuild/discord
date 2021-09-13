import chat_exporter
import discord
from discord.ext import commands


class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def source(self, ctx):
        """ Check the source code!"""
        await ctx.send(
            f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/MiscGuild/MiscBot")

    
def setup(bot):
    bot.add_cog(General(bot))
