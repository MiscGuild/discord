# The following file contains: source, gmember, info, dnkladd, dnklremove, dnklcheck, register, rename

from __main__ import bot
from datetime import datetime
import discord
import inspect
import os
from quickchart import QuickChart

from func.utils.minecraft_utils import get_hypixel_player_rank, get_player_gexp, get_graph_color_by_rank, calculate_network_level
from func.utils.discord_utils import create_ticket, is_valid_date
from func.utils.request_utils import get_hypixel_player, get_mojang_profile, get_player_guild
from func.utils.db_utils import delete_dnkl, select_one, insert_new_dnkl, update_dnkl
from func.utils.consts import dnkl_channel_id, registration_channel_id, dnkl_req, guild_handle, allies, pos_color, neutral_color, neg_color, guildless_embed, unknown_ign_embed, staff_impersonation_embed, invalid_date_msg, months


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
        gname = guild["name"]
        gtag = gname if not guild["tag"] else guild["tag"]

        # Find player in req
        for member in guild["members"]:
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

    async def info(self):
        player_data = await get_hypixel_player(self.string)
        # Player doesn't exist
        if not player_data:
            return unknown_ign_embed

        # Gather info
        ign = player_data["displayname"]
        uuid = player_data["uuid"]
        _, rank = await get_hypixel_player_rank(player_data)
        nwl = await calculate_network_level(player_data["networkExp"])
        karma = f"{int(player_data['karma']):,d}"
        achievement_points =  "-"  if "achievementPoints" not in player_data else f"{int(player_data['achievementPoints']):,d}"
        completed_challenges = "0" if "general_challenger" not in player_data["achievements"] else f"{int(player_data['achievements']['general_challenger']):,d}"
        completed_quests = "-" if "quests" not in player_data else f"{len(player_data['quests']):,d}"
        first_login = datetime.fromtimestamp(int(str(player_data["firstLogin"])[:-3]))
        last_login = "Unkown" if "lastLogin" not in player_data else datetime.fromtimestamp(int(str(player_data["lastLogin"])[:-3]))
        guild = await get_player_guild(uuid)
        gtag = "" if not guild or "tag" not in guild else f"[{guild['tag']}]"

        embed = discord.Embed(title=f"{rank} {ign} {gtag}",
                                url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                color=0x8368ff)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        embed.add_field(name="Network Level:", value=f"`{nwl}`", inline=True)
        embed.add_field(name="Karma:", value=f"`{karma}`", inline=True)
        embed.add_field(name="Achievement Points:", value=f"`{achievement_points}`", inline=False)
        embed.add_field(name="Challenges Finished:", value=f"`{completed_challenges}`", inline=True)
        embed.add_field(name="Quests Completed:", value=f"`{completed_quests}`", inline=True)
        embed.add_field(name="First • Last login", value=f"`{first_login} • {last_login}`", inline=False)
        return embed.set_image(url=f"https://gen.plancke.io/exp/{ign}.png")

    async def dnkladd(self, ctx):
        # start, end, reason
        ign, uuid = await get_mojang_profile(self.string)
        if not ign:
            return unknown_ign_embed

        # Ask for start date
        await ctx.send("**What is the start date?** (YYYY/MM/DD)")
        start_date = await bot.wait_for("message",
                                            check=lambda
                                            x: x.channel == ctx.channel and x.author == ctx.author)
        valid_date, sd, sm, sy = await is_valid_date(start_date.content)
        if not valid_date:
            return invalid_date_msg

        # Ask for end date
        await ctx.send("**What is the end date?** (YYYY/MM/DD)")
        end_date = await bot.wait_for("message",
                                            check=lambda
                                            x: x.channel == ctx.channel and x.author == ctx.author)
        valid_date, ed, em, ey = await is_valid_date(end_date.content)
        if not valid_date:
            return invalid_date_msg

        # Ask for reason
        await ctx.send("**What is the reason for their inactivity?**")
        reason = await bot.wait_for("message",
                                            check=lambda
                                            x: x.channel == ctx.channel and x.author == ctx.author)
        reason = reason.content

        # Get worded months (1 = January)
        sm = months[sm]
        em = months[em]

        # Send embed to DNKL channel
        embed = discord.Embed(title=ign,
                                url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                color=neutral_color)
        embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')
        embed.add_field(name="IGN:", value=f"{ign}", inline=False)
        embed.add_field(name="Start:", value=f"{sd} {sm} {sy}", inline=False)
        embed.add_field(name="End:", value=f"{ed} {em} {ey}", inline=False)
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
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
        row = await select_one("SELECT * FROM dnkl WHERE username = (?)", (self.string,))

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
        _, weeklygexp = await get_player_gexp(self.string)

        # Player is not in a guild
        if not weeklygexp:
            return guildless_embed

        self.string, uuid = await get_mojang_profile(self.string)
        # Player is eligible
        if weeklygexp > dnkl_req:
            embed = discord.Embed(title=self.string, color=pos_color)
            embed.add_field(name="This player is eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{dnkl_req} weekly guild experience.",
                            inline=True)


        # Player is not eligible
        else:
            embed = discord.Embed(title=self.string, color=neg_color)
            embed.add_field(name="This player is not eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{dnkl_req} weekly guild experience to be eligible.",
                            inline=True)

        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
        embed.set_author(name="Do-not-kick-list: Eligibility Check")
        return embed

    async def register(self, ctx):
        async with ctx.channel.typing():
            # Make sure it is only used in registration channel
            if ctx.channel.id != registration_channel_id:
                return "This command can only be used in the registration channel!"
                
            ign, uuid = await get_mojang_profile(self.string)

            if ign == None:
                return unknown_ign_embed
            # Filter out people impersonating staff
            if ign in bot.staff_names:
                return staff_impersonation_embed

            guild = await get_player_guild(uuid)
            guild_name = None if guild == None else guild["name"]

            # User is a member
            if guild_name == guild_handle:
                # Add member role and delete message
                await ctx.author.add_roles(bot.member_role, reason="Register")
                await ctx.message.delete()
                embed = discord.Embed(title="Registration successful!")
                embed.add_field(name=ign,
                                value="Member of " + guild_handle)
                return embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")

            # User is in an allied guild
            if guild_name in allies:
                # Add guild tag as nick
                gtag = "" if "tag" not in guild else guild["tag"]
                if not ctx.author.nick or gtag not in ctx.author.nick:
                    ign = ign + " " + gtag
                    await ctx.author.edit(nick=ign)

                    # Add and remove roles and delete message
                    await ctx.author.remove_roles(bot.new_member_role, reason="Register")
                    await ctx.author.add_roles(bot.guest, bot.ally, reason="Register")
                    await ctx.message.delete()

                    embed = discord.Embed(title="Registration successful!")
                    embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
                    return embed.add_field(name=ign, value=f"Member of {guild}")

            # User is a guest
            await ctx.author.remove_roles(bot.new_member_role, reason="Register")
            await ctx.author.add_roles(bot.awaiting_app, reason="Register")
            await ctx.message.delete()

            # Create registration ticket
            await create_ticket("RTickets", f"registration-ticket-{ctx.author.name}", ctx.author)

            embed = discord.Embed(title="Registration successful!", color=neutral_color)
            embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
            return embed.add_field(name=ign, value="New Member")

    async def rename(self, ctx):
        await ctx.message.delete()
        # Channel is not a ticket
        if ctx.channel.category.name not in bot.ticket_categories:
            return await ctx.send("This command can only be used in tickets!")
        
        # Channel is a ticket
        channel_name = self.string.replace(" ", "-")
        await ctx.channel.edit(name=channel_name)
