from __main__ import bot

import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.consts import INFORMATION_MESSAGE, INFORMATION_REQUIREMENTS_EMBED, RULES_MESSAGES, \
    ELITE_MEMBER_CATEGORIES
from src.utils.ui_utils import tickets


class Staff(commands.Cog, name="staff"):
    """
    Commands for Miscellaneous staff members.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    async def inactive(self, ctx: discord.ApplicationContext) -> None:
        """View all inactive users in the guild!"""
        await ctx.defer()
        for embed in await General().inactive():
            await ctx.respond(embed=embed)

    @bridge.bridge_command(aliases=["fs"])
    @commands.has_permissions(kick_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member who you would like to forcesync",
        required=True,
        input_type=discord.Member
    )
    async def forcesync(self, ctx: discord.ApplicationContext, member: discord.Member, name: str = None) -> None:
        """Update a user's discord nick, tag and roles for them!"""
        res = await Union(user=ctx.guild.get_member(member.id)).sync(ctx, name, None, True)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    @bridge.bridge_option(
        name="send_ping",
        description="Enter 'False' if you don't want to ping New Members upon completion of rolecheck",
        required=False,
        input_type=bool
    )
    async def rolecheck(self, ctx: discord.ApplicationContext, send_ping: bool = True) -> None:
        """Sync the names and roles of everyone in the discord!"""
        await General().rolecheck(ctx, send_ping)

    @bridge.bridge_command()
    @commands.has_permissions(administrator=True)
    async def information(self, ctx: discord.ApplicationContext) -> None:
        await ctx.send(content=INFORMATION_MESSAGE, embed=INFORMATION_REQUIREMENTS_EMBED)

    @bridge.bridge_command()
    @commands.has_permissions(administrator=True)
    async def rules(self, ctx: discord.ApplicationContext) -> None:
        for message in RULES_MESSAGES:
            await ctx.send(content=message)

    @bridge.bridge_command(name="update_elite_member", description="Update a user's Elite Member role!")
    @commands.has_permissions(administrator=True)
    @bridge.bridge_option(
        name="username",
        description="The username of the player you would like to give the Elite Member role",
        required=True,
        input_type=str
    )
    @bridge.bridge_option(
        name="reason",
        description="Why do they deserve the Elite Member role?",
        required=True,
        choices=[discord.OptionChoice(name=x, value=x) for x in ELITE_MEMBER_CATEGORIES],
    )
    @bridge.bridge_option(
        name="monetary_value",
        description="How much money have they spent on the server (in dollars)?",
        required=False,
        input_type=int,
        min_value=10
    )
    async def update_elite_member(self, ctx: discord.ApplicationContext, username: str, reason: str,
                                  monetary_value: int = None) -> None:
        await ctx.respond(
            embed=await String(string=reason, username=username).elite_member(monetary_value=monetary_value))

    @bridge.bridge_command()
    @commands.has_permissions(administrator=True)
    async def tickets(self, ctx: discord.ApplicationContext) -> None:
        """Send a ticket help embed!"""
        image, messages, view = await tickets()
        await ctx.send(content=messages[0])
        await ctx.send(content=messages[1], view=view)


def setup(bot):
    bot.add_cog(Staff(bot))
