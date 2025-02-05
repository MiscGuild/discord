from discord.ext import commands, bridge

from src.func.General import General
from src.func.Integer import Integer


class Giveaways(commands.Cog, name="giveaways"):
    """
    Everything to do with giveaways. That is giveaway listing, creation, deletion and updation!
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(aliases=["gcreate"])
    @commands.has_role("Giveaway Creator")
    async def giveawaycreate(self, ctx):
        """Create a giveaway!"""
        await ctx.respond(await General.giveawaycreate(ctx))

    @bridge.bridge_command(aliases=["gend", "giveawayfinish", "gfinish"])
    @commands.has_role("Giveaway Creator")
    @bridge.bridge_option(
        name="message_id",
        description="The message ID of the giveaway you would like to end",
        required=True,
        input_type=int
    )
    async def giveawayend(self, ctx, message_id: int):
        """Ends the giveaway with the given message ID!"""
        res = await Integer(integer=message_id).giveawayend()
        if res:
            await ctx.respond(res)

    @bridge.bridge_command(aliases=["greroll", "reroll"])
    @commands.has_role("Giveaway Creator")
    @bridge.bridge_option(
        name="message_id",
        description="The message ID of the giveaway you would like to end",
        required=True,
        input_type=int
    )
    @bridge.bridge_option(
        name="reroll_number",
        description="Number of winners you would like to generate in the reroll",
        required=False,
        input_type=int
    )
    async def giveawayreroll(self, ctx, message_id: int, reroll_number: int = None):
        """Rerolls the giveaway with the given message ID!"""
        res = await Integer(integer=message_id).giveawayreroll(reroll_number)
        if res:
            await ctx.respond(res)

    @bridge.bridge_command(aliases=["glist"])
    async def giveawaylist(self, ctx):
        """View all giveaway from the last 10 days!"""
        await ctx.respond(embed=await General.giveawaylist(ctx))


def setup(bot):
    bot.add_cog(Giveaways(bot))
