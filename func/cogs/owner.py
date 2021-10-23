from discord.ext import commands

class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted = []

    # @commands.command()
    # @commands.is_owner()
    # async def load(self, ctx, extension):


    # @commands.command()
    # @commands.is_owner()
    # async def unload(self, ctx, extension):


    # @commands.command()
    # @commands.is_owner()
    # async def reload(self, ctx, extension):


def setup(bot):
    bot.add_cog(Owner(bot))