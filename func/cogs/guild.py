from discord.ext import commands

class Guild(commands.Cog, name="Guild"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(aliases=["gi"])
    # async def ginfo(self, ctx, *, name):


    # @commands.command(aliases=['ge'])
    # async def gexp(self, ctx, gname):


    # @commands.command()
    # async def gactive(self, ctx):


    # @commands.command()
    # async def ginactive(self, ctx):


    # @commands.command(aliases=['gr'])
    # async def grank(self, ctx, reqrank):


    # @commands.command(aliases=['gm', 'g'])
    # async def gmember(self, ctx, name=None):

    # @commands.command(aliases=["gt"])
    # async def gtop(self, ctx):


    # @commands.command()
    # async def dailylb(self, ctx, x=1):


    # @commands.command(aliases=['req', 'requirement'])
    # async def requirements(self, ctx):

    # @commands.command(aliases=['res'])
    # async def resident(self, ctx):


    # @commands.command(aliases=['ticket'])
    # async def tickets(self, ctx):


def setup(bot):
    bot.add_cog(Guild(bot))