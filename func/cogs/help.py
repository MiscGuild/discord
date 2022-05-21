import discord
from discord.ext import commands
from discord.errors import Forbidden
from func.utils.consts import config, neutral_color

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!
However, you must put "bot.remove_command('help')" in your bot, and the command must be in a cog for it to work.
Original concept by Jared Newsom (AKA Jared M.F.)
[Deleted] https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b
Rewritten and optimized by github.com/nonchris
https://gist.github.com/nonchris/1c7060a14a9d94e7929aa2ef14c41bc2
You need to set three variables to make that cog run.
Have a look at line 51 to 57
"""


async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):
        """Shows all modules of the Miscellaneous bot"""

        # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        prefix = config['prefix']
        version = 1.0

        async def predicate(cmd):
            try:
                return await cmd.can_run(ctx)
            except commands.CommandError:
                return False
        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:

            # starting to build embed
            emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                description=f'Use `{prefix}help <module/command>` to gain more information about that module '
                                            f':smiley:\n')

            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.bot.cogs:
                valid = False
                for command in self.bot.get_cog(cog).get_commands():
                    if not command.hidden:
                        valid = await predicate(command)
                    if valid:
                        break
                if valid:
                    cogs_desc += f'`{cog.capitalize()}` {self.bot.cogs[cog].__doc__}\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Modules', value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)


        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:
            if input[0] not in self.bot.cogs:
                command = self.bot.get_command(input[0])
                syntax = f"{prefix}{command.name}"
                for key, value in command.clean_params.items():
                    if not value.default:
                        syntax += " [" + key + "]"
                    else:
                        syntax += " <" + key + ">"
                embed = discord.Embed(title=f"Help", color=neutral_color)
                embed.add_field(name=f"`{syntax}`", value=command.help)
                aliases = command.aliases
                if aliases:
                    embed.add_field(name="Aliases", value=", ".join(aliases), inline=False)
                await ctx.send(embed=embed)
                return

            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog.capitalize()} - Commands', description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.green())

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            for key, value in command.clean_params.items():
                                syntax = f"{prefix}{command.name}"
                                if not value.default:
                                    syntax += " [" + key + "]"
                                else:
                                    syntax += " <" + key + ">"
                            emb.add_field(name=f"`{syntax}`", value=command.help, inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                cogs_desc = ''
                for cog in self.bot.cogs:
                    if "Hidden" not in self.bot.cogs[cog].__doc__:
                        cogs_desc += f'`{cog.capitalize()}` {self.bot.cogs[cog].__doc__}\n'
                emb = discord.Embed(title="What's that?!",
                                    description=f"I've never heard of a module/command called `{input[0]}` before :scream:",
                                    color=discord.Color.orange())
                emb.add_field(name="Here is a list of all the fields and their descriptions", value=cogs_desc)
                emb.set_footer(text="Use ,help <module/command> to gain more information about that module/command")

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module or one command at once :sweat_smile:",
                                color=discord.Color.orange())

        # sending reply embed using our own function defined above
        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Help(bot))
