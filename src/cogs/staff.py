from __main__ import bot

import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.consts import INFORMATION_MESSAGE, INFORMATION_MESSAGE_2, INFORMATION_MESSAGE_3, REQUIREMENTS_EMBED, \
    RULES_MESSAGES, ELITE_MEMBER_CATEGORIES
from src.utils.ui_utils import tickets


class Staff(commands.Cog, name="staff"):
    """
    Staff-only tools: role syncs, inactivity lists and server info.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    async def inactive(self, ctx: discord.ApplicationContext) -> None:
        """Lists members whose guild experience needs attention.

        Splits them into who to promote to Delta or Gamma, who to
        demote, and who has fallen below 50k weekly gexp and should be
        kicked. Members who joined within a week and are on a normal
        pace are left out. Nothing is changed here — it is a punch list.
        """
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
        """Force-syncs one member's nickname, tag and roles.

        Skips the Hypixel Discord link check and rewrites everything to
        match their Hypixel profile. Reach for this when `/sync` refuses
        someone, or when a rolecheck got stuck on them.
        """
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
        """Re-syncs every member's nickname and roles at once.

        Rebuilds roles from each member's guild and weekly guild
        experience, and renames everyone to their in-game name unless
        they hold a role that allows a custom tag. On a large server
        this takes several minutes — if it hangs on someone, run
        `/forcesync` on them and start again.
        """
        await General().rolecheck(ctx, send_ping)

    @bridge.bridge_command()
    @commands.has_permissions(administrator=True)
    async def information(self, ctx: discord.ApplicationContext, send_embed_only=False) -> None:
        """Posts the server's introduction and rank guide.

        Sends the guild's about page and the Discord rank guide, then
        finishes with the weekly guild experience requirements.
        """
        if not send_embed_only:
            await ctx.send(content=INFORMATION_MESSAGE)
            await ctx.send(content=INFORMATION_MESSAGE_2)
            await ctx.send(content=INFORMATION_MESSAGE_3)
        await ctx.send(embed=REQUIREMENTS_EMBED)

    @bridge.bridge_command()
    @commands.has_permissions(administrator=True)
    async def rules(self, ctx: discord.ApplicationContext) -> None:
        """Posts the in-game and Discord rule messages.

        Every rule goes out as its own message so it is easy to read
        and point at.
        """
        for message in RULES_MESSAGES:
            await ctx.send(content=message)

    @bridge.bridge_command(name="update_elite_member", description="Grant or revoke a player's Elite Member role")
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
        """Grants or revokes a player's Elite Member status.

        `reason` must be `Event Sponsor`, `GvG Team`, `YouTuber` or
        `Server Booster`. Running it again with the same reason takes
        the status away. Sponsors need a `monetary_value` of $10 or
        more, and get time added in proportion to what they spent.
        """
        await ctx.respond(
            embed=await String(string=reason, username=username).elite_member(monetary_value=monetary_value))

    @bridge.bridge_command()
    @commands.has_permissions(administrator=True)
    async def tickets(self, ctx: discord.ApplicationContext) -> None:
        """Explains how the ticketing system works.

        Lists every ticket reason available to members, to guests and to
        everyone, plus a button that starts a new ticket.
        """
        image, messages, view = await tickets()
        await ctx.send(content=messages[0])
        await ctx.send(content=messages[1], view=view)

    @bridge.bridge_command()
    @commands.has_permissions(kick_members=True)
    @bridge.bridge_option(
        name="guild_name",
        description="The name of the guild",
        required=True,
        input_type=str
    )
    async def recruit(self, ctx: discord.ApplicationContext, *, guild_name: str) -> None:
        """Lists recruitable players from another Hypixel guild.

        Shows members sitting at 100,000 or more weekly guild
        experience, with their online status and join date. Anyone who
        joined under a week ago has to be ahead of a 50k/week pace, and
        their gexp is scaled up for display.
        """
        await ctx.defer()

        res = await String(string=guild_name).recruit()

        if not res:
            await ctx.respond("No recruitable players found.")
            return

        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

        elif isinstance(res, str):
            await ctx.respond(res)

        elif isinstance(res, list):
            await ctx.respond(res[0])

            for message in res[1:]:
                await ctx.followup.send(message)


def setup(bot):
    bot.add_cog(Staff(bot))
