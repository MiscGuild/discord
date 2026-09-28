import discord
from discord.commands import option
from discord.ext import commands, bridge

from src.func.String import String
from src.func.Union import Union


class General(commands.Cog, name="general"):
    """
    Source code, avatars, player profiles and ping preferences.
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
        """Links to the bot's source code on GitHub.

        With no argument you get the repository link. Pass a command
        name to jump straight to its implementation, e.g. `ban` or
        `g member`. The link covers the command's wrapper, not the
        helper it calls.
        """
        await ctx.respond(await String(string=command).source())

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="user",
        description="User whose avatar you'd like to view",
        required=False,
        input_type=discord.Member
    )
    async def avatar(self, ctx: discord.ApplicationContext, user: discord.Member = None) -> None:
        """Shows a member's Discord avatar.

        Defaults to your own avatar if no member is given. Members
        without a custom avatar show Discord's default one.
        """
        await ctx.respond(embed=await Union(user=user or ctx.author).avatar())

    @commands.slash_command()
    @option(
        name="setting",
        description="Do you want the bot to ping you in daily and weekly gexp leaderboards?",
        choices=[discord.OptionChoice("Yes", value=1), discord.OptionChoice("No", value=0)],
        required=True
    )
    async def do_pings(self, ctx: discord.ApplicationContext, setting: int) -> None:
        """Choose whether you get pinged in automatic leaderboard posts.

        Only affects the scheduled daily and weekly gexp leaderboards.
        Running `/g top` or `/g weekly` yourself never pings anyone,
        whatever this is set to.
        """
        await ctx.respond(embed=await Union(ctx.author).do_pings(setting=setting))

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="Member",
        description="The discord user whose minecraft ign you'd like to find",
        required=True,
        input_type=discord.Member
    )
    async def whois(self, ctx: discord.ApplicationContext, member: discord.Member = None) -> None:
        """Links a Discord account to its Minecraft username and UUID.

        Reads the bot's own database, so the member has to have synced
        or registered first. Unregistered members come back blank.
        """
        await ctx.respond(embed=await Union(member or ctx.author).whois())

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="user",
        description="Discord member whose profile you'd like to view",
        required=False,
        input_type=discord.Member
    )
    async def me(self, ctx: discord.ApplicationContext, user: discord.Member = None) -> None:
        """Shows a member's Miscellaneous profile.

        Covers their rank, Elite Member status, guild experience history
        and invitation stats. Anyone you pass here is shown publicly,
        invite stats included. Defaults to your own profile.
        """
        await ctx.respond(embed=await Union(user or ctx.author).me())


def setup(bot):
    bot.add_cog(General(bot))
