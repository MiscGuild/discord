import discord
from discord.ext import commands

from func.classes.String import String

class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot


    # Command from https://github.com/Rapptz/RoboDanny
    @commands.command()
    async def source(self, ctx, *, command: str=None):
        await ctx.send(await String(string=command).source())


    # @commands.command()
    # async def ping(self, ctx):


    # @commands.command()
    # async def avatar(self, ctx, user: discord.User):
    #     await ctx.send(embed=await User(user=user).avatar()) 



def setup(bot):
    bot.add_cog(General(bot))
