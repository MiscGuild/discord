import discord
from discord.ext import commands, bridge

from src.func.String import String
from src.func.Union import Union


class General(commands.Cog, name="general"):
    """
    Contains all source, avatar, qotd.
    """

    def __init__(self, bot):
        self.bot = bot

    # Command from https://github.com/Rapptz/RoboDanny
    @bridge.bridge_command(aliases=['src'])
    async def source(self, ctx, *, command: str = None):
        """View the source code for a command!"""
        await ctx.respond(await String(string=command).source())

    @bridge.bridge_command()
    async def avatar(self, ctx, user: discord.Member = None):
        """See the avatar of a given user!"""
        await ctx.respond(embed=await Union(user=user or ctx.author).avatar())

    @bridge.bridge_command()
    @commands.has_any_role("QOTD Manager", "Staff")
    async def qotd(self, ctx):
        """Used by QOTD Managers to register a QOTD"""
        await ctx.respond("**What is the question of the day?**")
        question = await self.bot.wait_for("message",
                                           check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
        await String(string=question.content).qotd(ctx)


def setup(bot):
    bot.add_cog(General(bot))
