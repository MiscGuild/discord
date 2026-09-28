import inspect

import discord
from discord.errors import Forbidden
from discord.ext import commands, bridge

from src.utils.consts import PREFIX, NEUTRAL_COLOR

# Discord's own embed limits. The description is the roomiest Markdown
# area an embed has, so help leans on it rather than on fields.
DESCRIPTION_LIMIT = 4096

# The client also stops rendering a description somewhere around fifty
# lines, regardless of how few characters are left, so packing has to
# respect height as well as width.
LINE_LIMIT = 40

ARGUMENT_LEGEND = (
    "[] represent compulsory fields\n"
    "<> represent optional fields\n"
    "Do not type the brackets!"
)


async def send_embed(ctx: discord.ApplicationContext, embed):
    """
    Sends an embed, falling back to progressively more private delivery.

    The bot can be allowed to talk but not to embed, or allowed to talk
    nowhere in the channel at all, so each fallback is a step more
    private than the last.
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


async def send_embeds(ctx: discord.ApplicationContext, embeds):
    """
    Sends every embed in turn, reusing the single-embed fallback chain.

    A module listing can outgrow one description, so these go out one at
    a time instead of as a single multi-embed message.
    """
    for embed in embeds:
        await send_embed(ctx, embed)


class Help(commands.Cog):
    """Browse the bot's commands, or read up on a single one."""

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def get_cog_commands(cog):
        """
        Collects every command in a cog that help should display.

        Pycord bridge cogs register both a prefix and a slash variant of
        the same command, sharing a qualified name. We keep the prefix
        variant, because it carries clean_params, help and aliases, and
        discard the slash twin.

        Cog.get_commands() only returns top-level commands, so group
        subcommands are flattened in here as well.
        """
        collected = []
        seen = set()

        for command in cog.get_commands():
            if not isinstance(command, (commands.Command, discord.SlashCommand)):
                continue

            if command.qualified_name in seen:
                continue

            seen.add(command.qualified_name)
            collected.append(command)

            if isinstance(command, commands.GroupMixin):
                for subcommand in command.walk_commands():
                    if not isinstance(subcommand, commands.Command):
                        continue

                    seen.add(subcommand.qualified_name)
                    collected.append(subcommand)

        return collected

    @staticmethod
    def get_parameters(command):
        """
        Yields a (name, required) pair for each user-facing parameter.

        Prefix commands expose clean_params, while slash-only commands
        expose their declared options instead.
        """
        if isinstance(command, commands.Command):
            for name, param in command.clean_params.items():
                yield name, param.default is inspect.Parameter.empty
        else:
            for option in command.options:
                yield option.name, option.required

    @staticmethod
    def get_description(command):
        """
        Returns a command's full help text.

        Prefix commands carry it on .help, but slash-only commands do
        not, so their callback docstring is read directly.
        """
        if isinstance(command, commands.Command):
            return command.help

        return inspect.getdoc(command.callback)

    @staticmethod
    def get_syntax(command):
        """
        Builds command syntax, including any group prefix.

        [] = required
        <> = optional
        """
        syntax = f"{PREFIX}{command.qualified_name}"

        for name, required in Help.get_parameters(command):
            syntax += f" [{name}]" if required else f" <{name}>"

        return syntax

    @staticmethod
    def command_is_visible(command):
        """Check whether a command should appear in help."""
        return (
                getattr(command, "enabled", True)
                and not getattr(command, "hidden", False)
        )

    @staticmethod
    def get_aliases(command):
        """
        Returns a command's aliases.

        Slash-only commands do not support aliases, so this may be empty.
        """
        return getattr(command, "aliases", [])

    @staticmethod
    def find_command(bot, name):
        """
        Looks up a single command by name, subcommands included.

        Bot.get_command() only finds top-level prefix commands, so the
        cogs are searched by qualified name as well. That second pass is
        what lets ",help g member" and ",help register" resolve at all.
        """
        parts = name.lower().split()
        command = bot.get_command(parts[0])

        for depth in range(len(parts) - 1):
            if not isinstance(command, commands.GroupMixin):
                return None

            command = command.get_command(parts[depth + 1])

        if command is not None:
            return command

        target = name.lower()

        for cog in bot.cogs.values():
            for candidate in Help.get_cog_commands(cog):
                if candidate.qualified_name.lower() == target:
                    return candidate

        return None

    @staticmethod
    def split_summary(text):
        """
        Splits a command's help text into a summary and further details.

        The first line is the summary. Everything after the blank line
        that follows it is the detail, which help renders dimmer and
        smaller. The detail is unwrapped back onto a single line, so a
        command costs a predictable number of lines however its docstring
        happened to be wrapped in the source.
        """
        text = (text or "").strip()

        if not text:
            return "No description available.", ""

        lines = text.splitlines()
        summary = lines[0].strip()
        details = " ".join(line.strip() for line in lines[1:]).strip()

        return summary, details

    @staticmethod
    def get_command_body(command):
        """
        Renders a command's help text, with detail marked as subtext.

        Discord's -# makes a line smaller and grey, which is the
        clearest way to push the supporting detail below the summary
        without relying on bold. The syntax itself is not included here;
        callers place that in the title or as a heading.
        """
        summary, details = Help.split_summary(Help.get_description(command))

        body = summary

        if details:
            body += f"\n-# {details}"

        aliases = Help.get_aliases(command)

        if aliases:
            body += f"\n-# Aliases: {', '.join(aliases)}"

        return body

    @staticmethod
    def get_command_section(command):
        """
        Renders one command as a Markdown block for a module listing.

        A heading is used for the syntax rather than bold text, because
        Discord only renders headings in an embed's description and
        title. The block is kept as a self-contained string so the caller
        can pack whole blocks, rather than text that has already been
        glued together and can no longer be split cleanly.
        """
        return f"### {Help.get_syntax(command)}\n{Help.get_command_body(command)}"

    @staticmethod
    def pack_sections(title: str, sections, color) -> list:
        """
        Packs Markdown sections into as few embeds as Discord will render.

        Two limits apply, not one. A description holds at most 4096
        characters, and the client separately gives up after roughly
        fifty lines, so packing against characters alone silently
        truncates the tail of a long cog listing. Whole sections are
        kept together either way, so no command is ever split in half.
        """
        embeds = []
        current = ""
        continued = False

        for section in sections:
            if len(section) > DESCRIPTION_LIMIT:
                section = f"{section[:DESCRIPTION_LIMIT - 1]}…"

            candidate = f"{current}\n\n{section}" if current else section

            if current and (
                    len(candidate) > DESCRIPTION_LIMIT
                    or candidate.count("\n") + 1 > LINE_LIMIT
            ):
                embeds.append(
                    discord.Embed(
                        title=f"{title} (cont.)" if continued else title,
                        description=current,
                        color=color
                    )
                )
                continued = True
                current = section
            else:
                current = candidate

        if current:
            embeds.append(
                discord.Embed(
                    title=f"{title} (cont.)" if continued else title,
                    description=current,
                    color=color
                )
            )

        return embeds

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
        """Browse every command, or drill into a single one.

        Run with nothing to list every module and its summary.
        Pass a module (e.g. `moderation`) to see all of its commands, or
        a command (e.g. `ban`, `g member`) for its syntax and aliases.
        """

        if not module:
            lines = [
                f"Use `{PREFIX}help <module/command>` to gain more "
                f"information about that module :smiley:"
            ]

            cogs_desc = ""

            for cog_name, cog in self.bot.cogs.items():
                cog_commands = self.get_cog_commands(cog)

                # Only display the cog if it has at least one
                # visible command.
                if any(
                        self.command_is_visible(command)
                        for command in cog_commands
                ):
                    description = (cog.__doc__ or "").strip()
                    cogs_desc += (
                        f"### {cog_name.capitalize()}\n{description}\n\n"
                    )

            if cogs_desc:
                lines += ["", cogs_desc.rstrip()]

            commands_desc = ""

            for command in self.bot.walk_commands():
                if (
                        not command.cog_name
                        and self.command_is_visible(command)
                ):
                    summary, _ = self.split_summary(
                        self.get_description(command)
                    )
                    commands_desc += f"### {command.name}\n{summary}\n\n"

            if commands_desc:
                lines += [
                    "",
                    "-# Not belonging to a module",
                    "",
                    commands_desc.rstrip()
                ]

            emb = discord.Embed(
                title="Commands and modules",
                description="\n".join(lines),
                color=discord.Color.blue()
            )

            await send_embed(ctx, emb)
            return

        command = self.find_command(self.bot, module)

        if command and self.command_is_visible(command):
            emb = discord.Embed(
                title=f"`{self.get_syntax(command)}`",
                description=self.get_command_body(command),
                color=NEUTRAL_COLOR
            )

            emb.set_footer(text=ARGUMENT_LEGEND)

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
            # IMPORTANT:
            # Only list the prefix variants where they exist.
            #
            # get_cog_commands() discards the slash twin of every bridge
            # command, because BridgeSlashGroup exposes neither
            # clean_params nor help.
            sections = [
                self.get_command_section(command)
                for command in self.get_cog_commands(matched_cog)
                if self.command_is_visible(command)
            ]

            embeds = self.pack_sections(
                title=f"{matched_cog_name.capitalize()} — Commands",
                sections=sections,
                color=discord.Color.green()
            )

            for embed in embeds:
                embed.set_footer(text=ARGUMENT_LEGEND)

            await send_embeds(ctx, embeds)
            return

        cogs_desc = ""

        for cog_name, cog in self.bot.cogs.items():
            description = cog.__doc__ or ""

            if "Hidden" not in description:
                cogs_desc += (
                    f"### {cog_name.capitalize()}\n{description.strip()}\n\n"
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
            emb.description += f"\n\n{cogs_desc.rstrip()}"

        emb.set_footer(
            text=(
                f"Use {PREFIX}help <module/command> to gain more "
                f"information about that module/command"
            )
        )

        await send_embed(ctx, emb)


def setup(bot):
    bot.add_cog(Help(bot))
