from discord.ext import commands
from func.classes.Func import Func
from func.classes.Integer import Integer


class Giveaways(commands.Cog, name="giveaways"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["gcreate"])
    @commands.has_role("Giveaway Creator")
    async def giveawaycreate(self, ctx):
        """Create a giveaway!"""
        await ctx.send(await Func.giveawaycreate(ctx))

    @commands.command(aliases=["gend", "giveawayfinish", "gfinish"])
    @commands.has_role("Giveaway Creator")
    async def giveawayend(self, ctx, message_ID: int):
        """Ends the giveaway with the given message ID!"""
        res = await Integer(integer=message_ID).giveawayend()
        if res != None:
            await ctx.send()

    @commands.command(aliases=["greroll", "reroll"])
    @commands.has_role("Giveaway Creator")
    async def giveawayreroll(self, ctx, message_ID: int, reroll_number: int=None):
        """Rerolls the giveaway with the given message ID!"""
        res = await Integer(integer=message_ID).giveawayreroll(reroll_number)
        if res != None:
            await ctx.send(res)

    @commands.command(aliases=["glist"])
    async def giveawaylist(self, ctx):
        """View all giveaway from the last 10 days!"""
        await ctx.send(embed=await Func.giveawaylist())


def setup(bot):
    bot.add_cog(Giveaways(bot))
