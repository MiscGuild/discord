from discord.ext import commands

from func.classes.Listener import Listener


class Listeners(commands.Cog, name="listeners"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await Listener.on_member_join(member)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        await Listener.on_error(event)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
       await Listener.on_command_error(ctx, error)

    # @commands.Cog.listener()
    # async def on_guild_channel_create(self, channel):

    # @commands.Cog.listener()
    # async def on_button_click(self, res):
    #     await Listener(res=res).on_button_click()

    # @commands.Cog.listener()
    # async def on_select_option(self, res):
    #     await Listener(res=res).on_select_option()


def setup(bot):
    bot.add_cog(Listeners(bot))