import discord
from discord.ext import commands

from ..classes.Integer import Integer
from ..classes.String import String

class Guild(commands.Cog, name="Guild"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(aliases=["gi"])
    # async def ginfo(self, ctx, *, name: str):
    #     result = await String(string=name).ginfo()
    #     # Send result according to returned value
    #     if isinstance(result, discord.Embed):
    #         await ctx.send(embed=result)
    #     elif isinstance(result, str):
    #         await ctx.send(result)


    # @commands.command(aliases=['ge'])
    # async def gexp(self, ctx, *, name: str):
    #     result = await String(string=name).gexp()
    #     # Send result according to returned value
    #     if isinstance(result, discord.Embed):
    #         await ctx.send(embed=result)
    #     elif isinstance(result, str):
    #         await ctx.send(result)


    # @commands.command()
    # async def gactive(self, ctx):


    # @commands.command()
    # async def ginactive(self, ctx):


    # @commands.command(aliases=['gr'])
    # async def grank(self, ctx, reqrank: str):
    #     msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
    #     await ctx.send(embed=await String(string=reqrank).grank(msg))


    # @commands.command(aliases=['gm', 'g'])
    # async def gmember(self, ctx, name=None):
    #     result = await String(string=name).gmember()
    #     # Send result according to returned value
    #     if isinstance(result, discord.Embed):
    #         await ctx.send(embed=result)
    #     if isinstance(result, str):
    #         await ctx.send(result)


    # @commands.command(aliases=["gt"])
    # async def gtop(self, ctx):


    # @commands.command()
    # async def dailylb(self, ctx, day=1):
    #     msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
    #     await ctx.send(await Integer(integer=day).dailylb(msg))


    # @commands.command(aliases=['req', 'requirement'])
    # async def requirements(self, ctx):

    # @commands.command(aliases=['res'])
    # async def resident(self, ctx):


    # @commands.command(aliases=['ticket'])
    # async def tickets(self, ctx):


def setup(bot):
    bot.add_cog(Guild(bot))