import discord
from discord.ext import commands
from func.classes.Func import Func
from func.classes.Listener import Listener
from func.classes.String import String
from func.classes.Union import Union


class Tickets(commands.Cog, name="tickets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["reg", "verify"])
    async def register(self, ctx, name: str):
        """Register with your IGN to sync your roles!"""
        res = await Union(user=ctx.author).register(ctx, name)
        if isinstance(res, discord.Embed):
            await ctx.send(embed=res)
        if isinstance(res, String):
            await ctx.send(res)

    @commands.command(aliases=["del"])
    @commands.has_role("Staff")
    async def delete(self, ctx):
        """Delete a ticket!"""
        res = await Func.delete(ctx)
        if res != None:
            await ctx.send(res)

    @commands.command()
    @commands.has_role("Staff")
    async def add(self, ctx, member: discord.Member):
        """Add a user to a ticket!"""
        res = await Union(user=member).add(ctx)
        if isinstance(res, str):
            await ctx.send(res)
        elif isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    @commands.command()
    @commands.has_role("Staff")
    async def remove(self, ctx, member: discord.Member):
        """Remove a user from a ticket!"""
        res = await Union(user=member).remove(ctx)
        if isinstance(res, str):
            await ctx.send(res)
        elif isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    @commands.command()
    @commands.has_role("Staff")
    async def rename(self, ctx, *, channel_name: str):
        """Rename a ticket!"""
        await String(string=channel_name).rename(ctx)

    @commands.command()
    @commands.has_role("Staff")
    async def transcript(self, ctx):
        """Create a transcript for a ticket!"""
        res = await Func.transcript(ctx)
        if isinstance(res, discord.Embed):
            await ctx.send(embed=res)
        elif isinstance(res, discord.File):
            await ctx.send(file=res)
        elif isinstance(res, str):
            await ctx.send(res)

    @commands.command()
    @commands.has_role("Admin")
    async def accept(self, ctx):
        """Accept a staff application!"""
        res = await Func.accept(ctx)
        if isinstance(res, str):
            await ctx.send(res)
        if isinstance(res, discord.Embed):
            await ctx.send(embed=res)

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def deny(self, ctx, channel: discord.TextChannel):
        """Deny a staff application!"""
        # Get result and send file if it is returned
        embed, file = await Func.deny(ctx, channel)
        await channel.send(embed=embed)
        if file != None:
            return await channel.send(file=file)

    @commands.command()
    async def new(self, ctx):
        """Create a new ticket!"""
        await ctx.send(await Func.new(ctx))

    @commands.Cog.listener()
    async def on_interaction(self, res):
        await Listener(obj=res).on_interaction()


def setup(bot):
    bot.add_cog(Tickets(bot))
