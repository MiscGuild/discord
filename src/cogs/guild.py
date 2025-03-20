import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Integer import Integer
from src.func.String import String
from src.utils.calculation_utils import check_if_mention
from src.utils.consts import gvg_info_embed, requirements_embed, resident_embed
from src.utils.db_utils import get_db_uuid_username, get_all_usernames


class Guild(commands.Cog, name="guild"):
    """
    Everything to do with Hypixel guilds. Commands to view guild experience, requirements and more!
    """

    def __init__(self, bot):
        self.bot = bot

    async def get_username_autocomplete(self, ctx: discord.AutocompleteContext):
        username_list = await get_all_usernames()  # Fetch all usernames (list of tuples)
        query = ctx.value.lower()
        filtered_usernames = [
            (value, name) for value, name in username_list if query in name.lower()
        ]
        return [discord.OptionChoice(name, value) for value, name in filtered_usernames[:25]]

    @bridge.bridge_group(name="g", description="Invoke guild related commands!", invoke_without_command=True)
    async def g(self, ctx: bridge.BridgeContext, name: str | discord.Member = None) -> None:
        """Invoke guild related commands!"""
        member_id = await check_if_mention(name)
        if not name and not member_id:
            username, uuid = await get_db_uuid_username(discord_id=ctx.author.id)
            res = await String(uuid=uuid, username=username).gmember(ctx)
        elif member_id:
            username, uuid = await get_db_uuid_username(discord_id=member_id)
            res = await String(uuid=uuid, username=username).gmember(ctx)
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
        """View the given user's guild experience over the past week!"""
        uuid = None
        if len(name) == 32:
            uuid = name
        if not name and not discord_member:
            username, uuid = await get_db_uuid_username(discord_id=ctx.author.id)
            res = await String(uuid=uuid, username=username).gmember(ctx)
        elif discord_member:
            username, uuid = await get_db_uuid_username(discord_id=discord_member.id)
            res = await String(uuid=uuid, username=username).gmember(ctx)
        else:
            if uuid:
                res = await String(uuid=uuid).gmember(ctx)
            else:
                res = await String(string=name).gmember(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res, ephemeral=True)

    @g.command(name="weekly", aliases=["weekly_gexp_lb", "weeklylb", "wlb"])
    async def weekly_gexp_lb(self, ctx: discord.ApplicationContext) -> None:
        """View the weekly guild experience leaderboard!"""
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
        """View the daily guild experience leaderboard!"""
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
        """View guild experience requirements!"""
        await ctx.respond(embed=requirements_embed)

    @bridge.bridge_command(aliases=["res"])
    async def resident(self, ctx: discord.ApplicationContext) -> None:
        """See the different ways of obtaining the resident rank!"""
        await ctx.respond(embed=resident_embed)

    @bridge.bridge_command()
    async def gvg(self, ctx: discord.ApplicationContext):
        """View information about GvG team and the requirements!!"""
        await ctx.respond(embed=gvg_info_embed)

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
        """View a user's invitation stats"""
        await ctx.defer()

        uuid = None
        if name and len(name) == 32:
            uuid = name
        if not name and not discord_member:
            username, uuid = await get_db_uuid_username(discord_id=ctx.author.id)
            res = await String(uuid=uuid, username=username).invites()
        elif discord_member:
            username, uuid = await get_db_uuid_username(discord_id=discord_member.id)
            res = await String(uuid=uuid, username=username).invites()
        else:
            if uuid:
                res = await String(uuid=uuid).invites()
            else:
                res = await String(string=name).invites()

        await ctx.respond(embed=res)


def setup(bot):
    bot.add_cog(Guild(bot))
