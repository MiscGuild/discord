from discord.ext import commands

class Hypixel(commands.Cog, name="Hypixel"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def sync(self, ctx, name=None, tag=None):

    
    # @commands.command(aliases=["i"])
    # async def info(self, ctx, name=None):


    # @commands.command()
    # @commands.has_permissions(manage_messages=True)
    # async def dnkladd(self, ctx, name=None, start=None, end=None, *, reason=None):


    # @commands.command(aliases=['dnklrmv'])
    # @commands.has_permissions(manage_messages=True)


    # @commands.command()
    # async def dnkllist(self, ctx, raw=None):


    # @commands.command(aliases=['dnklchk'])
    # async def dnklcheck(self, ctx, name=None):


def setup(bot):
    bot.add_cog(Hypixel(bot))