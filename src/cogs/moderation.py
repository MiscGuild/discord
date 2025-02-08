import discord
import discord.ext.commands.context as Context
from discord.ext import commands, bridge

from src.func.Integer import Integer
from src.func.Union import Union


class Moderation(commands.Cog, name="moderation"):
    """
    Everything to do with discord Moderation.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member you would like to mute",
        required=True,
        input_type=discord.Member
    )
    @bridge.bridge_option(
        name="reason",
        description="The reason behind the mute",
        required=False,
        input_type=str
    )
    async def mute(self, ctx: Context, member: discord.Member, *, reason: str = None) -> None:
        """Mute the mentioned user indefinitely!"""
        await ctx.respond(embed=await Union(user=member).mute(ctx.author, ctx.guild.roles, reason))

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member you would like to unmute",
        required=True,
        input_type=discord.Member
    )
    async def unmute(self, ctx: Context, member: discord.Member) -> None:
        """Unmute the mentioned user!"""
        await ctx.respond(embed=await Union(user=member).unmute(ctx.guild.roles))

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member you would like to kick",
        required=True,
        input_type=discord.Member
    )
    @bridge.bridge_option(
        name="reason",
        description="The reason behind the kick",
        required=False,
        input_type=str
    )
    async def kick(self, ctx: Context, member: discord.Member, *, reason: str = None) -> None:
        """Kick the mentioned user!"""
        await ctx.respond(embed=await Union(user=member).kick(ctx.author, reason))

    @bridge.bridge_command()
    @commands.has_permissions(ban_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member you would like to ban",
        required=True,
        input_type=discord.Member
    )
    @bridge.bridge_option(
        name="reason",
        description="The reason behind the ban",
        required=False,
        input_type=str
    )
    async def ban(self, ctx: Context, member: discord.Member, *, reason: str = None) -> None:
        """Ban the mentioned user!"""
        await ctx.respond(embed=await Union(user=member).ban(ctx.guild, ctx.author, reason))

    @bridge.bridge_command()
    @commands.has_permissions(ban_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member you would like to softban",
        required=True,
        input_type=discord.Member
    )
    @bridge.bridge_option(
        name="reason",
        description="The reason behind the softban",
        required=False,
        input_type=str
    )
    async def softban(self, ctx: Context, member: discord.Member, *, reason: str = None) -> None:
        """Softban the mentioned user!"""
        await ctx.respond(embed=await Union(user=member).softban(ctx.guild, ctx.author, reason))

    @bridge.bridge_command()
    @commands.has_permissions(ban_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member you would like to unban",
        required=True,
        input_type=discord.User
    )
    @bridge.bridge_option(
        name="reason",
        description="The reason behind the unban",
        required=False,
        input_type=str
    )
    async def unban(self, ctx: Context, user: discord.User, *, reason: str = None) -> None:
        """Unban the mentioned user!"""
        await ctx.respond(embed=await Union(user=user).unban(ctx.guild, ctx.author, reason))

    @bridge.bridge_command()
    @commands.has_permissions(manage_messages=True)
    @bridge.bridge_option(
        name="amount",
        description="The number of messages you would like to purge",
        required=True,
        input_type=int
    )
    @bridge.bridge_option(
        name="reason",
        description="The reason behind the purge",
        required=False,
        input_type=str
    )
    async def purge(self, ctx: Context, amount: int, *, reason: str = None) -> None:
        """Clears the given number of messages!"""
        await Integer(integer=amount).purge(ctx, reason)


def setup(bot):
    bot.add_cog(Moderation(bot))
