from discord.ext import commands

class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot


    # Command from https://github.com/Rapptz/RoboDanny
    # @commands.command()
    # async def source(self, ctx, *, command: str = None):


    # @commands.command()
    # async def ping(self, ctx):


    # @commands.command()
    # async def avatar(self, ctx, member: discord.User):


def setup(bot):
    bot.add_cog(General(bot))