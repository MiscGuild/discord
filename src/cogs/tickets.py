import discord

from discord.ext import commands, bridge
from src.func.General import General
from src.func.Listener import Listener
from src.func.String import String
from src.func.Union import Union


class Tickets(commands.Cog, name="tickets"):
    """
    Everything to do with tickets.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(aliases=["reg", "verify"])
    async def register(self, ctx, name: str):
        """Register with your IGN to sync your roles!"""
        res = await Union(user=ctx.author).register(ctx, name)
        if isinstance(res, discord.Embed):
            await ctx.respond(embed=res)
        if isinstance(res, String):
            await ctx.respond(res)

    @bridge.bridge_command(aliases=["del"])
    @commands.has_role("Staff")
    async def delete(self, ctx):
        """Delete a ticket!"""
        res = await General.delete(ctx)
        if res:
            await ctx.respond(res)

    @bridge.bridge_command()
    @commands.has_role("Staff")
    async def add(self, ctx, member: discord.Member):
        """Add a user to a ticket!"""
        res = await Union(user=member).add(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_role("Staff")
    async def remove(self, ctx, member: discord.Member):
        """Remove a user from a ticket!"""
        res = await Union(user=member).remove(ctx)
        if isinstance(res, str):
            await ctx.respond(res)
        elif isinstance(res, discord.Embed):
            await ctx.respond(embed=res)

    @bridge.bridge_command()
    @commands.has_role("Staff")
    async def rename(self, ctx, *, channel_name: str):
        """Rename a ticket!"""
        await ctx.respond(embed=await String(string=channel_name).rename(ctx))

    @bridge.bridge_command()
    @commands.has_role("Staff")
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
    async def deny(self, ctx, channel: discord.TextChannel):
        """Deny a staff application!"""
        # Get result and send file if it is returned
        embed, file = await General.deny(ctx, channel)
        await channel.respond(embed=embed)
        if file:
            return await channel.respond(file=file)

    @bridge.bridge_command()
    async def new(self, ctx):
        """Create a new ticket!"""
        await ctx.respond(await General.new(ctx))

    @bridge.bridge_command(aliases=['AddMilestone'])
    @commands.has_role('Staff')
    async def milestoneadd(self, ctx, gamemode: str = None,*, milestone: str = None):
        """Register a milestone"""
        embed, view = await General.add_milestone(ctx, gamemode, milestone)
        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(aliases=['UpdateMilestone'])
    @commands.has_role('Staff')
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
