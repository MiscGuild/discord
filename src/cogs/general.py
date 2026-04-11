import discord
from discord.commands import option
from discord.ext import commands, bridge

from src.func.String import String
from src.func.Union import Union


class General(commands.Cog, name="general"):
    """
    Contains source, avatar.
    """

    def __init__(self, bot):
        self.bot = bot

    # Command from https://github.com/Rapptz/RoboDanny
    @bridge.bridge_command(name="source", aliases=['src'])
    @bridge.bridge_option(
        name="command",
        description="The command you would like to see the source code for",
        required=False,
        input_type=str
    )
    async def source(self, ctx: discord.ApplicationContext, *, command: str = None) -> None:
        """View the source code for the bot or a specific command"""
        await ctx.respond(await String(string=command).source())

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="user",
        description="User whose avatar you'd like to view",
        required=False,
        input_type=discord.Member
    )
    async def avatar(self, ctx: discord.ApplicationContext, user: discord.Member = None) -> None:
        """See the avatar of a given user!"""
        await ctx.respond(embed=await Union(user=user or ctx.author).avatar())

    @commands.slash_command()
    @option(
        name="setting",
        description="Do you want the bot to ping you in daily and weekly gexp leaderboards?",
        choices=[discord.OptionChoice("Yes", value=1), discord.OptionChoice("No", value=0)],
        required=True
    )
    async def do_pings(self, ctx: discord.ApplicationContext, setting: int) -> None:
        """Used to enable/disable pings in automatic daily and weekly leaderboard messages!"""
        await ctx.respond(embed=await Union(ctx.author).do_pings(setting=setting))

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="Member",
        description="The discord user whose minecraft ign you'd like to find",
        required=True,
        input_type=discord.Member
    )
    async def whois(self, ctx: discord.ApplicationContext, member: discord.Member = None) -> None:
        """Used to find a player's minecraft username and uuid using their discord account."""
        await ctx.respond(embed=await Union(member or ctx.author).whois())

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="user",
        description="Discord member whose profile you'd like to view",
        required=False,
        input_type=discord.Member
    )
    async def me(self, ctx: discord.ApplicationContext, user: discord.Member = None) -> None:
        """View a user's profile"""
        await ctx.respond(embed=await Union(user or ctx.author).me())


def setup(bot):
    bot.add_cog(General(bot))
