import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.calculation_utils import get_username_autocomplete
from src.utils.data_classes import RegisteredDiscordMember
from src.utils.db_utils import get_dnkl_list


async def get_dnkl_autocomplete(ctx: discord.AutocompleteContext):
    """
    Suggests do-not-kick list entries by name.

    The value is the player's UUID, so the name is re-resolved live once
    the command runs.
    """
    dnkl_list = await get_dnkl_list()
    return [discord.OptionChoice(name, value) for name, value in dnkl_list]


class Hypixel(commands.Cog, name="hypixel"):
    """
    Sync your Discord profile and manage the do-not-kick list.
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
        """Updates your nickname, tag and roles from your Hypixel profile.

        Link your Discord account under *Social Media → DISCORD* on your
        Hypixel profile first. Pass a `tag` to append one to your
        nickname — that needs a tag-permitted role, and it is capped at
        six characters with no profanity. Your nickname is overwritten
        every time.
        """
        res = await Union(user=ctx.author).sync(ctx, name, tag)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_group(name="dnkl", description="Check, add and remove players on the do-not-kick list",
                         invoke_without_command=True)
    async def dnkl(self, ctx: bridge.BridgeContext):
        """
        Manage the do-not-kick list.

        Running it on its own just points you at the subcommands.
        """
        if ctx.invoked_subcommand is None:  # Ensures this runs only if no subcommand is called
            await ctx.respond("Use `/dnkl add`, `/dnkl remove`, or `/dnkl list`, or `/dnkl check`.")

    @dnkl.command(name="add", aliases=['a'])
    @commands.has_any_role("Staff")
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player you want to add to the do-not-kick list",
        autocomplete=get_username_autocomplete,
        required=True,
        input_type=str
    )
    async def dnkl_add(self, ctx: discord.ApplicationContext, name: str) -> None:
        """Starts a do-not-kick application for a player.

        Asks for a start date, a length and a reason right here in the
        channel you run it in, then posts a summary for staff to
        approve or deny. Aiming for over three weeks is refused
        outright, and so is "Banned on Hypixel".
        """
        if name and len(name) == 32:
            res = await String(uuid=name).dnkladd(ctx)
        else:
            res = await String(string=name).dnkladd(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @dnkl.command(name="remove", aliases=['rmv', 'r'])
    @commands.has_permissions(manage_messages=True)
    @bridge.bridge_option(
        name="player",
        description="The player you would like to remove from the do-not-kick list",
        autocomplete=get_dnkl_autocomplete,  # Use autocomplete function
        required=False
    )
    async def dnkl_remove(self, ctx: discord.ApplicationContext, player: str) -> None:
        """Removes a player from the do-not-kick list.

        Deletes their database entry and the public announcement in the
        do-not-kick channel.
        """
        await ctx.respond(await String(uuid=player).dnklremove())

    @dnkl.command(name="list", aliases=['l'])
    async def dnkl_list(self, ctx: discord.ApplicationContext) -> None:
        """Lists everyone currently on the do-not-kick list.

        Each entry shows their start date, how long they asked for and
        the reason they gave.
        """
        await ctx.respond(embed=await General().dnkllist())

    @dnkl.command(name="check", aliases=['chk', 'c'])
    @bridge.bridge_option(
        name="name",
        description="The Minecraft username of the player whose do-not-kick-list eligibility you'd like to check",
        autocomplete=get_username_autocomplete,
        required=False,
        input_type=str
    )
    async def dnkl_check(self, ctx: discord.ApplicationContext, name: str = None) -> None:
        """Checks if a player meets the 100k weekly gexp requirement.

        Shows their weekly gexp against the bar and defaults to your own
        account. Clearing the bar is not a guarantee — staff still
        decide each application on its own.
        """

        if name and len(name) == 32:
            res = await String(uuid=name).dnklcheck()
        elif not name:
            member_lookup = RegisteredDiscordMember()
            member = await member_lookup.from_discord_id(discord_id=ctx.author.id)
            res = await String(uuid=member.uuid).dnklcheck()
        else:
            res = await String(string=name).dnklcheck()

        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)


def setup(bot):
    bot.add_cog(Hypixel(bot))
