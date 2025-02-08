import discord
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
    async def giveawaycreate(self, ctx: discord.ApplicationContext) -> None:
        """Create a giveaway!"""
        await ctx.respond(await General().giveawaycreate(ctx))

    @bridge.bridge_command(aliases=["gend", "giveawayfinish", "gfinish"])
    @commands.has_role("Giveaway Creator")
    @bridge.bridge_option(
        name="message_id",
        description="The message ID of the giveaway you would like to end",
        required=True,
        input_type=int
    )
    async def giveawayend(self, ctx: discord.ApplicationContext, message_id: int) -> None:
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
    async def giveawayreroll(self, ctx: discord.ApplicationContext, message_id: int, reroll_number: int = None) -> None:
        """Re-rolls the giveaway with the given message ID!"""
        res = await Integer(integer=message_id).giveawayreroll(reroll_number)
        if res:
            await ctx.respond(res)

    @bridge.bridge_command(aliases=["glist"])
    async def giveawaylist(self, ctx: discord.ApplicationContext) -> None:
        """View all giveaway from the last 10 days!"""
        await ctx.respond(embed=await General().giveawaylist())


def setup(bot):
    bot.add_cog(Giveaways(bot))
