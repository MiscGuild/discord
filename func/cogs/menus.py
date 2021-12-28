from discord.ext import commands

from func.classes.Listener import Listener


class Menus(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.is_owner()
    # async def reaction_roles(self, ctx):

    # @commands.command()
    # @commands.is_owner()
    # async def ticket_embed(self, ctx):

    # @commands.Cog.listener()
    # async def on_button_click(self, res):
    #     await Listener(res=res).on_button_click()

    # @commands.Cog.listener()
    # async def on_select_option(self, res):
    #     await Listener(res=res).on_select_option()


def setup(bot):
    bot.add_cog(Menus(bot))
