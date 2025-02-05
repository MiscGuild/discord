import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.db_utils import get_db_uuid_username_from_discord_id


class Hypixel(commands.Cog, name="hypixel"):
    """
    All discord related Hypixel commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="name",
        description="Your Minecraft Username",
        required=True,
        input_type=str
    )
    @bridge.bridge_option(
        name="tag",
        description="The Tag you'd like to put beside your username",
        required=False,
        input_type=str
    )
    async def sync(self, ctx, name, tag: str = None):
        """Update your discord nick, tag and roles!"""
        res = await Union(user=ctx.author).sync(ctx, name, tag)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command(aliases=['i'])
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player whose stats you'd like to view",
        required=False,
        input_type=str
    )
    async def info(self, ctx, name: str = None):
        """View Hypixel stats of the given user!"""
        if not name:
            uuid, username = await get_db_uuid_username_from_discord_id(ctx.author.id)
            res = await String(uuid=uuid, username=username).info()
        else:
            res = await String(string=name).info()
        await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=['dnkladd', 'dnkla'])
    @commands.has_any_role("Staff")
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player who you want to add to the do-not-kick-list",
        required=True,
        input_type=str
    )
    async def dnkl_add(self, ctx, name: str):
        """Add a user to the do-not-kick-list!"""
        res = await String(string=name).dnkladd(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command(aliases=['dnklrmv', 'dnklremove', 'dnklremv', 'dnklr'])
    @commands.has_permissions(manage_messages=True)
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player who you want to remove from the do-not-kick-list",
        required=False,
        input_type=str
    )
    @bridge.bridge_option(
        name="uuid",
        description="The UUID of the player who you want to remove from the do-not-kick-list",
        required=False,
        input_type=str
    )
    async def dnkl_remove(self, ctx, name: str = None, uuid: str = None):
        """Remove a player from the do-not-kick-list"""
        if not name and not uuid:
            await ctx.respond("Please provide either the username or the UUID of the player you want to remove.")
            return
        if name and not uuid and len(name) > 16:
            uuid = name
        if uuid:
            await ctx.respond(await String(uuid=uuid).dnklremove())
        else:
            await ctx.respond(await String(string=name).dnklremove())

    @bridge.bridge_command(aliases=['dnkllist', 'dnkll'])
    async def dnkl_list(self, ctx):
        """View all users on the do-not-kick-list!"""
        await ctx.respond(embed=await General.dnkllist(ctx))

    @bridge.bridge_command(aliases=['dnklchk', 'dnklcheck', 'dnklc'])
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player whose do-not-kick-list eligibility you'd like to check",
        required=False,
        input_type=str
    )
    async def dnkl_check(self, ctx, name: str = None):
        """Check whether you are eligible for the do-not-kick-list!"""
        if not name:
            uuid, username = await get_db_uuid_username_from_discord_id(ctx.author.id)
            res = await String(uuid=uuid, username=username).dnklcheck()
        else:
            res = await String(string=name).dnklcheck()

        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)


def setup(bot):
    bot.add_cog(Hypixel(bot))
