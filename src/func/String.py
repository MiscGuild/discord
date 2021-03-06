# The following file contains: source, gmember, info, dnkladd, dnklremove, dnklcheck, rename

import inspect
import os
from datetime import datetime

import discord
from __main__ import bot
from quickchart import QuickChart
from src.utils.consts import (dnkl_channel_id, dnkl_req, guildless_embed,
                              months, neg_color, neutral_color, pos_color,
                              qotd_ans_channel_id, qotd_channel_id,
                              ticket_categories, unknown_ign_embed)
from src.utils.db_utils import (delete_dnkl, insert_new_dnkl, select_one,
                                update_dnkl)
from src.utils.discord_utils import dnkl_application
from src.utils.minecraft_utils import (calculate_network_level,
                                       get_color_by_gexp,
                                       get_hypixel_player_rank,
                                       get_player_gexp)
from src.utils.request_utils import (get_hypixel_player, get_mojang_profile,
                                     get_player_guild)


class String:
    def __init__(self, string: str):
        self.string = string

    # Command from https://github.com/Rapptz/RoboDanny
    async def source(self):
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

    async def gmember(self, ctx):
        name, uuid = await get_mojang_profile(self.string)
        guild = await get_player_guild(uuid)

        # Player is guildless
        if not guild:
            return guildless_embed

        # Get guild data
        gname = guild["name"]
        gtag = gname if not "tag" in guild else guild["tag"]

        # Find player in req
        for member in guild["members"]:
            if member["uuid"] == uuid:
                # Get player data
                gexp_history = member["expHistory"]
                weekly_gexp = sum(gexp_history.values())

                # Send shortened version for non-command channels
                if "commands" not in ctx.channel.name:
                    return f"__**{name}**__\n**Guild Experience -** `{format(weekly_gexp, ',d')}`"

                week_dict = {0: "Today:", 1: "Yesterday:", 2: "Two days ago:", 3: "Three days ago:",
                             4: "Four days ago:", 5: "Five days ago:", 6: "Six days ago:"}

                # Fetch remaining data
                join_date = str(datetime.fromtimestamp(int(str(member["joined"])[:-3])))[:10]
                rank = member["rank"]
                quest_participation = member["questParticipation"] if "questParticipation" in member else 0
                dates = [k for k, _ in gexp_history.items()]
                gexp_vals = [int(v) for _, v in gexp_history.items()]
                gexp_history_text = ""
                for i in range(0, 7):
                    date = week_dict.get(i, "None")
                    gexp_history_text = gexp_history_text + f"**???** {date} **{format(gexp_vals[i], ',d')}**\n"

                # Get graph color
                color, graph_color, graph_border = await get_color_by_gexp(rank, weekly_gexp)

                # Create embed
                embed = discord.Embed(title=name, url=f"https://plancke.io/hypixel/player/stats/{name}", color=color)
                embed.set_author(name=f"{gname} [{gtag}]", url=f"https://plancke.io/hypixel/guild/player/{name}")
                embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
                embed.add_field(name="General Information:", value=f"`???` **Rank**: `{rank}`\n"
                                                                   f"`???` **Joined**: `{join_date}`\n"
                                                                   f"`???` **Quests Completed**: `{quest_participation}`\n"
                                                                   f"`???` **Overall Guild Experience**: `{format(weekly_gexp, ',d')}`\n\n{gexp_history_text}",
                                inline=False)

                # Create chart
                dates.reverse()
                gexp_vals.reverse()
                chart = QuickChart()
                chart.width = 1000
                chart.height = 500
                chart.background_color = "transparent"
                chart.config = {"type": "line", "data": {"labels": dates, "datasets": [
                    {"label": "Experience", "data": gexp_vals, "lineTension": 0.4, "backgroundColor": graph_color,
                     "borderColor": graph_border, "pointRadius": 0, }]}}
                return embed.set_image(url=chart.get_url())

    async def info(self):
        player_data = await get_hypixel_player(name=self.string)
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
        embed.add_field(name="First ??? Last login", value=f"`{first_login} ??? {last_login}`", inline=False)
        return embed.set_image(url=f"https://gen.plancke.io/exp/{ign}.png")

    async def dnkladd(self, ctx):
        # start, end, reason
        ign, uuid = await get_mojang_profile(self.string)
        if not ign:
            return unknown_ign_embed

        # Ask DNKL application questions
        embed = await dnkl_application(ign, uuid, ctx.channel, ctx.author)
        dnkl_message = await bot.get_channel(dnkl_channel_id).send(embed=embed.set_author(name="Do-not-kick-list"))

        # Check if user is already on DNKL
        current_message = await select_one("SELECT message_id FROM dnkl WHERE uuid = (?)", (uuid,))
        # User is not currently on DNKL
        if not current_message:
            await insert_new_dnkl(dnkl_message.id, uuid, ign)
            return "This user has been added to the do-not-kick-list!"

        # User is already on DNKl
        # Try to delete current message
        try:
            current_message = await bot.get_channel(dnkl_channel_id).fetch_message(current_message)
            await current_message.delete()
        except Exception:
            pass

        await update_dnkl(dnkl_message.id, uuid)
        return "Since this user was already on the do-not-kick-list, their entry has been updated."

    async def dnklremove(self):
        ign, uuid = await get_mojang_profile(self.string)
        row = await select_one("SELECT * FROM dnkl WHERE username = (?)", (ign,))

        if not row:
            return "This player is not on the do-not-kick-list!"
        else:
            message_id, _, username = row
            # Delete row
            await delete_dnkl(username)

            # Delete DNKL message
            try:
                msg = await bot.get_channel(dnkl_channel_id).fetch_message(message_id)
                await msg.delete()
            except Exception:
                return f"{username} has been removed from the do-not-kick-list, however the message was not found."

            return f"{username} has been removed from the do-not-kick-list!"

    async def dnklcheck(self):
        self.string, uuid = await get_mojang_profile(self.string)
        _, weeklygexp = await get_player_gexp(uuid)

        # Player is not in a guild
        if not weeklygexp:
            return guildless_embed

        # Player is eligible
        if weeklygexp > dnkl_req:
            embed = discord.Embed(title=self.string, color=pos_color)
            embed.add_field(name="This player is eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{dnkl_req} weekly guild experience.", inline=True)

        # Player is not eligible
        else:
            embed = discord.Embed(title=self.string, color=neg_color)
            embed.add_field(name="This player is not eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{dnkl_req} weekly guild experience to be eligible.",
                            inline=True)

        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
        embed.set_author(name="Do-not-kick-list: Eligibility Check")
        return embed

    async def rename(self, ctx):
        # Channel is not a ticket
        if ctx.channel.category.name not in ticket_categories.values():
            return await ctx.send("This command can only be used in tickets!")

        old_name = ctx.channel.name
        # Channel is a ticket
        channel_name = self.string.replace(" ", "-")
        await ctx.channel.edit(name=channel_name)
        return discord.Embed(title=f"The channel name was changed from {old_name} to {channel_name}", color=neutral_color)

    async def qotd(self, ctx):
        # 15th May 2022 was the 473rd QOTD day. It is used as a reference point to calculate the day number.
        day_number = 473 + (datetime.utcnow() - datetime.strptime("2022/05/15", "%Y/%m/%d")).days
        embed = discord.Embed(
            title=f"Day {day_number}: {datetime.utcnow().day} {months[datetime.utcnow().month]} {datetime.utcnow().year}",
            description=self.string, color=neutral_color)
        embed.set_footer(text="Put your answers in #qotd-answer")

        await bot.get_channel(qotd_channel_id).send("<@&923978802818871356>", embed=embed)
        await ctx.send(f"**The QOTD has been sent to <#{qotd_channel_id}>!**")
        await bot.get_channel(qotd_ans_channel_id).send(
            "https://media.discordapp.net/attachments/495114793288728586/535784155527774208/Rainbow.gif")
