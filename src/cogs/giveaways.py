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

    @bridge.bridge_group(name="giveaway", description="Manage giveaways", invoke_without_command=True)
    async def giveaway(self, ctx: bridge.BridgeContext):
        if ctx.invoked_subcommand is None:  # Ensures this runs only if no subcommand is called
            await ctx.respond("Use `/giveaway create`, `/giveaway end `, or `/giveaway reroll` or `/giveaway end`.")

    @giveaway.command(name="create", aliases=["gcreate"])
    @commands.has_role("Giveaway Creator")
    async def giveaway_create(self, ctx: discord.ApplicationContext) -> None:
        """Create a giveaway!"""
        await ctx.respond(
            "Please provide the required information to create the giveaway by responding to the following prompts!")
        await General().giveawaycreate(ctx)

    @giveaway.command(name="end", aliases=["gend", "giveawayfinish", "gfinish"])
    @commands.has_role("Giveaway Creator")
    @bridge.bridge_option(
        name="message_id",
        description="The message ID of the giveaway you would like to end",
        required=True,
        input_type=int
    )
    async def giveaway_end(self, ctx: discord.ApplicationContext, message_id: int) -> None:
        """Ends the giveaway with the given message ID!"""
        res = await Integer(integer=message_id).giveawayend()
        if res:
            await ctx.respond(res)

    @giveaway.command(name="reroll", aliases=["greroll"])
    @commands.has_role("Giveaway Creator")
    @bridge.bridge_option(
        name="message_id",
        description="The message ID of the giveaway you would like to reroll",
        required=True,
        input_type=int
    )
    @bridge.bridge_option(
        name="reroll_number",
        description="Number of winners you would like to generate in the reroll",
        required=False,
        input_type=int
    )
    async def giveaway_reroll(self, ctx: discord.ApplicationContext, message_id: int,
                              reroll_number: int = None) -> None:
        """Re-rolls the giveaway with the given message ID!"""
        res = await Integer(integer=message_id).giveawayreroll(reroll_number)
        if res:
            await ctx.respond(res)

    @giveaway.command(name="list", aliases=["glist"])
    async def giveaway_list(self, ctx: discord.ApplicationContext) -> None:
        """View all giveaways from the last 10 days!"""
        await ctx.respond(embed=await General().giveawaylist())


def setup(bot):
    bot.add_cog(Giveaways(bot))
