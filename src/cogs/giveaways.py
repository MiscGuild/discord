import discord
from discord.ext import commands, bridge

from src.func.General import General
from src.func.Integer import Integer


class Giveaways(commands.Cog, name="giveaways"):
    """
    Create, end, re-roll and list server giveaways.
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_group(name="giveaway", description="Create, end, re-roll and list giveaways",
                         invoke_without_command=True)
    async def giveaway(self, ctx: bridge.BridgeContext):
        """
        Manage server giveaways.

        Running it on its own just points you at the subcommands.
        """
        if ctx.invoked_subcommand is None:  # Ensures this runs only if no subcommand is called
            await ctx.respond("Use `/giveaway create`, `/giveaway end `, or `/giveaway reroll` or `/giveaway end`.")

    @giveaway.command(name="create", aliases=["c"])
    @commands.has_role("Giveaway Creator")
    async def giveaway_create(self, ctx: discord.ApplicationContext) -> None:
        """Creates a giveaway through an interactive prompt.

        Asks for the channel, prize, winner count, duration, guild
        experience requirement, role requirements and sponsors. Type
        `cancel` at any prompt to back out. Requirements are only
        enforced when the winners are drawn.
        """
        await ctx.respond(
            "Please provide the required information to create the giveaway by responding to the following prompts!")
        await General().giveawaycreate(ctx)

    @giveaway.command(name="end", aliases=["e", "f", "finish"])
    @commands.has_role("Giveaway Creator")
    @bridge.bridge_option(
        name="message_id",
        description="The message ID of the giveaway you would like to end",
        required=True,
        input_type=int
    )
    async def giveaway_end(self, ctx: discord.ApplicationContext, message_id: int) -> None:
        """Ends a giveaway and picks the winners.

        Winners are drawn from the 🎉 reactions, skipping anyone who no
        longer meets the role or guild experience requirements. The
        result is announced in the giveaway's own channel, not here.
        """
        res = await Integer(integer=message_id).giveawayend()
        if res:
            await ctx.respond(res)

    @giveaway.command(name="reroll", aliases=["r"])
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
        """Re-rolls a giveaway that has already ended.

        Draws fresh winners from the same 🎉 reactions. Pass a number to
        change how many are picked. Running this on a giveaway that is
        still live is refused.
        """
        res = await Integer(integer=message_id).giveawayreroll(reroll_number)
        if res:
            await ctx.respond(res)

    @giveaway.command(name="list", aliases=["l"])
    async def giveaway_list(self, ctx: discord.ApplicationContext) -> None:
        """Lists active giveaways and any that ended recently.

        Giveaways stay listed until about 10 days after they end.
        """
        await ctx.respond(embed=await General().giveawaylist())


def setup(bot):
    bot.add_cog(Giveaways(bot))
