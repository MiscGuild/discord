# The following file contains: source, gmember, sync, info, dnkladd, dnklremove, dnkllist, dnklcheck, register, rename

import discord
import inspect
import os
from __main__ import bot
from datetime import datetime
from discord.errors import Forbidden
from quickchart import QuickChart

from func.utils.consts import pos_color, neg_color, neutral_color, guildless_embed, unknown_ign_embed, staff_impersonation_embed, bot_missing_perms_embed
from func.utils.discord_utils import has_tag_perms, check_tag
from func.utils.minecraft_utils import get_player_gexp, get_graph_color_by_rank
from func.utils.request_utils import get_mojang_profile, get_player_guild, get_gtag


class String:
    def __init__(self, string: str):
        self.string = string

    # Command from https://github.com/Rapptz/RoboDanny
    async def source(self):
        source_url = "https://github.com/MiscGuild/MiscBot"
        branch = "main"

        if not self.string:
            return source_url

        if self.string == "help":
            src = type(bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = bot.get_command(self.string.replace(",", " "))
            if not obj:
                return "Command not found."

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            # not a built-in command
            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = "https://github.com/MiscGuild/MiscBot"
            branch = "main"

        final_url = f"<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        return f"Following is the source code for {self.string}\n{final_url}"

    async def gmember(self, ctx):
        name, uuid = await get_mojang_profile(self.string)
        guild = await get_player_guild(uuid)

        # Player is guildless
        if not guild:
            return guildless_embed

        # Get guild data
        gname = guild["guild"]["name"]
        gtag = gname if not guild["guild"]["tag"] else guild["guild"]["tag"]

        # Find player in req
        for member in guild["guild"]["members"]:
            if member["uuid"] == uuid:
                # Get player data
                gexp_history = member["expHistory"]
                weekly_gexp = sum(gexp_history.values())

                # Send shortened version for non-command channels
                if "commands" not in ctx.channel.name:
                    await ctx.message.delete()
                    return f"__**{name}**__\n**Guild Experience -** `{format(weekly_gexp, ',d')}`"

                week_dict = {
                    0: "Today:",
                    1: "Yesterday:",
                    2: "Two days ago:",
                    3: "Three days ago:",
                    4: "Four days ago:",
                    5: "Five days ago:",
                    6: "Six days ago:"
                }

                # Fetch remaining data
                join_date = str(datetime.fromtimestamp(int(str(member["joined"])[:-3])))[0:10]
                rank = member["rank"]
                quest_participation = member["questParticipation"] if "questParticipation" in member else 0
                dates = [k for k, _ in gexp_history.items()]
                gexp_vals = [int(v) for _, v in gexp_history.items()]
                gexp_history_text = ""
                for i in range(0, 7):
                    date = week_dict.get(i, "None")
                    gexp_history_text = gexp_history_text + f"**▸** {date} **{format(gexp_vals[i], ',d')}**\n"

                # Get graph color
                color, graph_color, graph_border = await get_graph_color_by_rank(rank, weekly_gexp)

                # Create embed
                embed = discord.Embed(title=name, url=f"https://plancke.io/hypixel/player/stats/{name}", color=color)
                embed.set_author(name=f"{gname} [{gtag}]", url=f"https://plancke.io/hypixel/guild/player/{name}")
                embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
                embed.add_field(name="General Information:",
                                value=f"`✚` **Rank**: `{rank}`\n"
                                      f"`✚` **Joined**: `{join_date}`\n"
                                      f"`✚` **Quests Completed**: `{quest_participation}`\n"
                                      f"`✚` **Overall Guild Experience**: `{format(weekly_gexp, ',d')}`\n\n{gexp_history_text}",
                                inline=False)

                # Create chart
                dates.reverse()
                gexp_vals.reverse()
                chart = QuickChart()
                chart.width = 1000
                chart.height = 500
                chart.background_color = "transparent"
                chart.config = {
                    "type": "line",
                    "data": {
                        "labels": dates,
                        "datasets": [{
                            "label": "Experience",
                            "data": gexp_vals,
                            "lineTension": 0.4,
                            "backgroundColor": graph_color,
                            "borderColor": graph_border,
                            "pointRadius": 0,
                        }]
                    }
                }
                return embed.set_image(url=chart.get_url())

    async def sync(self, ctx, tag=None, is_fs=False):
        ign, uuid = await get_mojang_profile(self.string)

        # Invalid username
        if not ign:
            return unknown_ign_embed
        # User trying to sync with staff name
        elif ign in bot.staff_names and bot.staff not in ctx.author.roles:
            return staff_impersonation_embed

        # Initialize vars for storing changes
        roles_to_add = []
        roles_to_remove = []
        new_nick = ign

        guild_name = await get_player_guild(uuid)
        guild_name = "no guild" if not guild_name else guild_name["guild"]["name"]
        can_tag = await has_tag_perms(ctx.author)

        # Check tag before other logic
        if tag and can_tag:
            tag_check_success, tag_check_reason = await check_tag(tag)
            if tag_check_success:
                new_nick += f"[{tag}]"
            else:
                return tag_check_reason

        # Users is in Misc
        if guild_name == "Miscellaneous":
            roles_to_add.append(bot.member_role)
            roles_to_remove.extend([bot.guest, bot.awaiting_app])

        # User is an ally
        elif guild_name in bot.misc_allies:
            gtag = await get_gtag(guild_name)

            # Account for if user has nick perms
            new_nick = ign + " " + gtag
            roles_to_remove.extend([self.bot.new_member_role, self.bot.awaiting_app, self.bot.member_role])
            roles_to_add.extend([self.bot.guest, self.bot.ally])

        # User is a guest
        else:
            # Filter people who have not been approved to join the discord
            if str(ctx.channel.category.name) == "RTickets" and not is_fs:
                return "You cannot use this command in a registration ticket!\nKindly await staff assistance!"

            roles_to_add.append(bot.guest)
            roles_to_remove.extend([bot.member_role, bot.awaiting_app])

        # Create embed
        footer = f"• Member of {guild_name}"
        for role in roles_to_remove:
            footer += f"\n• Removed {role.name}"
        for role in roles_to_add:
            footer += f"\n• Added {role.name}"

        embed = discord.Embed(title="Your nick, roles, and tag have been successfully changed!",
                              description="If this wasn't the change you anticipated, please create a ticket!",
                              color=neutral_color)
        embed.set_footer(text=footer)

        # Set roles and nick
        await ctx.author.add_roles(*roles_to_add, reason="Sync")
        await ctx.author.remove_roles(*roles_to_remove, reason="Sync")
        try:
            await ctx.author.edit(nick=new_nick)
        except Forbidden:
            return bot_missing_perms_embed

        return embed

    # async def info():

    # async def dnkladd(start: str, end: str, *, reason: str):

    # async def dnklremove():

    # async def dnkllist():

    async def dnklcheck(self):
        _, weeklygexp = await get_player_gexp(self.string)

        # Player is not in a guild
        if not weeklygexp:
            return guildless_embed

        self.string, uuid = await get_mojang_profile(self.string)
        # Player is eligible
        if weeklygexp > bot.dnkl:
            embed = discord.Embed(title=self.string, color=pos_color)
            embed.add_field(name="This player is eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{bot.dnkl} weekly guild experience.",
                            inline=True)


        # Player is not eligible
        else:
            embed = discord.Embed(title=self.string, color=neg_color)
            embed.add_field(name="This player is not eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{bot.dnkl} weekly guild experience to be eligible.",
                            inline=True)

        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
        embed.set_author(name="Do-not-kick-list: Eligibility Check")
        return embed

    # async def register(self):

    async def rename(self, ctx):
        await ctx.message.delete()
        # Channel is not a ticket
        if ctx.channel.category.name not in bot.ticket_categories:
            return await ctx.send("This command can only be used in tickets!")
        
        # Channel is a ticket
        channel_name = self.string.replace(" ", "-")
        await ctx.channel.edit(name=channel_name)
