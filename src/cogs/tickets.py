import discord
from discord.commands import option
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Listener import Listener
from src.func.String import String
from src.func.Union import Union
from src.utils.consts import milestone_categories


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
    async def register(self, ctx, name: str):
        """Register with your IGN to sync your roles!"""
        res, guest_ticket = await Union(user=ctx.author).register(ctx, name)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
            if guest_ticket:
                await ctx.followup.send(f"Head on over to <#{guest_ticket.id}>!", ephemeral=True)
        if isinstance(res, String):
            await ctx.respond(res)

    @bridge.bridge_command(aliases=["del"])
    @commands.has_any_role("Staff", "Discord Moderator")
    async def delete(self, ctx):
        """Delete a ticket!"""
        res = await General.delete(ctx)
        if res:
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    @option(
        name="member",
        description="The Discord user you would like to add to the ticket",
        required=True,
        input_type=discord.Member
    )
    async def add(self, ctx, member: discord.Member):
        """Add a user to a ticket!"""
        res = await Union(user=member).add(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    @option(
        name="member",
        description="The Discord user you would like to remove from the ticket",
        required=True,
        input_type=discord.Member
    )
    async def remove(self, ctx, member: discord.Member):
        """Remove a user from a ticket!"""
        res = await Union(user=member).remove(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    @option(
        name="channel_name",
        description="The new name for the channel",
        required=False,
        input_type=str
    )
    async def rename(self, ctx, *, channel_name: str):
        """Rename a ticket!"""
        await ctx.respond(embed=await String(string=channel_name).rename(ctx))

    @bridge.bridge_command()
    @commands.has_any_role("Staff", "Discord Moderator")
    async def transcript(self, ctx):
        """Create a transcript for a ticket!"""
        res = await General.transcript(ctx)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        elif isinstance(res, discord.File):
            await ctx.respond(file=res)
        elif isinstance(res, str):
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_role("Admin")
    async def accept(self, ctx):
        """Accept a staff application!"""
        res = await General.accept(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_any_role("Admin", "Moderator")
    @option(
        name="channel",
        description="The name of the channel where the staff application is",
        required=True,
        input_type=discord.TextChannel
    )
    async def deny(self, ctx, channel: discord.TextChannel):
        """Deny a staff application!"""
        # Get result and send file if it is returned
        embed, file = await General.deny(ctx, channel)
        await channel.send(embed=embed)
        if file:
            return await channel.send(file=file)

    @bridge.bridge_command()
    async def new(self, ctx):
        """Create a new ticket!"""
        await ctx.respond(await General.new(ctx))

    @bridge.bridge_command(aliases=['AddMilestone'])
    @commands.has_any_role("Staff", "Discord Moderator")
    @option(
        name="gamemode",
        description="The gamemode in which the milestone was achieved",
        choices=[discord.OptionChoice(v, value=k) for k, v in milestone_categories.items()],
        required=False
    )
    async def milestoneadd(self, ctx, gamemode: str = None, *, milestone: str = None):
        """Register a milestone"""
        embed, view = await General.add_milestone(ctx, gamemode, milestone)
        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(aliases=['UpdateMilestone'])
    @commands.has_any_role("Staff", "Discord Moderator")
    async def milestoneupdate(self, ctx):
        """Update a milestone that has already been registered"""
        embed, view = await General.update_milestone(ctx)
        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(aliases=["CompileMilestones", "mc", "cm", "CompileMilestone"])
    @commands.has_role('Staff')
    async def milestonecompile(self, ctx):
        """Compiles all milestones into one message and sends it to the milestones channel"""
        await ctx.respond(await General.compile_milestones(ctx))

    @commands.Cog.listener()
    async def on_interaction(self, res):
        await Listener(obj=res).on_interaction()


def setup(bot):
    bot.add_cog(Tickets(bot))
