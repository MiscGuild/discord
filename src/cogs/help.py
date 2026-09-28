import inspect

import discord
from discord.errors import Forbidden
from discord.ext import commands, bridge

from src.utils.consts import PREFIX, NEUTRAL_COLOR


async def send_embed(ctx: discord.ApplicationContext, embed):
    """
    Handles sending help embeds.
    """
    try:
        await ctx.respond(embed=embed)
    except Forbidden:
        try:
            await ctx.respond(
                "Hey, seems like I can't send embeds. "
                "Please check my permissions :)"
            )
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in "
                f"{ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? "
                f":slight_smile:",
                embed=embed
            )


class Help(commands.Cog):
    """Shows this help embed!"""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_prefix_commands(cog):
        """
        Pycord bridge cogs can contain both the prefix and slash variants
        of a command.

        We only want the prefix Command objects here because they have
        clean_params, help, aliases, etc.
        """
        return [
            command
            for command in cog.get_commands()
            if isinstance(command, commands.Command)
        ]

    @staticmethod
    def get_syntax(command):
        """
        Builds command syntax.

        [] = required
        <> = optional
        """
        syntax = f"{PREFIX}{command.name}"

        for name, param in command.clean_params.items():
            if param.default is inspect.Parameter.empty:
                # No default -> required argument
                syntax += f" [{name}]"
            else:
                # Has default -> optional argument
                syntax += f" <{name}>"

        return syntax

    @staticmethod
    def command_is_visible(command):
        """Check whether a command should appear in help."""
        return (
                getattr(command, "enabled", True)
                and not getattr(command, "hidden", False)
        )

    @bridge.bridge_command()
    @bridge.bridge_option(
        name="module",
        description=(
                "The name of the module or command you'd like "
                "to view the details of"
        ),
        required=False,
        input_type=str
    )
    async def help(
            self,
            ctx: discord.ApplicationContext,
            module=None
    ) -> None:
        """Shows all modules of the Miscellaneous bot."""

        if not module:
            emb = discord.Embed(
                title="Commands and modules",
                color=discord.Color.blue(),
                description=(
                    f"Use `{PREFIX}help <module/command>` to gain more "
                    f"information about that module :smiley:\n"
                )
            )

            cogs_desc = ""

            for cog_name, cog in self.bot.cogs.items():
                prefix_commands = self.get_prefix_commands(cog)

                # Only display the cog if it has at least one
                # visible prefix/bridge command.
                if any(
                        self.command_is_visible(command)
                        for command in prefix_commands
                ):
                    description = cog.__doc__ or ""
                    cogs_desc += (
                        f"`{cog_name.capitalize()}` {description}\n"
                    )

            if cogs_desc:
                emb.add_field(
                    name="Modules",
                    value=cogs_desc,
                    inline=False
                )

            commands_desc = ""

            for command in self.bot.walk_commands():
                if (
                        not command.cog_name
                        and self.command_is_visible(command)
                ):
                    commands_desc += (
                        f"{command.name} - "
                        f"{command.help or 'No description available.'}\n"
                    )

            if commands_desc:
                emb.add_field(
                    name="Not belonging to a module",
                    value=commands_desc,
                    inline=False
                )

            await send_embed(ctx, emb)
            return

        if len(module.split()) > 1:
            emb = discord.Embed(
                title="That's too much.",
                description=(
                    "Please request only one module or one command "
                    "at once :sweat_smile:"
                ),
                color=discord.Color.orange()
            )

            await send_embed(ctx, emb)
            return

        command = self.bot.get_command(module)

        if command and self.command_is_visible(command):
            syntax = self.get_syntax(command)

            emb = discord.Embed(
                title="Help",
                color=NEUTRAL_COLOR
            )

            emb.add_field(
                name=f"`{syntax}`",
                value=command.help or "No description available.",
                inline=False
            )

            if command.aliases:
                emb.add_field(
                    name="Aliases",
                    value=", ".join(command.aliases),
                    inline=False
                )

            emb.set_footer(
                text=(
                    "[] represent compulsory fields\n"
                    "<> represent optional fields\n"
                    "Do not type the brackets!"
                )
            )

            await send_embed(ctx, emb)
            return

        matched_cog = None
        matched_cog_name = None

        # Case-insensitive cog lookup
        for cog_name, cog in self.bot.cogs.items():
            if cog_name.lower() == module.lower():
                matched_cog = cog
                matched_cog_name = cog_name
                break

        if matched_cog:
            emb = discord.Embed(
                title=f"{matched_cog_name.capitalize()} - Commands",
                description=matched_cog.__doc__ or "",
                color=discord.Color.green()
            )

            # IMPORTANT:
            # Only retrieve the prefix variants.
            #
            # This prevents BridgeSlashGroup from reaching
            # command.clean_params.
            prefix_commands = self.get_prefix_commands(matched_cog)

            for command in prefix_commands:
                if not self.command_is_visible(command):
                    continue

                syntax = self.get_syntax(command)

                emb.add_field(
                    name=f"`{syntax}`",
                    value=command.help or "No description available.",
                    inline=False
                )

            emb.set_footer(
                text=(
                    "[] represent compulsory fields\n"
                    "<> represent optional fields\n"
                    "Do not type the brackets!"
                )
            )

            await send_embed(ctx, emb)
            return

        cogs_desc = ""

        for cog_name, cog in self.bot.cogs.items():
            description = cog.__doc__ or ""

            if "Hidden" not in description:
                cogs_desc += (
                    f"`{cog_name.capitalize()}` {description}\n"
                )

        emb = discord.Embed(
            title="What's that?!",
            description=(
                f"I've never heard of a module/command called "
                f"`{module}` before :scream:"
            ),
            color=discord.Color.orange()
        )

        if cogs_desc:
            emb.add_field(
                name="Here is a list of all the fields and their descriptions",
                value=cogs_desc,
                inline=False
            )

        emb.set_footer(
            text=(
                f"Use {PREFIX}help <module/command> to gain more "
                f"information about that module/command"
            )
        )

        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Help(bot))
