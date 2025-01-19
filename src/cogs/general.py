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
    @option(
        name="setting",
        description="Do you want the bot to ping you in daily and weekly gexp leaderboards?",
        choices=[discord.OptionChoice("Yes", value=1), discord.OptionChoice("No", value=0)],
        required=True
    )
    async def do_pings(self, ctx, setting: int):
        """Used to enable/disable pings in automatic daily and weekly leaderboard messages!"""
        await ctx.respond(embed=await Union(ctx.author).do_pings(setting=setting))
        
    
    
    @commands.slash_command()
    @commands.has_any_role("QOTD Manager", "Staff")
    async def qotd(self, ctx):
        """Used by QOTD Managers to register a QOTD"""

        class ModalCreator(discord.ui.Modal):
            def __init__(self) -> None:
                #   fields = ["LABEL", "PLACEHOLDER", STYLE]
                super().__init__(title="QOTD Creator")
                self.add_item(discord.ui.InputText(label="What is the question of the day?",
                                                   placeholder="Enter the question here",
                                                   max_length=256,
                                                   style=discord.InputTextStyle.long))
                self.add_item(discord.ui.InputText(label="Who suggested this question?",
                                                   placeholder="Enter their username. If it was you, enter your username.",
                                                   max_length=256,
                                                   style=discord.InputTextStyle.short))

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message("The QOTD has been sent!")
                await String(string=self.children[0].value).qotd(ctx, self.children[1].value)

        await ctx.send_modal(modal=ModalCreator())

    @commands.slash_command()
    @option(
        name="Member",
        description="The discord user whose minecraft ign you'd like to find",
        required=True,
        input_type=discord.Member
    )
    async def whois(self, ctx, member: discord.Member):
        await ctx.respond(embed=await Union(member).whois())

def setup(bot):
    bot.add_cog(General(bot))
