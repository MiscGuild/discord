import discord
from discord.commands import option
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.discord_utils import name_grabber


class Hypixel(commands.Cog, name="hypixel"):
    """
    All discord related Hypixel commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @option(
        name="name",
        description="Your Minecraft Username",
        required=True,
        input_type=str
    )
    @option(
        name="tag",
        description="The Tag you'd like to put beside your username",
        required=False,
        input_type=str
    )
    async def sync(self, ctx, name, tag: str = None):
        """Update your discord nick, tag and roles!"""
        res = await Union(user=ctx.author).sync(ctx, name, tag)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command(aliases=['i'])
    @option(
        name="name",
        description="The Minecraft username of the player whose stats you'd like to view",
        required=False,
        input_type=str
    )
    async def info(self, ctx, name: str = None):
        """View Hypixel stats of the given user!"""
        if not name:
            name = await name_grabber(ctx.author)
        await ctx.respond(embed=await String(string=name).info())

    @bridge.bridge_command(aliases=['dnkladd', 'dnkla'])
    @commands.has_any_role("Staff")
    @option(
        name="name",
        description="The Minecraft username of the player who you want to add to the do-not-kick-list",
        required=True,
        input_type=str
    )
    async def dnkl_add(self, ctx, name: str):
        """Add a user to the do-not-kick-list!"""
        res = await String(string=name).dnkladd(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=['dnklrmv', 'dnklremove', 'dnklremv', 'dnklr'])
    @commands.has_permissions(manage_messages=True)
    @option(
        name="name",
        description="The Minecraft username of the player who you want to remove from the do-not-kick-list",
        required=True,
        input_type=str
    )
    async def dnkl_remove(self, ctx, name: str):
        """Remove a player from the do-not-kick-list"""
        await ctx.respond(await String(string=name).dnklremove())

    @bridge.bridge_command(aliases=['dnkllist', 'dnkll'])
    async def dnkl_list(self, ctx):
        """View all users on the do-not-kick-list!"""
        await ctx.respond(embed=await General.dnkllist(ctx))

    @bridge.bridge_command(aliases=['dnklchk', 'dnklcheck', 'dnklc'])
    @option(
        name="name",
        description="The Minecraft username of the player whose do-not-kick-list eligibility you'd like to check",
        required=False,
        input_type=str
    )
    async def dnkl_check(self, ctx, name: str = None):
        """Check whether you are eligible for the do-not-kick-list!"""
        if not name:
            name = await name_grabber(ctx.author)

        res = await String(string=name).dnklcheck()
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command(aliases=["p", "score", "point"])
    @option(
        name="name",
        description="The Minecraft username of the player whose score you'd like to view",
        required=False,
        input_type=str
    )
    async def points(self, ctx, name: str = None):
        """View Hypixel stats of the given user!"""
        if not name:
            name = await name_grabber(ctx.author)
        await ctx.respond(embed=await String(string=name).score())

    @bridge.bridge_command(aliases=['tlb', 'tl'])
    async def tourney_leaderboard(self, ctx):
        """View the current tournament leaderboard!"""
        await ctx.defer()
        await ctx.respond(file=await General().tourney_leaderboard())


def setup(bot):
    bot.add_cog(Hypixel(bot))
