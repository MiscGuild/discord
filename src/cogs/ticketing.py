import discord
from discord.commands import option
from discord.ext import commands, bridge

from src.func.General import General
from src.func.String import String
from src.func.Union import Union
from src.utils.consts import MILESTONE_CATEGORIES


class Ticketing(commands.Cog, name="ticketing"):
    """
    Open tickets, and let staff manage, rename and archive them.
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
        """Links your Discord account to your Minecraft username.

        Only works in the registration channel, and your reply is public
        — everyone in it can see your in-game name and guild. If your
        account is already linked elsewhere, a staff ticket is opened
        for you instead of overwriting anything.
        """
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
        """Closes and deletes the current ticket.

        A 10 second warning goes out, then the channel is removed. The
        transcript is saved to the log channel and DM'd to whoever
        opened the ticket, so keep your DMs open or you will lose it.
        """
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
        """Grants a member access to the current ticket.

        Gives them permission to read, send, react and upload in the
        channel without touching any of their roles. They are not
        notified, and re-adding resets them to these same defaults.
        """
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
        """Revokes a member's access to the current ticket.

        The channel disappears from their sidebar and they can no longer
        send. No messages are deleted, so `/add` brings them back.
        """
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
        """Renames the current ticket channel.

        Spaces become hyphens. The topic is left alone, so the ticket
        still knows who opened it and any milestones survive.
        """
        res = await String(string=channel_name).rename(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    async def transcript(self, ctx: discord.ApplicationContext) -> None:
        """Exports the current ticket as an HTML file.

        Just for you, and not saved anywhere. Use `/delete` instead if
        the transcript should reach the log channel and the ticket's
        creator.
        """
        res = await General().transcript(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, discord.File):
            await ctx.respond(file=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_permissions(ban_members=True)
    async def accept(self, ctx: discord.ApplicationContext) -> None:
        """Accepts a staff application.

        Posts the acceptance message in the ticket. It does not grant
        the staff role for you and does not close the ticket, so both
        are still yours to do.
        """
        res = await General().accept(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_permissions(ban_members=True)
    @bridge.bridge_option(
        name="channel",
        description="The name of the channel where the staff application is",
        required=True,
        input_type=discord.TextChannel
    )
    @bridge.bridge_option(
        name="reason",
        description="The reason for denying the application",
        required=False,
        input_type=str
    )
    async def deny(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, reason: str) -> None:
        """Denies a staff application in the given channel.

        The denial and a transcript of their answers go out publicly in
        the ticket, and the applicant is told they can apply again in
        two weeks. The ticket is left open.
        """
        denial_text, file = await General().deny(channel, reason)
        await ctx.respond(f"Denied application in {channel.mention}!", ephemeral=True)
        await channel.send(denial_text, file=file)


    @bridge.bridge_command()
    @bridge.bridge_option(
        name="reason",
        description="The reason for creating the ticket",
        required=False,
        input_type=str
    )
    async def new(self, ctx: discord.ApplicationContext, *, reason: str = None) -> None:
        """Opens a new support ticket.

        Pick your reason from the dropdown that appears, or pass it
        straight away. What you get asked next depends on the reason —
        joining the guild, reporting a player, applying for staff and
        more all follow different paths.
        """
        await ctx.defer()
        await ctx.respond(await General().new(ctx, reason))

        # Main command group: `/milestone`

    @bridge.bridge_group(name="milestone", description="Register and publish the weekly milestone board",
                         invoke_without_command=True)
    async def milestone(self, ctx: bridge.BridgeContext):
        """
        Manage the weekly milestone board.

        Running it on its own just points you at the subcommands.
        """
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
        """Registers a milestone for whoever opened this ticket.

        Pick a category from the dropdown and complete the sentence, or
        pass the category and the milestone directly. Must be run inside
        their milestone ticket — it lands in the channel topic and
        nothing is published until someone runs `/milestone compile`.
        """
        embed, view = await General().add_milestone(ctx, gamemode, milestone)
        await ctx.respond(embed=embed, view=view)

    # Subcommand: `/milestone update`
    @milestone.command(name="update", aliases=['u'], description="Update an existing milestone")
    @commands.has_any_role("Staff", "Discord Moderator")
    async def milestone_update(self, ctx: bridge.BridgeContext) -> None:
        """Edits a milestone already registered in this ticket.

        Shows a dropdown of what is on file; pick one and type the
        replacement. Must be run inside the same ticket, since the
        channel topic is the only place it is stored.
        """
        embed, view = await General().update_milestone(ctx)
        await ctx.respond(embed=embed, view=view)

    # Subcommand: `/milestone compile`
    @milestone.command(name="compile", aliases=["c"],
                       description="Compiles all milestones into one message")
    @commands.has_any_role("Staff", "Discord Moderator")
    async def milestone_compile(self, ctx: bridge.BridgeContext) -> None:
        """Publishes this week's milestones and closes the tickets.

        Everything in the MILESTONES category goes out to the weekly
        board, then those ticket channels are deleted — so it can only
        be run once a week, and a mistake loses the tickets.
        """
        await ctx.defer()
        await ctx.respond(await General().compile_milestones())


def setup(bot):
    bot.add_cog(Ticketing(bot))
