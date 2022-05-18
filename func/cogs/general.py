import discord
from discord.ext import commands
from func.classes.String import String
from func.classes.Union import Union


class General(commands.Cog, name="general"):
    """
    Contains all source, avatar, qotd.
    """
    def __init__(self, bot):
        self.bot = bot

    # Command from https://github.com/Rapptz/RoboDanny
    @commands.command()
    async def source(self, ctx, *, command: str = None):
        """View the source code for a command!"""
        await ctx.send(await String(string=command).source())

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """See the avatar of a given user!"""
        await ctx.send(embed=await Union(user=user or ctx.author).avatar())

    @commands.command()
    @commands.has_any_role("QOTD Manager", "Staff")
    async def qotd(self, ctx):
        """Used by QOTD Managers to register a QOTD"""
        await ctx.send("**What is the question of the day?**")
        question = await self.bot.wait_for("message",
                                           check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
        await String(string=question.content).qotd(ctx)


def setup(bot):
    bot.add_cog(General(bot))
