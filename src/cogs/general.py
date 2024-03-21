import discord
from discord.commands import option
from discord.ext import commands, bridge

from src.func.String import String
from src.func.Union import Union


class General(commands.Cog, name="general"):
    """
    Contains source, avatar, qotd.
    """

    def __init__(self, bot):
        self.bot = bot

    # Command from https://github.com/Rapptz/RoboDanny
    @bridge.bridge_command(name="source", aliases=['src'])
    @option(
        name="command",
        description="The command you would like to see the source code for",
        required=False,
        input_type=str
    )
    async def source(self, ctx, *, command: str = None):
        """View the source code for the bot or a specific command"""
        await ctx.respond(await String(string=command).source())

    @bridge.bridge_command()
    @option(
        name="user",
        description="User whose avatar you'd like to view",
        required=False,
        input_type=discord.Member
    )
    async def avatar(self, ctx, user: discord.Member = None):
        """See the avatar of a given user!"""
        await ctx.respond(embed=await Union(user=user or ctx.author).avatar())

    @commands.slash_command()
    @commands.has_any_role("QOTD Manager", "Staff")
    async def qotd(self, ctx):
        """Used by QOTD Managers to register a QOTD"""

        class ModalCreator(discord.ui.Modal):
            def __init__(self) -> None:
                #   fields = ["LABEL", "PLACEHOLDER", STYLE]
                super().__init__(title="QOTD Creator")
                self.add_item(discord.ui.InputText(label="What is the question of the day?", placeholder="Enter the question here", style=discord.InputTextStyle.long))


            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message("The QOTD has been sent!")
                await String(string=self.children[0].value).qotd(ctx)

        await ctx.send_modal(modal=ModalCreator())


def setup(bot):
    bot.add_cog(General(bot))
