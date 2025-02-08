import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Integer import Integer
from src.func.String import String
from src.utils.consts import gvg_info_embed, requirements_embed, resident_embed
from src.utils.db_utils import get_db_uuid_username_from_discord_id


class Guild(commands.Cog, name="guild"):
    """
    Everything to do with Hypixel guilds. Commands to view guild experience, requirements and more!
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(aliases=["gm", "g", "gexp"])
    @bridge.bridge_option(
        name="name",
        description="The username of the player whose guild experience you'd like to view",
        required=False,
        input_type=str
    )
    async def gmember(self, ctx, name: str = None) -> None:
        """View the given user's guild experience over the past week!"""
        if not name:
            uuid, username = await get_db_uuid_username_from_discord_id(ctx.author.id)
            res = await String(uuid=uuid, username=username).gmember(ctx)
        else:
            res = await String(string=name).gmember(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        if isinstance(res, str):
            await ctx.respond(res, ephemeral=True)

    @bridge.bridge_command(aliases=['weeklylb', 'wlb'])
    async def weekly_gexp_lb(self, ctx) -> None:
        """View the weekly guild experience leaderboard!"""
        await ctx.defer()
        res = await General().weeklylb(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        if isinstance(res, discord.File):
            await ctx.respond(file=res)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=['dailylb', 'dlb'])
    @bridge.bridge_option(
        name="day",
        description="Specify the number of days to go back in time and retrieve the corresponding leaderboard (0-6)",
        required=False,
        input_type=int
    )
    async def gtop(self, ctx, day: int = 1) -> None:
        """View the daily guild experience leaderboard!"""
        await ctx.defer()
        res = await Integer(integer=day).gtop(ctx=ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.File):
            await ctx.respond(file=res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=["req", "reqs"])
    async def requirements(self, ctx) -> None:
        """View guild experience requirements!"""
        await ctx.respond(embed=requirements_embed)

    @bridge.bridge_command(aliases=["res"])
    async def resident(self, ctx) -> None:
        """See the different ways of obtaining the resident rank!"""
        await ctx.respond(embed=resident_embed)

    @bridge.bridge_command()
    async def gvg(self, ctx):
        """View information about GvG team and the requirements!!"""
        await ctx.respond(embed=gvg_info_embed)

    @bridge.bridge_command(aliases=["invite", "inv"])
    @bridge.bridge_option(
        name="name",
        description="The username of the player whose invites you'd like to view",
        required=False,
        input_type=str
    )
    async def invites(self, ctx, name: str = None) -> None:
        """View your invitation stats"""
        await ctx.defer()
        if not name:
            uuid, username = await get_db_uuid_username_from_discord_id(ctx.author.id)
            res = await String(uuid=uuid, username=username).invites()
        else:
            res = await String(string=name).invites()
        await ctx.respond(embed=res)

def setup(bot):
    bot.add_cog(Guild(bot))
