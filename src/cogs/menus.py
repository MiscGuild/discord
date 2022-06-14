from discord.ext import commands

from func.classes.Listener import Listener


class Menus(commands.Cog, command_attrs=dict(hidden=True), name="menus"):
    """
    Hidden cog.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reactionroles(self, ctx):
        """Send the reaction roles embeds!"""
        for embed, view in await Listener.reactionroles():
            await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.is_owner()
    async def tickets(self, ctx):
        """Send a ticket help embed!"""
        image, embed, view = await Listener.tickets(ctx)
        await ctx.send(file=image, embed=embed, view=view)


def setup(bot):
    bot.add_cog(Menus(bot))
