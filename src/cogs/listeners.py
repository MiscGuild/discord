from discord.ext import commands
from src.func.Listener import Listener


class Listeners(commands.Cog, name="listeners"):
    """
    Hidden cog.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await Listener(obj=member).on_member_join()

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        await Listener(obj=event).on_error()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await Listener(obj=error).on_command_error(ctx)

    @commands.Cog.listener()
    async def on_message(self, message):
        await Listener(obj=message).on_message()


def setup(bot):
    bot.add_cog(Listeners(bot))
