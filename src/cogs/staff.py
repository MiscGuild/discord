import discord
from __main__ import bot
from discord.ext import commands
from src.func.General import General
from src.func.Union import Union
from src.utils.consts import partner_channel_id


class Staff(commands.Cog, name="staff"):
    """
    Commands for Miscellaneous staff members.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Staff")
    async def inactive(self, ctx):
        """View all inactive users in the guild!"""
        for embed in await General.inactive(ctx):
            await ctx.send(embed=embed)

    @commands.command(aliases=["fs"])
    @commands.has_role("Staff")
    async def forcesync(self, ctx, member: discord.Member, name: str):
        """Update a user's discord nick, tag and roles for them!"""
        res = await Union(user=member).sync(ctx, name, None, True)
        if isinstance(res, discord.Embed):
            await ctx.send(embed=res)
        elif isinstance(res, str):
            await ctx.send(res)

    @commands.command()
    @commands.has_role("Admin")
    async def staffreview(self, ctx):
        """Send a progress update and review for staff members!"""
        res = await General.staffreview(ctx)
        # Result may be empty
        if res:
            await bot.staff_announcements.send(embed=res)

    @commands.command()
    @commands.has_role("Admin")
    async def partner(self, ctx, organization_name: str):
        """Create an embed with information about a partner!"""
        await bot.get_channel(partner_channel_id).send(embed=await General.partner(ctx, organization_name))

    @commands.command()
    @commands.has_role("Staff")
    async def rolecheck(self, ctx, send_ping: bool = True):
        """Sync the names and roles of everyone in the discord!"""
        await General.rolecheck(ctx, send_ping)


def setup(bot):
    bot.add_cog(Staff(bot))
