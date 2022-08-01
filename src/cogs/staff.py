from __main__ import bot

import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Union import Union
from src.utils.consts import partner_channel_id, information_embed, neutral_color


class Staff(commands.Cog, name="staff"):
    """
    Commands for Miscellaneous staff members.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @commands.has_role("Staff")
    async def inactive(self, ctx):
        """View all inactive users in the guild!"""
        await ctx.defer()
        for embed in await General.inactive(ctx):
            await ctx.respond(embed=embed)

    @bridge.bridge_command(aliases=["fs"])
    @commands.has_role("Staff")
    async def forcesync(self, ctx, member: discord.Member, name: str):
        """Update a user's discord nick, tag and roles for them!"""
        res = await Union(user=member).sync(ctx, name, None, True)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)


    @bridge.bridge_command()
    @commands.has_role("Admin")
    async def partner(self, ctx, organization_name: str):
        """Create an embed with information about a partner!"""
        await bot.get_channel(partner_channel_id).send(embed=await General.partner(ctx, organization_name))
        await ctx.respond(embed=discord.Embed(title=f"Miscellaneous has officially partnered with {organization_name}", color=neutral_color).set_footer(text="The partner embed has been sent to the partners channel!"))


    @bridge.bridge_command()
    @commands.has_role("Admin")
    async def information(self, ctx):
        await ctx.respond(embed=information_embed)

    @commands.command()
    @commands.has_role("Staff")
    async def rolecheck(self, ctx, send_ping: bool = True):
        """Sync the names and roles of everyone in the discord!"""
        await General.rolecheck(ctx, send_ping)

    @commands.command(aliases=['ug', 'updateevent', 'ue'])
    @commands.has_role("Staff")
    async def updategexp(self, ctx):
        '''Command to update the gexps of people on the spreadsheet during the guild event'''
        await General.updategexp(ctx)


def setup(bot):
    bot.add_cog(Staff(bot))
