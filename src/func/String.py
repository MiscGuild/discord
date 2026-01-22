# The following file contains: source, gmember, info, dnkladd, dnklremove, dnklcheck, rename

import inspect
import os
from __main__ import bot
from datetime import datetime, timezone, timedelta

import discord
from quickchart import QuickChart

from src.utils.calculation_utils import (calculate_network_level,
                                         get_color_by_gexp,
                                         get_hypixel_player_rank,
                                         get_player_gexp, get_monthly_gexp)
from src.utils.consts import (PREFIX, DNKL_CHANNEL_ID, DNKL_REQ, GUILDLESS_EMBED,
                              NEG_COLOR, NEUTRAL_COLOR, POS_COLOR,
                              TICKET_CATEGORIES, UNKNOWN_IGN_EMBED, GUILD_HANDLE,
                              MISSING_PERMS_EMBED, NON_STAFF_RANKS)
from src.utils.db_utils import (delete_dnkl, select_one, get_db_uuid_username,
                                get_member_gexp_history, insert_elite_member, get_elite_member)
from src.utils.referral_utils import get_invitation_stats
from src.utils.request_utils import (get_hypixel_player,
                                     get_player_guild, get_name_by_uuid, get_uuid_by_name)
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
        if self.uuid and not self.username:
            uuid = self.uuid
            name = await get_name_by_uuid(uuid)
        elif self.uuid and self.username:
            uuid = self.uuid
            name = self.username
        else:
            name, uuid = await get_uuid_by_name(self.string)
            if not name:
                return UNKNOWN_IGN_EMBED

        guild = await get_player_guild(uuid)

        # Player is guildless
        if not guild:
            return GUILDLESS_EMBED

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
            if "commands" not in ctx.channel.name and str(ctx.channel.category) not in TICKET_CATEGORIES.values():
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
            historical_gexp_data = await get_member_gexp_history(uuid)
            monthly_gexp = 0
            yearly_gexp = 0

            if historical_gexp_data:
                monthly_gexp = await get_monthly_gexp(historical_gexp_data)
                yearly_gexp = sum(historical_gexp_data.values())

            join_date = str(datetime.fromtimestamp(int(str(member["joined"])[:-3])))[:10]
            rank = member["rank"]
            quest_participation = member["questParticipation"] if "questParticipation" in member else 0
            dates = [k for k, _ in gexp_history.items()]
            gexp_vals = [int(v) for _, v in gexp_history.items()]
            gexp_history_text = ""
            for i in range(0, 7):
                date = week_dict.get(i, "None")
                gexp_history_text = gexp_history_text + f"**▸** {date} **{format(gexp_vals[i], ',d')}**\n"

            color, graph_color, graph_border = await get_color_by_gexp(rank, weekly_gexp)

            general_information_text = f"`✚` **Rank**: `{rank}`\n"
            general_information_text += f"`✚` **Joined**: `{join_date}`\n"
            general_information_text += f"`✚` **Quests Completed**: `{quest_participation}`\n"
            general_information_text += f"`✚` **Yearly Guild Experience**: `{format(yearly_gexp, ',d')}`\n"
            general_information_text += f"`✚` **Monthly Guild Experience**: `{format(monthly_gexp, ',d')}`\n\n"
            general_information_text += f"`✚` **Weekly Guild Experience**: `{format(weekly_gexp, ',d')}`\n"

            general_information_text += f"\n{gexp_history_text}"
            # Create embed
            embed = discord.Embed(title=name, url=f"https://plancke.io/hypixel/player/stats/{name}", color=color)
            embed.set_author(name=f"{gname} {gtag}", url=f"https://plancke.io/hypixel/guild/player/{name}")
            embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
            embed.add_field(name="General Information:", value=general_information_text, inline=False)
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
            name, uuid = await get_uuid_by_name(self.string)
            if not name:
                return UNKNOWN_IGN_EMBED
        player_data = await get_hypixel_player(name=uuid)
        # Player doesn't exist
        if not player_data:
            return UNKNOWN_IGN_EMBED

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
        if self.uuid:
            ign = await get_name_by_uuid(self.uuid)
            uuid = self.uuid
        else:
            ign, uuid = await get_uuid_by_name(self.string)
            if not ign:
                return UNKNOWN_IGN_EMBED

        _, weekly_gexp, days_in_guild = await get_player_gexp(uuid)
        if not ign:
            return UNKNOWN_IGN_EMBED

        await ctx.respond("Please respond to the following prompts: ")
        # Ask DNKL application questions
        await dnkl_application(ign, uuid, ctx.channel, ctx.author, weekly_gexp, days_in_guild)

    async def dnklremove(self) -> str:
        if self.string:
            username, uuid = await get_uuid_by_name(self.string)
        else:
            username, uuid = await get_name_by_uuid(self.uuid), self.uuid

        row = await select_one("SELECT * FROM dnkl WHERE uuid = (?)", (uuid,))

        if not row:
            return "This player is not on the do-not-kick-list!"
        else:
            message_id, _ = row
            # Delete row
            await delete_dnkl(uuid)

            # Delete DNKL message
            try:
                msg = await bot.get_channel(DNKL_CHANNEL_ID).fetch_message(message_id)
                await msg.delete()
            except discord.errors.NotFound:
                return f"{username} has been removed from the do-not-kick-list, however the message was not found."

            return f"{username} has been removed from the do-not-kick-list!"

    async def dnklcheck(self) -> discord.Embed:
        if self.uuid and self.username:
            uuid = self.uuid
            name = self.username
        elif self.uuid:
            name = await get_name_by_uuid(self.uuid)
            uuid = self.uuid
        else:
            name, uuid = await get_uuid_by_name(self.string)
            if not name:
                return UNKNOWN_IGN_EMBED

        _, weeklygexp, _ = await get_player_gexp(uuid)

        # Player is not in a guild
        if weeklygexp is None:
            return GUILDLESS_EMBED

        # Player is eligible
        if weeklygexp > DNKL_REQ:
            embed = discord.Embed(title=name, color=POS_COLOR)
            embed.add_field(name="This player is eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{DNKL_REQ} weekly guild experience.", inline=True)

        # Player is not eligible
        else:
            embed = discord.Embed(title=name, color=NEG_COLOR)
            embed.add_field(name="This player is not eligible to apply for the do-not-kick-list.",
                            value=f"They have {weeklygexp}/{DNKL_REQ} weekly guild experience to be eligible.",
                            inline=True)

        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
        embed.set_author(name="Do-not-kick-list: Eligibility Check")
        return embed

    async def rename(self, ctx: discord.ApplicationContext) -> discord.Embed | str:
        if ctx.channel.category.name not in TICKET_CATEGORIES.values():
            return "This command can only be used in tickets!"

        if not self.string:
            return f"**SYNTAX:** `{PREFIX}rename <new channel name>`"

        # Channel is a ticket
        old_name = ctx.channel.name
        channel_name = self.string.replace(" ", "-")
        await ctx.channel.edit(name=channel_name)
        return discord.Embed(title=f"The channel name was changed from {old_name} to {channel_name}",
                             color=NEUTRAL_COLOR)

    async def invites(self) -> discord.Embed:
        if self.uuid and not self.username:
            uuid = self.uuid
            name = await get_name_by_uuid(uuid)
        elif self.uuid and self.username:
            uuid = self.uuid
            name = self.username
        else:
            name, uuid = await get_uuid_by_name(self.string)
            if not name:
                return UNKNOWN_IGN_EMBED

        guild = await get_player_guild(uuid)
        if not guild:
            return GUILDLESS_EMBED
        elif ("name" not in guild) or (guild["name"] != GUILD_HANDLE):
            return MISSING_PERMS_EMBED

        invitation_stats = await get_invitation_stats(uuid)
        weekly_invites = invitation_stats.weekly.total
        weekly_valid_invites = invitation_stats.weekly.valid
        total_invites = invitation_stats.total
        total_valid_invites = invitation_stats.valid

        weekly_invites_dict = {}
        for invitee in invitation_stats.weekly.all_uuids:
            weekly_invites_dict[invitee] = await get_name_by_uuid(invitee)

        valid_invites = [weekly_invites_dict[invitee] for invitee in invitation_stats.weekly.valid_uuids]

        invites_text = ""
        for invitee in weekly_invites_dict.values():
            invitee = invitee.replace("_", "\\_")
            if invitee in valid_invites:
                invites_text += f"🟢 {invitee}\n"
            else:
                invites_text += f"🔴 {invitee}\n"
        embed = discord.Embed(title=f"{name}'s Invites", color=NEUTRAL_COLOR)
        embed.add_field(name="Weekly Invites", value=None if not invites_text else invites_text, inline=False)
        embed.add_field(name="This week's statistics", value=f"Valid Invites: {weekly_valid_invites}\n"
                                                             f"Total Invites: {weekly_invites}\n"
                                                             f"Success Rate: {round(weekly_valid_invites * 100 / weekly_invites) if weekly_invites else 0}%",
                        inline=False)
        embed.add_field(name="Total Valid Invites", value=str(total_valid_invites), inline=True)
        embed.add_field(name="Total Invites", value=str(total_invites), inline=True)
        embed.add_field(name="Total Success Rate",
                        value=f"{round(total_valid_invites * 100 / total_invites if total_invites else 0)}%",
                        inline=True)
        embed.set_footer(text="Total invites and total valid invites do not include this week's invites. They are "
                              "updated at the end of the week."
                              "\nAn invite is considered valid if they earn "
                              f"{format(2 * NON_STAFF_RANKS[0].requirement, ',d')} guild experience at the end of the week. "
                              "If they joined in the middle of the week, their guild experience will be scaled up.")
        return embed

    async def elite_member(self, discord_member: discord.Member = None, monetary_value: int = None,
                           is_automatic: bool = False) -> discord.Embed:
        if discord_member:
            name, uuid = await get_db_uuid_username(discord_id=discord_member.id)
        else:
            username = self.username
            name, uuid = await get_uuid_by_name(username)
        if not name:
            return UNKNOWN_IGN_EMBED

        reason = self.string or ""

        (is_booster, is_sponsor, is_gvg, is_creator, is_indefinite, expiry) = await get_elite_member(uuid) or (
            False, False, False, False, False, None)
        resident_days = 0

        if "server booster" in reason.lower() and is_automatic:
            reason = "Server Booster"
            is_booster = not is_booster


        elif "sponsor" in reason.lower():
            reason = "Event Sponsor"

            is_sponsor = True
            if monetary_value is None:
                return discord.Embed(title="Monetary Value Required",
                                     description="Please provide the amount of money (in dollars) they have spent on the server.",
                                     color=NEG_COLOR)

            resident_days = (1 + (monetary_value - 10) / 8) * 30

            now = datetime.now(timezone.utc)

            if expiry:
                expiry_dt = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                if expiry_dt > now:
                    expiry = expiry_dt + timedelta(days=resident_days)
                else:
                    expiry = now + timedelta(days=resident_days)
            else:
                expiry = now + timedelta(days=resident_days)

            expiry = expiry.strftime("%Y-%m-%d %H:%M:%S")

        elif "gvg" in reason.lower():
            reason = "GvG Team"
            is_gvg = not is_gvg

        elif reason.lower() in ("yt", "content creator", "youtube", "twitch", "streamer", "youtuber"):
            reason = "Content Creator"
            is_creator = not is_creator

        elif "server booster" in reason.lower():
            reason = "Server Booster"
            is_booster = not is_booster


        else:
            return discord.Embed(title="Invalid Reason",
                                 description="Please choose a valid reason for the Elite Member role.",
                                 color=NEG_COLOR)

        is_indefinite = True if any([is_booster, is_creator, is_gvg]) else False

        await insert_elite_member(uuid=uuid, is_booster=is_booster, is_sponsor=is_sponsor, is_creator=is_creator,
                                  is_gvg=is_gvg, is_indefinite=is_indefinite, expiry=expiry)

        if not any([is_sponsor, is_booster, is_creator, is_gvg]):
            embed = discord.Embed(title=f"Elite Member Removed: {name}", color=NEUTRAL_COLOR)
            embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
            return embed

        embed = discord.Embed(title=f"Elite Member: {name}", color=NEUTRAL_COLOR)
        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Indefinite", value=str(is_indefinite), inline=True)
        embed.add_field(name="Expiry", value=expiry if expiry else "None", inline=True)
        if reason == "Event Sponsor":
            embed.add_field(name="Days Added", value=f"{resident_days}", inline=True)
        return embed
