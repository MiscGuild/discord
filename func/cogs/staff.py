from discord.ext import commands

class Staff(commands.Cog, name="Staff"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.has_role("Staff")
    # async def inactive(self, ctx):


    # @commands.command(aliases=['fs'])
    # @commands.has_role("Staff")
    # async def forcesync(self, ctx, member: discord.Member, name):


    # @commands.command()
    # @commands.has_role("Admin")
    # async def staffreview(self, ctx):


    # @commands.command()
    # @commands.has_role("Admin")
    # async def partner(self, ctx):


    # @commands.command()
    # @commands.has_role("Staff")
    # async def rolecheck(self, ctx, send_ping=None):

def setup(bot):
    bot.add_cog(Staff(bot))