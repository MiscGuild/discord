import discord
from discord.ext import commands, bridge

from src.func.Integer import Integer
from src.func.Union import Union


class Moderation(commands.Cog, name="moderation"):
    """
    Mute, kick, ban and purge members. Needs moderator permissions.
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
    async def mute(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str = None) -> None:
        """Times a member out by applying the `Muted` role.

        The mute is **indefinite** — there is no duration or timeout.
        Clear it again with `/unmute` when they are done.
        """
        await ctx.respond(embed=await Union(user=member).mute(ctx.author, ctx.guild.roles, reason))

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    @bridge.bridge_option(
        name="member",
        description="The Discord member you would like to unmute",
        required=True,
        input_type=discord.Member
    )
    async def unmute(self, ctx: discord.ApplicationContext, member: discord.Member) -> None:
        """Removes the `Muted` role from a member.

        Only reverses the mute itself. It does not restore any earlier
        timeout, nickname or role state.
        """
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
    async def kick(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str = None) -> None:
        """Kicks a member from the server.

        They can rejoin with an invite, but their roles are not restored
        automatically — run `/rolecheck` to re-sync the whole server.
        """
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
    async def ban(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str = None) -> None:
        """Permanently bans a member from the server.

        This is a full ban, not a timeout. Reverse a mistake with
        `/unban`.
        """
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
    async def softban(self, ctx: discord.ApplicationContext, member: discord.Member, *, reason: str = None) -> None:
        """Bans then immediately unbans a member.

        Effectively removes them and clears their recent messages while
        still letting them rejoin. Use `/ban` for a real removal.
        """
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
    async def unban(self, ctx: discord.ApplicationContext, user: discord.User, *, reason: str = None) -> None:
        """Lifts an existing ban on a user.

        Works on someone who has already left the server. It does not
        restore the roles or nickname they had before.
        """
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
    async def purge(self, ctx: discord.ApplicationContext, amount: int, *, reason: str = None) -> None:
        """Bulk-deletes messages from the channel.

        Nothing is sent back here — a transcript of what was deleted is
        saved to the log channel instead. Discord refuses to bulk-delete
        messages older than 14 days, so you may get fewer than asked.
        """
        await Integer(integer=amount).purge(ctx, reason)


def setup(bot):
    bot.add_cog(Moderation(bot))
