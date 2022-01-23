from discord.ext import commands

from func.classes.Integer import Integer


class Giveaways(commands.Cog, name="giveaways"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(aliases=["gcreate"])
    # @commands.has_role("Giveaway Creator")
    # async def giveawaycreate(self, ctx):

    @commands.command(aliases=["gend", "giveawayfinish", "gfinish"])
    @commands.has_role("Giveaway Creator")
    async def giveawayend(self, ctx, message_ID: int):
        """Ends the giveaway with the given message ID!"""
        await ctx.send(await Integer(integer=message_ID).giveawayend())

    @commands.command(aliases=["greroll", "reroll"])
    @commands.has_role("Giveaway Creator")
    async def giveawayreroll(self, ctx, message_ID: int, reroll_number: int=None):
        """Rerolls the giveaway with the given message ID!"""
        await ctx.send(await Integer(integer=message_ID).giveawayreroll(reroll_number))

    # @commands.command(aliases=["glist"])
    # async def giveawaylist(self, ctx):


def setup(bot):
    bot.add_cog(Giveaways(bot))
