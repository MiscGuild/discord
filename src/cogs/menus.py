import discord
from discord.ext import commands, bridge

from src.utils.ui_utils import reactionroles, tickets


class Menus(commands.Cog, command_attrs=dict(hidden=True), name="menus"):
    """
    Hidden cog.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @commands.is_owner()
    async def reactionroles(self, ctx: discord.ApplicationContext) -> None:
        """Send the reaction roles embeds!"""
        for embed, view in await reactionroles():
            await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.is_owner()
    async def tickets(self, ctx: discord.ApplicationContext) -> None:
        """Send a ticket help embed!"""
        image, embed, view = await tickets()
        await ctx.send(file=image, embed=embed, view=view)


def setup(bot):
    bot.add_cog(Menus(bot))
