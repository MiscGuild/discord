# The following file contains: source, ginfo, grank, gmember, sync, info, dnkladd, dnklremove, dnkllist, dnklcheck

from __main__ import bot
import discord
import inspect
import os
from datetime import datetime
from quickchart import QuickChart

from func.utils.requests.m_profile import m_profile
from func.utils.requests.player_guild import player_guild
from func.utils.minecraft.get_player_gexp import get_player_gexp
from func.utils.minecraft.get_graph_color_by_rank import get_graph_color_by_rank

from func.utils.consts import pos_color, neg_color, guildless_embed

class String:
    def __init__(self, string: str):
        self.string = string

    # Command from https://github.com/Rapptz/RoboDanny
    async def source(self):
        """
        Displays the source code for the given command!
        """
        source_url = "https://github.com/MiscGuild/MiscBot"
        branch = "main"

        if self.string == None:
            return source_url

        if self.string == "help":
            src = type(bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = bot.get_command(self.string.replace(",", " "))
            if obj == None:
                return "Could not find command."

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


    # async def ginfo():

    
    # async def gexp():


    # async def grank(msg):


    async def gmember(self, ctx):
        name, uuid = await m_profile(self.string)
        guild = await player_guild(uuid)

        # Player is guildless
        if guild == None:
            return guildless_embed
        
        # Get guild data
        gname = guild["guild"]["name"]
        gtag = gname if guild["guild"]["tag"] == None else guild["guild"]["tag"]

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
                                    f"`✚` **Overall Guild Experience**: `{format(weekly_gexp, ',d')}`\n\n{gexp_history_text}", inline=False)

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



    # async def sync(tag=None):


    # async def info():


    # async def dnkladd(start: str, end: str, *, reason: str):


    # async def dnklremove():


    # async def dnkllist():


    async def dnklcheck(self):
        _, weeklygexp = await get_player_gexp(self.string)

        # Player is not in a guild
        if weeklygexp == None:
            guildless_embed

        self.string, uuid = await m_profile(self.string)
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
