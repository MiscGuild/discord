import discord
from discord.ext import commands

from func.classes.Func import Func
from func.classes.Integer import Integer
from func.classes.String import String
from func.utils.discord_utils import name_grabber
from func.utils.consts import get_requirements_embed, get_resident_embed


class Guild(commands.Cog, name="Guild"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def gactive(self, ctx):

    @commands.command(aliases=["gm", "g"])
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

    @commands.command()
    async def weeklylb(self, ctx):
        """View the weekly gexp leaderboard!"""
        res = await Func.weeklylb(ctx)
        if isinstance(res, discord.File):
            await ctx.send(file=res)
        if isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    @commands.command()
    async def gtop(self, ctx, day=1):
        """View the daily guild experience leaderboard!"""
        res = await Integer(integer=day).gtop(ctx=ctx)
        if isinstance(res, discord.File):
            await ctx.send(file=res)
        elif isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    @commands.command(aliases=["req", "reqs"])
    async def requirements(self, ctx):
        """View the guild gexp requirements!"""
        # Just send the reqs embed straight away
        await ctx.send(embed=await get_requirements_embed())

    @commands.command(aliases=["res"])
    async def resident(self, ctx):
        """See the different ways of obtaining the resident rank!"""
        await ctx.send(embed=await get_resident_embed())


def setup(bot):
    bot.add_cog(Guild(bot))
