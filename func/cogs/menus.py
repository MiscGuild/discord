from discord.ext import commands

from func.classes.Listener import Listener


class Menus(commands.Cog, command_attrs=dict(hidden=True), name="menus"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.is_owner()
    # async def reaction_roles(self, ctx):

    # @commands.command()
    # @commands.is_owner()
    # async def ticket_embed(self, ctx):


def setup(bot):
    bot.add_cog(Menus(bot))
