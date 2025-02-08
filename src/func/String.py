# The following file contains: source, gmember, info, dnkladd, dnklremove, dnklcheck, rename

import inspect
import os
from __main__ import bot
from datetime import datetime

import discord
from quickchart import QuickChart

from src.utils.calculation_utils import (calculate_network_level,
                                         get_color_by_gexp,
                                         get_hypixel_player_rank,
                                         get_player_gexp)
from src.utils.consts import (dnkl_channel_id, dnkl_req, guildless_embed,
                              months, neg_color, neutral_color, pos_color,
                              qotd_ans_channel_id, qotd_channel_id,
                              ticket_categories, unknown_ign_embed, rainbow_separator, guild_handle,
                              missing_permissions_embed, member_req)
from src.utils.db_utils import (delete_dnkl, select_one,
                                get_invites)
from src.utils.referral_utils import check_invitation_validity
from src.utils.request_utils import (get_hypixel_player, get_mojang_profile,
                                     get_player_guild, get_name_by_uuid)
from src.utils.ticket_utils.dnkl import dnkl_application


class String:
    def __init__(self, string: str = None, uuid: str = None, username: str = None):
        self.string = string
        self.uuid = uuid
        self.username = username

    # Command from https://github.com/Rapptz/RoboDanny
    async def source(self) -> str:
        source_url = "https://github.com/MiscGuild/discord"
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

    async def gmember(self, ctx: discord.ApplicationContext) -> discord.Embed | str | None:
        if self.uuid and self.username:
            uuid = self.uuid
            name = self.username
        else:
            name, uuid = await get_mojang_profile(self.string)
            if not name:
                return unknown_ign_embed

        guild = await get_player_guild(uuid)

        # Player is guildless
        if not guild:
            return guildless_embed

        # Get guild data
        gname = guild["name"]
        gtag = "" if not "tag" in guild else f"[{guild['tag']}]"

        # Find player in req
        for member in guild["members"]:
            if member["uuid"] != uuid:
                continue

            # Get player data
            gexp_history = member["expHistory"]
            weekly_gexp = sum(gexp_history.values())

            # Send shortened version for non-command and non-ticket channels
            if "commands" not in ctx.channel.name and str(ctx.channel.category) not in ticket_categories.values():
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
            join_date = str(datetime.fromtimestamp(int(str(member["joined"])[:-3])))[:10]
            rank = member["rank"]
            quest_participation = member["questParticipation"] if "questParticipation" in member else 0
            dates = [k for k, _ in gexp_history.items()]
            gexp_vals = [int(v) for _, v in gexp_history.items()]
            gexp_history_text = ""
            for i in range(0, 7):
                date = week_dict.get(i, "None")
                gexp_history_text = gexp_history_text + f"**▸** {date} **{format(gexp_vals[i], ',d')}**\n"

            # Get graph color
            color, graph_color, graph_border = await get_color_by_gexp(rank, weekly_gexp)

            # Create embed
            embed = discord.Embed(title=name, url=f"https://plancke.io/hypixel/player/stats/{name}", color=color)
            embed.set_author(name=f"{gname} {gtag}", url=f"https://plancke.io/hypixel/guild/player/{name}")
            embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
            embed.add_field(name="General Information:", value=f"`✚` **Rank**: `{rank}`\n"
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
            chart.config = {"type": "line",
                            "data": {
                                "labels": dates,
                                "datasets": [
                                    {
                                        "label": "Experience",
                                        "data": gexp_vals,
                                        "lineTension": 0.4,
                                        "backgroundColor": graph_color,
                                        "borderColor": graph_border,
                                        "pointRadius": 0,
                                    }
                                ]
                            }
                            }
            return embed.set_image(url=chart.get_url())


    async def info(self) -> discord.Embed:
        if self.uuid and self.username:
            uuid = self.uuid
        else:
            name, uuid = await get_mojang_profile(self.string)
            if not name:
                return unknown_ign_embed
        player_data = await get_hypixel_player(name=uuid)
        # Player doesn't exist
        if not player_data:
            return unknown_ign_embed

        # Gather info
        ign = player_data["displayname"]
        uuid = player_data["uuid"]
        _, rank = await get_hypixel_player_rank(player_data)
        nwl = await calculate_network_level(player_data["networkExp"])
        karma = f"{int(player_data['karma']):,d}"
        achievement_points = "-" if "achievementPoints" not in player_data else f"{int(player_data['achievementPoints']):,d}"
        completed_challenges = "0" if "general_challenger" not in player_data[
            "achievements"] else f"{int(player_data['achievements']['general_challenger']):,d}"
        completed_quests = "-" if "quests" not in player_data else f"{len(player_data['quests']):,d}"
        first_login = datetime.fromtimestamp(int(str(player_data["firstLogin"])[:-3]))
        last_login = "Unknown" if "lastLogin" not in player_data else datetime.fromtimestamp(
            int(str(player_data["lastLogin"])[:-3]))
        guild = await get_player_guild(uuid)
        gtag = "" if not guild or "tag" not in guild else f"[{guild['tag']}]"

        embed = discord.Embed(title=f"{rank} {ign} {gtag}", url=f'https://plancke.io/hypixel/player/stats/{ign}',
                              color=0x8368ff)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        embed.add_field(name="Network Level:", value=f"`{nwl}`", inline=True)
        embed.add_field(name="Karma:", value=f"`{karma}`", inline=True)
        embed.add_field(name="Achievement Points:", value=f"`{achievement_points}`", inline=False)
        embed.add_field(name="Challenges Finished:", value=f"`{completed_challenges}`", inline=True)
        embed.add_field(name="Quests Completed:", value=f"`{completed_quests}`", inline=True)
        embed.add_field(name="First • Last login", value=f"`{first_login} • {last_login}`", inline=False)
        return embed.set_image(url=f"https://gen.plancke.io/exp/{ign}.png")

    async def dnkladd(self, ctx: discord.ApplicationContext) -> discord.Embed | None:
        # start, end, reason
        ign, uuid = await get_mojang_profile(self.string)
        _, weekly_gexp = await get_player_gexp(uuid)
        if not ign:
            return unknown_ign_embed
        await ctx.respond("Please respond to the following prompts: ")
        # Ask DNKL application questions
        await dnkl_application(ign, uuid, ctx.channel, ctx.author, weekly_gexp)


    async def dnklremove(self) -> str:
        if self.string:
            _, uuid = await get_mojang_profile(self.string)
        else:
            _, uuid = await get_name_by_uuid(self.uuid), self.uuid

        row = await select_one("SELECT * FROM dnkl WHERE uuid = (?)", (uuid,))

        if not row:
            return "This player is not on the do-not-kick-list!"
        else:
            message_id, _, username = row
            # Delete row
            await delete_dnkl(uuid)

            # Delete DNKL message
            try:
                msg = await bot.get_channel(dnkl_channel_id).fetch_message(message_id)
                await msg.delete()
            except discord.errors.NotFound:
                return f"{username} has been removed from the do-not-kick-list, however the message was not found."

            return f"{username} has been removed from the do-not-kick-list!"


    async def dnklcheck(self) -> discord.Embed:
        if self.uuid and self.username:
            uuid = self.uuid
            name = self.username
        else:
            name, uuid = await get_mojang_profile(self.string)
            if not name:
                return unknown_ign_embed
        _, weeklygexp = await get_player_gexp(uuid)

        # Player is not in a guild
        if not weeklygexp:
            return guildless_embed

        # Player is eligible
        if weeklygexp > dnkl_req:
            embed = discord.Embed(title=name, color=pos_color)
            embed.add_field(name="This player is eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{dnkl_req} weekly guild experience.", inline=True)

        # Player is not eligible
        else:
            embed = discord.Embed(title=name, color=neg_color)
            embed.add_field(name="This player is not eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{dnkl_req} weekly guild experience to be eligible.",
                            inline=True)

        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
        embed.set_author(name="Do-not-kick-list: Eligibility Check")
        return embed

    async def rename(self, ctx: discord.ApplicationContext) -> int | discord.Embed | discord.Message:
        # Channel is not a ticket
        if ctx.channel.category.name not in ticket_categories.values():
            return await ctx.send("This command can only be used in tickets!")

        old_name = ctx.channel.name
        # Channel is a ticket
        channel_name = self.string.replace(" ", "-")
        await ctx.channel.edit(name=channel_name)
        return discord.Embed(title=f"The channel name was changed from {old_name} to {channel_name}",
                             color=neutral_color)

    async def qotd(self, ctx: discord.ApplicationContext, suggester: str) -> None:
        # 15th May 2022 was the 473rd QOTD day. It is used as a reference point to calculate the day number.
        day_number = 473 + (datetime.utcnow() - datetime.strptime("2022/05/15", "%Y/%m/%d")).days
        embed = discord.Embed(
            title=f"**{self.string}\n**",
            description=f"Respond in: <#{qotd_ans_channel_id}>\n"
                        f"-# Requested by {suggester}\n"
                        f"-# Posted by {ctx.author.nick if ctx.author.nick else ctx.author.name}", color=neutral_color)
        embed.set_author(
            name=f"Day {day_number}: {datetime.utcnow().day} {months[datetime.utcnow().month]} {datetime.utcnow().year}")

        await bot.get_channel(qotd_channel_id).send("<@&923978802818871356>", embed=embed)
        await bot.get_channel(qotd_ans_channel_id).send(rainbow_separator)

    async def invites(self) -> discord.Embed:
        if self.uuid and self.username:
            uuid = self.uuid
            name = self.username
        else:
            name, uuid = await get_mojang_profile(self.string)
            if not name:
                return unknown_ign_embed

        guild = await get_player_guild(uuid)
        if ("name" not in guild) or (guild["name"] != guild_handle):
            return missing_permissions_embed

        invites = await get_invites(uuid)
        invites_text = ""
        if not invites:
            weekly_invites, total_invites, total_valid_invites = None, 0, "0"
            valid_invites = []
        else:
            weekly_invites, total_invites, total_valid_invites = invites
            weekly_invites = weekly_invites.split()
            valid_invites = await check_invitation_validity(weekly_invites)
            weekly_invites_dict = {}
            for invitee in weekly_invites:
                weekly_invites_dict[invitee] = await get_name_by_uuid(invitee)

            valid_invites = [weekly_invites_dict[invitee] for invitee in valid_invites]

            for invitee in weekly_invites_dict.values():
                if invitee in valid_invites:
                    invites_text += f"🟢 {invitee}\n"
                else:
                    invites_text += f"🔴 {invitee}\n"
        embed = discord.Embed(title=f"{name}'s Invites", color=neutral_color)
        embed.add_field(name="Weekly Invites", value=None if not invites_text else invites_text, inline=False)
        embed.add_field(name="This week's statistics", value=f"Total Valid Invites: {len(valid_invites)}\n"
                                                             f"Total Invites: {len(weekly_invites)}\n"
                                                             f"Success Rate: {round(len(valid_invites) * 100 / len(weekly_invites)) if len(weekly_invites) else 0}%",
                        inline=False)
        embed.add_field(name="Total Valid Invites", value=total_valid_invites, inline=True)
        embed.add_field(name="Total Invites", value=str(total_invites), inline=True)
        embed.add_field(name="Total Success Rate",
                        value=f"{round(total_valid_invites * 100 / total_invites if total_invites else 0)}%",
                        inline=True)
        embed.set_footer(text="Total invites and total valid invites do not include this week's invites. They are "
                              "updated at the end of the week."
                              "\nAn invite is considered valid if they earn "
                              f"{format(2 * member_req, ',d')} guild experience at the end of the week. "
                              "If they joined in the middle of the week, their guild experience will be scaled up.")
        return embed
