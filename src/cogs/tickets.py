import discord
from discord.commands import option
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.consts import MILESTONE_CATEGORIES


class Tickets(commands.Cog, name="tickets"):
    """
    Everything to do with tickets.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @option(
        name="name",
        description="Your Minecraft username",
        required=True,
        input_type=str
    )
    async def register(self, ctx: discord.ApplicationContext, name: str) -> None:
        """Register with your IGN to sync your roles!"""
        res, guest_ticket = await Union(user=ctx.author).register(ctx, name)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
            if guest_ticket:
                await ctx.followup.send(f"Head on over to <#{guest_ticket.id}>!", ephemeral=True)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command(aliases=["del"])
    @commands.has_any_role("Staff", "Discord Moderator")
    async def delete(self, ctx: discord.ApplicationContext) -> None:
        """Delete a ticket!"""
        res = await General().delete(ctx)
        if res:
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    @bridge.bridge_option(
        name="member",
        description="The Discord user you would like to add to the ticket",
        required=True,
        input_type=discord.Member
    )
    async def add(self, ctx: discord.ApplicationContext, member: discord.Member) -> None:
        """Add a user to a ticket!"""
        res = await Union(user=member).add(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    @bridge.bridge_option(
        name="member",
        description="The Discord user you would like to remove from the ticket",
        required=True,
        input_type=discord.Member
    )
    async def remove(self, ctx: discord.ApplicationContext, member: discord.Member) -> None:
        """Remove a user from a ticket!"""
        res = await Union(user=member).remove(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    @bridge.bridge_option(
        name="channel_name",
        description="The new name for the channel",
        required=False,
        input_type=str
    )
    async def rename(self, ctx: discord.ApplicationContext, *, channel_name: str) -> None:
        """Rename a ticket!"""
        res = await String(string=channel_name).rename(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    async def transcript(self, ctx: discord.ApplicationContext) -> None:
        """Create a transcript for a ticket!"""
        res = await General().transcript(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, discord.File):
            await ctx.respond(file=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_role("Admin")
    async def accept(self, ctx: discord.ApplicationContext) -> None:
        """Accept a staff application!"""
        res = await General().accept(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_any_role("Admin", "Moderator")
    @bridge.bridge_option(
        name="channel",
        description="The name of the channel where the staff application is",
        required=True,
        input_type=discord.TextChannel
    )
    async def deny(self, ctx: discord.ApplicationContext, channel: discord.TextChannel) -> discord.Message | None:
        """Deny a staff application!"""
        # Get result and send file if it is returned
        embed, file = await General().deny(ctx, channel)
        await channel.send(embed=embed)
        if file:
            return await channel.send(file=file)

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="reason",
        description="The reason for creating the ticket",
        required=False,
        input_type=str
    )
    async def new(self, ctx: discord.ApplicationContext, *, reason: str = None) -> None:
        """Create a new ticket!"""
        await ctx.defer()
        await ctx.respond(await General().new(ctx, reason))

        # Main command group: `/milestone`

    @bridge.bridge_group(name="milestone", description="Manage milestones", invoke_without_command=True)
    async def milestone(self, ctx: bridge.BridgeContext):
        if ctx.invoked_subcommand is None:  # Ensures this runs only if no subcommand is called
            await ctx.respond("Use `/milestone add`, `/milestone update`, or `/milestone compile`.")

    # Subcommand: `/milestone add`
    @milestone.command(name="add", aliases=['a'], description="Register a milestone")
    @commands.has_any_role("Staff", "Discord Moderator")
    @bridge.bridge_option(
        name="gamemode",
        description="The gamemode in which the milestone was achieved",
        choices=[discord.OptionChoice(v, value=k) for k, v in MILESTONE_CATEGORIES.items()],
        required=False
    )
    async def milestone_add(self, ctx: bridge.BridgeContext, gamemode: str = None, *,
                            milestone: str = None) -> None:
        embed, view = await General().add_milestone(ctx, gamemode, milestone)
        await ctx.respond(embed=embed, view=view)

    # Subcommand: `/milestone update`
    @milestone.command(name="update", aliases=['u'], description="Update an existing milestone")
    @commands.has_any_role("Staff", "Discord Moderator")
    async def milestone_update(self, ctx: bridge.BridgeContext) -> None:
        embed, view = await General().update_milestone(ctx)
        await ctx.respond(embed=embed, view=view)

    # Subcommand: `/milestone compile`
    @milestone.command(name="compile", aliases=["c"],
                       description="Compiles all milestones into one message")
    @commands.has_any_role("Staff", "Discord Moderator")
    async def milestone_compile(self, ctx: bridge.BridgeContext) -> None:
        await ctx.defer()
        await ctx.respond(await General().compile_milestones())


def setup(bot):
    bot.add_cog(Tickets(bot))
