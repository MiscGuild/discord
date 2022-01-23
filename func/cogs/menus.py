from discord.ext import commands

from func.classes.Func import Func


class Menus(commands.Cog, command_attrs=dict(hidden=True), name="menus"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reactionroles(self, ctx):
        """Send the reaction roles embeds!"""
        for embed, view in await Func.reactionroles():
            await ctx.send(embed=embed, view=view)

    # @commands.command()
    # @commands.is_owner()
    # async def ticket_embed(self, ctx):


def setup(bot):
    bot.add_cog(Menus(bot))
