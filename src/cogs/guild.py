import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Integer import Integer
from src.func.String import String
from src.utils.consts import gvg_info_embed, requirements_embed, resident_embed
from src.utils.discord_utils import name_grabber


class Guild(commands.Cog, name="guild"):
    """
    Everything to do with guilds. All the commands related to guilds come under this module.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(aliases=["gm", "g", "gexp"])
    async def gmember(self, ctx, name: str = None):
        """View the given user's gexp over the past week!"""
        if not name:
            name = await name_grabber(ctx.author)

        res = await String(string=name).gmember(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        if isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command(aliases=['weeklylb', 'wlb'])
    async def weekly_gexp_lb(self, ctx):
        """View the weekly gexp leaderboard!"""
        await ctx.defer()
        res = await General.weeklylb(ctx)
        if isinstance(res, discord.File):
            await ctx.respond(file=res)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=['dailylb', 'dlb'])
    async def gtop(self, ctx, day: int = 1):
        """View the daily guild experience leaderboard!"""
        await ctx.defer()
        res = await Integer(integer=day).gtop(ctx=ctx)
        if isinstance(res, discord.File):
            await ctx.respond(file=res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=["req", "reqs"])
    async def requirements(self, ctx):
        """View the guild gexp requirements!"""
        await ctx.respond(embed=requirements_embed)

    @bridge.bridge_command(aliases=["res"])
    async def resident(self, ctx):
        """See the different ways of obtaining the resident rank!"""
        await ctx.respond(embed=resident_embed)

    @bridge.bridge_command()
    async def gvg(self, ctx):
        """View information about Miscellaneous' GvG team and the requirements!!"""
        await ctx.respond(embed=gvg_info_embed)


def setup(bot):
    bot.add_cog(Guild(bot))
