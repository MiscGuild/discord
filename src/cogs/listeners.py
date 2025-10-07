import discord
from discord.ext import commands

from src.func.Listener import Listener


class Listeners(commands.Cog, name="listeners"):
    """
    Hidden cog.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member) -> None:
        await Listener(obj=member).on_member_join()

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs) -> None:
        await Listener(obj=event).on_error()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ApplicationContext, error) -> None:
        await Listener(obj=error).on_command_error(ctx)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error) -> None:
        await Listener(obj=error).on_application_command_error(ctx)

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        await Listener(obj=message).on_invitation_message()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        await Listener(obj=(before, after)).on_member_update()

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        await Listener(obj=thread).on_thread_create()


def setup(bot):
    bot.add_cog(Listeners(bot))
