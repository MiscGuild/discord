import discord
from discord.errors import Forbidden
from discord.ext import commands, bridge

from src.utils.consts import PREFIX, NEUTRAL_COLOR

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!
However, you must put "bot.remove_command('help')" in your bot, and the command must be in a cog for it to work.
Original concept by Jared Newsom (AKA Jared M.F.)
[Deleted] https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b
Rewritten and optimized by github.com/nonchris
https://gist.github.com/nonchris/1c7060a14a9d94e7929aa2ef14c41bc2
You need to set three variables to make that cog run.
Have a look at line 51 to 57
"""


async def send_embed(ctx: discord.ApplicationContext, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """

    try:
        await ctx.respond(embed=embed)
    except Forbidden:
        try:
            await ctx.respond("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """
    Shows this help embed!
    """

    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="module",
        description="The name of the module or command you'd like to view the details of",
        required=False,
        input_type=str
    )
    async def help(self, ctx: discord.ApplicationContext, module=None) -> None:
        """Shows all modules of the Miscellaneous bot"""


        async def predicate(cmd):
            # Check if the command is enabled and not hidden
            return cmd.enabled if hasattr(cmd, 'enabled') else True

        if not module:
            emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                description=f'Use `{PREFIX}help <module/command>` to gain more information about that module '
                                            f':smiley:\n')

            cogs_desc = ''
            for cog in self.bot.cogs:
                valid = False
                for command in self.bot.get_cog(cog).get_commands():
                    valid = await predicate(command)
                    if valid:
                        break
                if valid:
                    cogs_desc += f'`{cog.capitalize()}` {self.bot.cogs[cog].__doc__}\n'

            emb.add_field(name='Modules', value=cogs_desc, inline=False)

            commands_desc = ''
            for command in self.bot.walk_commands():
                if not command.cog_name:
                    commands_desc += f'{command.name} - {command.help}\n'

            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

        elif len(module.split()) == 1:
            if module not in self.bot.cogs:
                command = self.bot.get_command(module)
                if command:
                    syntax = f"{PREFIX}{command.name}"
                    for key, value in command.clean_params.items():
                        if not value.default:
                            syntax += " [" + key + "]"
                        else:
                            syntax += " <" + key + ">"
                    embed = discord.Embed(title=f"Help", color=NEUTRAL_COLOR)
                    embed.add_field(name=f"`{syntax}`", value=command.help)
                    aliases = command.aliases
                    if aliases:
                        embed.add_field(name="Aliases", value=", ".join(aliases), inline=False)
                    await ctx.respond(embed=embed)
                    return

            for cog in self.bot.cogs:
                if cog.lower() == module.lower():
                    emb = discord.Embed(title=f'{cog.capitalize()} - Commands', description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.green())

                    for command in self.bot.get_cog(cog).get_commands():
                        if await predicate(command):  # Check if the command can be run
                            syntax = f"{PREFIX}{command.name}"
                            for key, value in command.clean_params.items():
                                if not value.default:
                                    syntax += " [" + key + "]"
                                else:
                                    syntax += " <" + key + ">"
                            emb.add_field(name=f"`{syntax}`", value=command.help, inline=False)

                    emb.set_footer(
                        text="\n\n[] represent compulsory fields\n<> represent optional fields\nDo not type the brackets!")
                    break

            else:
                cogs_desc = ''
                for cog in self.bot.cogs:
                    if "Hidden" not in self.bot.cogs[cog].__doc__:
                        cogs_desc += f'`{cog.capitalize()}` {self.bot.cogs[cog].__doc__}\n'
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard of a module/command called `{module}` before :scream:",
                                    color=discord.Color.orange())
                emb.add_field(name="Here is a list of all the fields and their descriptions", value=cogs_desc)
                emb.set_footer(text="Use ,help <module/command> to gain more information about that module/command")

        elif len(module.split()) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module or one command at once :sweat_smile:",
                                color=discord.Color.orange())

        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Help(bot))
