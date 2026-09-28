import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Integer import Integer
from src.func.String import String
from src.utils.calculation_utils import check_if_mention, get_username_autocomplete
from src.utils.consts import GVG_INFO_EMBED, REQUIREMENTS_EMBED, RESIDENT_EMBED
from src.utils.data_classes import RegisteredDiscordMember


class Guild(commands.Cog, name="guild"):
    """
    Guild experience, leaderboards, requirements, invites and ranks.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_group(name="g", description="View guild experience, leaderboards and requirements",
                         invoke_without_command=True)
    async def g(self, ctx: bridge.BridgeContext, name: str | discord.Member = None) -> None:
        """Shortcut for `/g member`.

        Takes a username or a raw mention, or nothing at all for your own
        stats. Pair it with `/g weekly` and `/g daily` for the
        leaderboards.
        """
        member_id = await check_if_mention(name)

        member_lookup = RegisteredDiscordMember()
        if not name and not member_id:
            member = await member_lookup.from_discord_id(discord_id=ctx.author.id)
            res = await String(uuid=member.uuid, username=member.ign).gmember(ctx)
        elif member_id:
            member = await member_lookup.from_discord_id(discord_id=member_id)
            res = await String(uuid=member.uuid, username=member.ign).gmember(ctx)
        else:
            res = await String(string=name).gmember(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res, ephemeral=True)

    @g.command(name="member", aliases=["m", "gexp"])
    @bridge.bridge_option(
        name="name",
        description="The username of the player whose guild experience you'd like to view",
        autocomplete=get_username_autocomplete,
        required=False,
    )
    @bridge.bridge_option(
        name="member",
        description="The discord member whose guild experience you'd like to view",
        required=False,
        input_type=discord.Member
    )
    async def gmember(self, ctx: discord.ApplicationContext, name: str = None,
                      discord_member: discord.Member = None) -> None:
        """Shows a player's guild experience for the week.

        Includes their rank, a 7-day gexp graph and all-time totals.
        Takes a username, a mention, or nothing for your own stats.
        Outside `#commands` and tickets you get a one-line reply
        instead, sent just to you.
        """
        uuid = None

        member_lookup = RegisteredDiscordMember()
        if name and len(name) == 32:
            uuid = name
            name = None

        if not name and not discord_member:
            member = await member_lookup.from_discord_id(discord_id=ctx.author.id)
            res = await String(uuid=member.uuid, username=member.ign).gmember(ctx)
        elif discord_member:
            member = await member_lookup.from_discord_id(discord_id=discord_member.id)
            res = await String(uuid=member.uuid, username=member.ign).gmember(ctx)
        elif uuid:
            res = await String(uuid=uuid).gmember(ctx)
        elif name:
            res = await String(string=name).gmember(ctx)

        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res, ephemeral=True)

    @g.command(name="weekly", aliases=["weekly_gexp_lb", "weeklylb", "wlb"])
    async def weekly_gexp_lb(self, ctx: discord.ApplicationContext) -> None:
        """Shows the top 10 guild experience earners this week.

        Refreshes every Monday. Running it yourself never pings anyone.
        """
        await ctx.defer()
        res = await General().weeklylb()
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.File):
            await ctx.respond(file=res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @g.command(name="daily", aliases=["top", "lb"])
    @bridge.bridge_option(
        name="day",
        description="Specify the number of days to go back in time and retrieve the corresponding leaderboard (0-6)",
        required=False,
        input_type=int
    )
    async def gtop(self, ctx: discord.ApplicationContext, day: int = 1) -> None:
        """Shows the top 10 guild experience earners for a given day.

        Pass `0`–`6` to go back that many days, where `0` is today and
        `6` is a week ago. Defaults to yesterday.
        """
        await ctx.defer()
        res = await Integer(integer=day).gtop()
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.File):
            await ctx.respond(file=res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=["req", "reqs"])
    async def requirements(self, ctx: discord.ApplicationContext) -> None:
        """Shows the weekly guild experience needed for each rank.

        Omega 50k, Delta 200k, Gamma 400k, plus the 100k you need to be
        eligible for the do-not-kick list.
        """
        await ctx.respond(embed=REQUIREMENTS_EMBED)

    @bridge.bridge_command(aliases=["res", "elite", "elitemember", "em"])
    async def elite_member(self, ctx: discord.ApplicationContext) -> None:
        """Explains the four ways to reach Delta without grinding.

        You can qualify as a YouTuber, Event Sponsor, Server Booster or
        GvG Team Member instead of hitting 200k weekly gexp.
        """
        await ctx.respond(embed=RESIDENT_EMBED)

    @bridge.bridge_command()
    async def gvg(self, ctx: discord.ApplicationContext):
        """Explains Guild vs Guild and the stats needed to join the team.

        You need 500 BedWars wins at 1.6 FKDR, 1000 SkyWars wins at
        1.2 KDR, and 2000 Duels kills at 1.5 WLR.
        """
        await ctx.respond(embed=GVG_INFO_EMBED)

    @bridge.bridge_command(aliases=["invite", "inv"])
    @bridge.bridge_option(
        name="name",
        description="The username of the player whose invites you'd like to view",
        required=False,
        autocomplete=get_username_autocomplete
    )
    @bridge.bridge_option(
        name="member",
        description="The discord member whose invites you'd like to view",
        required=False,
        input_type=discord.Member
    )
    async def invites(self, ctx: discord.ApplicationContext, name: str = None,
                      discord_member: discord.Member = None) -> None:
        """Shows how many players a member has invited this week.

        Marks each invite valid or invalid and shows the success rate.
        An invite counts as valid if that player reaches 100k weekly
        gexp by the end of the week.
        """
        await ctx.defer()

        uuid = None
        member_lookup = RegisteredDiscordMember()

        if name and len(name) == 32:
            uuid = name
        if not name and not discord_member:
            member = await member_lookup.from_discord_id(discord_id=ctx.author.id)
            res = await String(uuid=member.uuid, username=member.ign).invites()
        elif discord_member:
            member = await member_lookup.from_discord_id(discord_id=discord_member.id)
            res = await String(uuid=member.uuid, username=member.ign).invites()
        else:
            if uuid:
                res = await String(uuid=uuid).invites()
            else:
                res = await String(string=name).invites()

        await ctx.respond(embed=res)

    @bridge.bridge_command(name="elite_members")
    async def elite_members(self, ctx: discord.ApplicationContext) -> None:
        """Lists every current Elite Member, grouped by category.

        Split into Boosters, Sponsors, GvG and Creators. A member with
        more than one category appears under each. See
        `/elite_member` for how someone qualifies.
        """
        embed = await General().elite_members()
        if isinstance(embed, discord.Embed):
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(embed=RESIDENT_EMBED)

def setup(bot):
    bot.add_cog(Guild(bot))
