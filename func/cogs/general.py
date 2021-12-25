import discord
from discord.ext import commands

from func.classes.String import String
from func.classes.Union import Union

class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot


    # Command from https://github.com/Rapptz/RoboDanny
    @commands.command()
    async def source(self, ctx, *, command: str=None):
        """View the source code for a command!"""
        await ctx.send(await String(string=command).source())


    @commands.command()
    async def avatar(self, ctx, user: discord.User):
        """See the avatar of a given user!"""
        await ctx.send(embed=await Union(user=user).avatar()) 


def setup(bot):
    bot.add_cog(General(bot))
