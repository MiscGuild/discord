from __main__ import bot

import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Union import Union
from src.utils.consts import partner_channel_id, information_embed, neutral_color, rules_embed


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
        for embed in await General().inactive(ctx):
            await ctx.respond(embed=embed)

    @bridge.bridge_command(aliases=["fs"])
    @commands.has_any_role("Staff", "Discord Moderator")
    @bridge.bridge_option(
        name="member",
        description="The Discord member who you would like to forcesync",
        required=True,
        input_type=discord.Member
    )
    @bridge.bridge_option(
        name="name",
        description="Their Minecraft username",
        required=False,
        input_type=str
    )
    async def forcesync(self, ctx, member: discord.Member, name: str = None) -> None:
        """Update a user's discord nick, tag and roles for them!"""
        res = await Union(user=ctx.guild.get_member(member.id)).sync(ctx, name, None, True)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_role("Admin")
    @bridge.bridge_option(
        name="organization_name",
        description="The name of the organization you are partnering with",
        required=True,
        input_type=str
    )
    async def partner(self, ctx, *, organization_name: str):
        """Create an embed with information about a partner!"""
        await bot.get_channel(partner_channel_id).send(embed=await General().partner(ctx, organization_name))
        await ctx.respond(embed=discord.Embed(title=f"Miscellaneous has officially partnered with {organization_name}",
                                              color=neutral_color).set_footer(
            text="The partner embed has been sent to the partners channel!"))

    @bridge.bridge_command()
    @commands.has_role("Admin")
    async def information(self, ctx):
        await ctx.respond(embed=information_embed)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    @bridge.bridge_option(
        name="send_ping",
        description="Enter 'False' if you don't want to ping New Members upon completion of rolecheck",
        required=False,
        input_type=bool
    )
    async def rolecheck(self, ctx, send_ping: bool = True):
        """Sync the names and roles of everyone in the discord!"""
        await General().rolecheck(ctx, send_ping)

    @bridge.bridge_command()
    @commands.has_role("Guild Master")
    async def rules(self, ctx):
        await ctx.send(embed=rules_embed)



def setup(bot):
    bot.add_cog(Staff(bot))
