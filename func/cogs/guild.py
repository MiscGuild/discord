import discord
from discord.ext import commands

from func.classes.Integer import Integer
from func.classes.String import String
from func.utils.discord_utils import name_grabber


class Guild(commands.Cog, name="Guild"):
    def __init__(self, bot):
        self.bot = bot


    # @commands.command()
    # async def gactive(self, ctx):

    # @commands.command()
    # async def ginactive(self, ctx):

    # @commands.command(aliases=['gr'])
    # async def grank(self, ctx, reqrank: str):
    #     msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
    #     await ctx.send(embed=await String(string=reqrank).grank(msg))

    @commands.command(aliases=['gm', 'g'])
    async def gmember(self, ctx, name=None):
        """View the given user's gexp over the past week!"""
        if not name:
            name = await name_grabber(ctx.author)

        result = await String(string=name).gmember(ctx)
        # Send result according to returned value
        if isinstance(result, discord.Embed):
            await ctx.send(embed=result)
        if isinstance(result, str):
            await ctx.send(result)

    # @commands.command(aliases=["gt"])
    # async def gtop(self, ctx):

    @commands.command()
    async def gtop(self, ctx, day=1):
        """View the daily guild experience leaderboard!"""
        res = await Integer(integer=day).gtop(ctx=ctx)
        if isinstance(res, discord.File):
            await ctx.send(file=res)
        elif isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    # @commands.command(aliases=['req', 'requirement'])
    # async def requirements(self, ctx):

    # @commands.command(aliases=['res'])
    # async def resident(self, ctx):

    # @commands.command(aliases=['ticket'])
    # async def tickets(self, ctx):


def setup(bot):
    bot.add_cog(Guild(bot))
