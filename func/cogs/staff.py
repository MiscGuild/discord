import discord
from discord.ext import commands

from func.classes.Boolean import Boolean
from func.classes.Union import Union


class Staff(commands.Cog, name="Staff"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.has_role("Staff")
    # async def inactive(self, ctx):

    @commands.command(aliases=["fs"])
    @commands.has_role("Staff")
    async def forcesync(self, ctx, member: discord.Member, name: str):
        """Update a user's discord nick, tag and roles for them!"""
        result = await Union(user=member).sync(ctx, name, None, True)
        if isinstance(result, discord.Embed):
            await ctx.send(embed=result)
        elif isinstance(result, str):
            await ctx.send(result)

    # @commands.command()
    # @commands.has_role("Admin")
    # async def staffreview(self, ctx):

    # @commands.command()
    # @commands.has_role("Admin")
    # async def partner(self, ctx):

    @commands.command()
    @commands.has_role("Staff")
    async def rolecheck(self, ctx, send_ping: bool=True):
        """Sync the names and roles of everyone in the discord!"""
        await Boolean(boolean=send_ping).rolecheck(ctx)


def setup(bot):
    bot.add_cog(Staff(bot))
