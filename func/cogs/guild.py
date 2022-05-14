import discord
from discord.ext import commands
from func.classes.Func import Func
from func.classes.Integer import Integer
from func.classes.String import String
from func.utils.consts import requirements_embed, resident_embed, gvg_info_embed
from func.utils.discord_utils import name_grabber


class Guild(commands.Cog, name="guild"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["gm", "g", "gmember", "gexp"])
    async def member_gexp(self, ctx, name: str = None):
        """View the given user's gexp over the past week!"""
        if not name:
            name = await name_grabber(ctx.author)

        res = await String(string=name).gmember(ctx)
        if isinstance(res, discord.Embed):
            await ctx.send(embed=res)
        if isinstance(res, str):
            await ctx.send(res)

    @commands.command(aliases=['weeklylb'])
    async def weekly_gexp_lb(self, ctx):
        """View the weekly gexp leaderboard!"""
        res = await Func.weeklylb(ctx)
        if isinstance(res, discord.File):
            await ctx.send(file=res)
        if isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    @commands.command()
    async def gtop(self, ctx, day: int = 1):
        """View the daily guild experience leaderboard!"""
        res = await Integer(integer=day).gtop(ctx=ctx)
        if isinstance(res, discord.File):
            await ctx.send(file=res)
        elif isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    @commands.command(aliases=["req", "reqs"])
    async def requirements(self, ctx):
        """View the guild gexp requirements!"""
        await ctx.send(embed=requirements_embed)

    @commands.command(aliases=["res"])
    async def resident(self, ctx):
        """See the different ways of obtaining the resident rank!"""
        await ctx.send(embed=resident_embed)

    @commands.command()
    async def gvg(self, ctx):
        """View information about GvG's and GvG requirements!"""
        await ctx.send(embed=gvg_info_embed)


def setup(bot):
    bot.add_cog(Guild(bot))
