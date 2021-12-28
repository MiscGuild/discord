import discord
from discord.ext import commands

from func.classes.String import String

from func.utils.discord.name_grabber import name_grabber

class Hypixel(commands.Cog, name="Hypixel"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx, name: str, tag: str=None):
        """Update your discord nick, tag and roles!"""
        result = await String(string=name).sync(ctx, tag)
        if isinstance(result, discord.Embed):
            await ctx.send(embed=result)
        elif isinstance(result, str):
            await ctx.send(result)

    
    # @commands.command(aliases=["i"])
    # async def info(self, ctx, name: str=None):
    #     await ctx.send(embed=await String(string=name).info())


    # @commands.command()
    # @commands.has_permissions(manage_messages=True)
    # async def dnkladd(self, ctx, name=None, start=None, end=None, *, reason=None):


    # @commands.command(aliases=['dnklrmv'])
    # @commands.has_permissions(manage_messages=True)
    # async def dnklremove(self, ctx, name: str):
    #     result = await String(string=name).dnklremove()
    #     # Send result according to returned value
    #     if isinstance(result, discord.Embed):
    #         await ctx.send(embed=result)
    #     elif isinstance(result, str):
    #         await ctx.send(result)


    # @commands.command()
    # async def dnkllist(self, ctx, raw: str=None):
    #     result = await String(string=raw).dnkllist()
    #     # Send result according to returned value
    #     if isinstance(result, discord.Embed):
    #         await ctx.send(embed=result)


    @commands.command(aliases=['dnklchk'])
    async def dnklcheck(self, ctx, name: str=None):
        """Check whether you are eligible for the do-not-kick-list!"""
        if name == None:
            name = await name_grabber(ctx.author)

        result = await String(string=name).dnklcheck()
        # Send result according to returned value
        if isinstance(result, discord.Embed):
            await ctx.send(embed=result)
        elif isinstance(result, str):
            await ctx.send(result)


def setup(bot):
    bot.add_cog(Hypixel(bot))
