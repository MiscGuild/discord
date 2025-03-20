import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.db_utils import get_dnkl_list, get_db_uuid_username


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
        required=False,
        input_type=str
    )
    @bridge.bridge_option(
        name="tag",
        description="The Tag you'd like to put beside your username",
        required=False,
        input_type=str
    )
    async def sync(self, ctx: discord.ApplicationContext, name: str = None, tag: str = None) -> None:
        """Update your discord nick, tag and roles!"""
        res = await Union(user=ctx.author).sync(ctx, name, tag)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    # @bridge.bridge_command(aliases=['i'])
    # @bridge.bridge_option(
    #     name="name",
    #     description="The Minecraft username of the player whose stats you'd like to view",
    #     required=False,
    #     input_type=str
    # )
    # async def info(self, ctx: discord.ApplicationContext, name: str = None) -> None:
    #     """View Hypixel stats of the given user!"""
    #     if not name:
    #         uuid, username = await get_db_uuid_username(discord_id=ctx.author.id)
    #         res = await String(uuid=uuid, username=username).info()
    #     else:
    #         res = await String(string=name).info()
    #     await ctx.respond(embed=res)

    @bridge.bridge_group(name="dnkl", description="Manage dnkl-related things", invoke_without_command=True)
    async def dnkl(self, ctx: bridge.BridgeContext):
        if ctx.invoked_subcommand is None:  # Ensures this runs only if no subcommand is called
            await ctx.respond("Use `/dnkl add`, `/dnkl remove`, or `/dnkl list`, or `/dnkl check`.")

    @dnkl.command(name="add", aliases=['a'])
    @commands.has_any_role("Staff")
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player you want to add to the do-not-kick list",
        required=True,
        input_type=str
    )
    async def dnkl_add(self, ctx: discord.ApplicationContext, name: str) -> None:
        """Add a user to the do-not-kick list!"""
        res = await String(string=name).dnkladd(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    async def get_dnkl_autocomplete(self, ctx: discord.AutocompleteContext):
        dnkl_list = await get_dnkl_list()
        return [discord.OptionChoice(name, value) for name, value in dnkl_list]

    @dnkl.command(name="remove", aliases=['rmv', 'r'])
    @commands.has_permissions(manage_messages=True)
    @bridge.bridge_option(
        name="player",
        description="The player you would like to remove from the do-not-kick list",
        autocomplete=get_dnkl_autocomplete,  # Use autocomplete function
        required=False
    )
    async def dnkl_remove(self, ctx: discord.ApplicationContext, player: str) -> None:
        """Remove a player from the do-not-kick list"""
        await ctx.respond(await String(uuid=player).dnklremove())
        # if not name and not uuid:
        #     await ctx.respond("Please provide either the username or the UUID of the player you want to remove.")
        #     return
        # if name and not uuid and len(name) > 16:
        #     uuid = name
        # if uuid:
        #     await ctx.respond(await String(uuid=uuid).dnklremove())
        # else:
        #     await ctx.respond(await String(string=name).dnklremove())

    @dnkl.command(name="list", aliases=['l'])
    async def dnkl_list(self, ctx: discord.ApplicationContext) -> None:
        """View all users on the do-not-kick list!"""
        await ctx.respond(embed=await General().dnkllist())

    @dnkl.command(name="check", aliases=['chk', 'c'])
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player whose do-not-kick-list eligibility you'd like to check",
        required=False,
        input_type=str
    )
    async def dnkl_check(self, ctx: discord.ApplicationContext, name: str = None) -> None:
        """Check whether a player is on the do-not-kick list!"""
        if not name:
            username, uuid = await get_db_uuid_username(discord_id=ctx.author.id)
            res = await String(uuid=uuid, username=username).dnklcheck()
        else:
            res = await String(string=name).dnklcheck()

        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)


def setup(bot):
    bot.add_cog(Hypixel(bot))
