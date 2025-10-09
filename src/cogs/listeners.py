import discord
from discord.ext import commands

from src.func.Listener import Listener


class Listeners(commands.Cog, name="listeners"):
    """Hidden cog."""

    def __init__(self, bot):
        self.bot = bot
        self._listener = Listener(bot)  # optional: reuse one, or construct per-call

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await self._listener.on_member_join(member)

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs) -> None:
        # event is a string event name per discord.py
        await self._listener.on_error(event)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await self._listener.on_command_error(ctx, error)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception) -> None:
        await self._listener.on_application_command_error(ctx, error)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self._listener.on_invitation_message(message)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        await self._listener.on_member_update(before, after)

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        await self._listener.on_thread_create(thread)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction) -> None:
        await self._listener.on_interaction(interaction)


def setup(bot):
    bot.add_cog(Listeners(bot))
