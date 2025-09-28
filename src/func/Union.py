# The following file contains: mute, unmute, kick, ban, softban, unban, sync/forcesync, register, add, remove, avatar

import asyncio
from __main__ import bot
from datetime import datetime, timezone
from typing import Union as typingUnion, Tuple

import discord

from src.utils.calculation_utils import check_tag, get_monthly_gexp
from src.utils.consts import (active_req, allies, discord_not_linked_embed, guild_handle, neg_color, neutral_color,
                              pos_color, registration_channel_id,
                              staff_impersonation_embed, ticket_categories,
                              unknown_ign_embed, join_request_embed, guildless_embed)
from src.utils.db_utils import update_member, insert_new_member, get_db_uuid_username, set_do_ping_db, \
    get_member_gexp_history, get_elite_member, get_do_ping
from src.utils.discord_utils import (create_ticket, has_tag_perms,
                                     is_linked_discord)
from src.utils.referral_utils import get_invitation_stats
from src.utils.request_utils import (get_gtag, get_hypixel_player,
                                     get_player_guild, get_name_by_uuid, get_uuid_by_name)


class Union:
    def __init__(self, user: typingUnion[discord.Member, discord.User]):
        self.user = user

    async def mute(self, author, guild_roles, reason: str = None) -> discord.Embed:
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await self.user.add_roles(discord.utils.get(guild_roles, name="Muted"))
        return discord.Embed(title="Muted!", description=f"{self.user} was muted by {author}!", color=neg_color)

    async def unmute(self, guild_roles) -> discord.Embed:
        await self.user.remove_roles(discord.utils.get(guild_roles, name="Muted"))
        embed = discord.Embed(title="Unmuted!",
                              description=f"{self.user} has been unmuted!",
                              color=neutral_color)
        return embed

    async def kick(self, author: discord.User, reason: str = None) -> discord.Embed:
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await self.user.kick(reason=reason)
        return discord.Embed(title="Kicked!",
                             description=f"{self.user} was kicked by {author}",
                             color=neg_color)

    async def ban(self, guild: discord.Guild, author: discord.User, reason: str = None) -> discord.Embed:
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await guild.ban(self.user, reason=reason)
        return discord.Embed(title="Banned!",
                             description=f"{self.user} was banned by {author}",
                             color=neg_color)

    async def softban(self, guild: discord.Guild, author: discord.User, reason: str = None) -> discord.Embed:
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await guild.ban(self.user, reason=reason)
        await guild.unban(self.user, reason=reason)
        return discord.Embed(title="Softbanned!",
                             description=f"{self.user} was softbanned by {author}",
                             color=neg_color)

    async def unban(self, guild: discord.Guild, author: discord.User, reason: str = None) -> discord.Embed:
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await guild.unban(self.user, reason=reason)
        return discord.Embed(title="Unbanned!",
                             description=f"{self.user} was unbanned by {author}",
                             color=neg_color)

    async def sync(self, ctx: discord.ApplicationContext, name: str, tag: str = None,
                   is_fs=False) -> discord.Embed | str:
        await ctx.defer()
        if is_fs and not name:
            username, uuid = await get_db_uuid_username(discord_id=self.user.id)
            ign = await get_name_by_uuid(uuid, is_sync=True)
            if username != ign:
                await update_member(self.user.id, uuid, ign)
        elif not name:
            username, uuid = await get_db_uuid_username(discord_id=self.user.id)
            ign = await get_name_by_uuid(uuid, is_sync=True)
            if username != ign:
                await update_member(self.user.id, uuid, ign)
        else:
            ign, uuid = await get_uuid_by_name(name)

        # Invalid username
        if not ign:
            return unknown_ign_embed

        # Initialize vars for storing changes
        roles_to_add = []
        roles_to_remove = [bot.processing]
        new_nick = ign

        # Fetch player & guild data
        player_data = await get_hypixel_player(uuid=uuid)
        guild_data = await get_player_guild(uuid)

        # Account is not linked to discord
        if not await is_linked_discord(player_data, self.user) and is_fs is False:
            embed = discord_not_linked_embed.copy()
            return embed.add_field(name="Do the above and then enter the following in chat:",
                                   value=f"`{str(self.user.name)}`")

        await update_member(discord_id=self.user.id,
                            uuid=uuid,
                            username=ign)
        guild_name = "no guild" if not guild_data else guild_data["name"]
        can_tag = await has_tag_perms(self.user)

        # Check tag before other logic
        if tag and can_tag:
            tag_check_success, tag_check_reason = await check_tag(tag)
            if tag_check_success:
                new_nick += f" [{tag}]"
            else:
                return tag_check_reason

        # User is a member
        if guild_name == guild_handle:
            roles_to_add.append(bot.member_role)
            roles_to_remove.extend([bot.guest, bot.ally, bot.new_member_role, bot.processing])

            # Add active role if eligible
            for member in guild_data["members"]:
                if member["uuid"] == uuid and sum(member["expHistory"].values()) > active_req:
                    roles_to_add.append(bot.active_role)
                    break

        # User is an ally
        elif guild_name in allies:
            if not can_tag:
                new_nick += f" {await get_gtag(guild_name)}"
            roles_to_remove.extend([bot.new_member_role, bot.member_role, bot.new_member_role, bot.processing])
            roles_to_add.extend([bot.guest, bot.ally])

        # User is a guest
        else:
            # Filter people who have not been approved to join the discord
            if ctx.channel.id == registration_channel_id and not is_fs:
                return "You cannot use this command in a registration ticket!\nKindly await staff assistance!"

            roles_to_add.append(bot.guest)
            roles_to_remove.extend([bot.member_role, bot.new_member_role, bot.ally])

        # Create embed
        embed = discord.Embed(title=f"{ign}'s nick, roles, and tag have been successfully changed!",
                              description="If this wasn't the change you anticipated, please create a ticket!",
                              color=neutral_color)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        embed.set_footer(text=f"• Member of {guild_name}" + "\n• Removed: " + ", ".join(
            [role.name for role in roles_to_remove]) + "\n• Added: " + ", ".join([role.name for role in roles_to_add]))

        # Set roles and nick
        await self.user.add_roles(*roles_to_add, reason="Sync")
        await self.user.remove_roles(*roles_to_remove, reason="Sync")
        await self.user.edit(nick=new_nick)

        return embed

    async def register(self, ctx: discord.ApplicationContext, name: str) -> Tuple[discord.Embed, str] | Tuple[
        str, None] | Tuple[
        discord.Embed, None]:
        await ctx.defer()
        # Make sure it is only used in registration channel
        if ctx.channel.id != registration_channel_id:
            return "This command can only be used in the registration channel!\nThe command you are looking for is `/sync`", None

        ign, uuid = await get_uuid_by_name(name)

        if not ign:
            return unknown_ign_embed, None

        # Filter out people impersonating staff
        if ign in bot.staff_names:
            return staff_impersonation_embed, None

        username, uuid, check_already_registered = await get_db_uuid_username(uuid=uuid, get_discord_id=True)

        discord_account_already_linked = await get_db_uuid_username(discord_id=check_already_registered)
        if not check_already_registered and not any(discord_account_already_linked):
            await insert_new_member(discord_id=self.user.id,
                                    uuid=uuid,
                                    username=ign)
        # Fetch player & guild data
        guild_data = await get_player_guild(uuid)

        guild_name = "Guildless" if not guild_data else guild_data["name"]

        embed = discord.Embed(
            title="Registration successful!", color=neutral_color)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        embed.add_field(name=ign, value=f"Member of {guild_name}" if guild_name != "Guildless" else "Guildless")

        if check_already_registered:
            original_owner = check_already_registered
            await ctx.author.add_roles(bot.processing, reason="Registration - Processing")
            ticket = await create_ticket(ctx.author, f"ticket-{ign}",
                                         category_name=ticket_categories["registrees"])
            await ticket.purge(limit=1000)
            await ticket.edit(name=f"duplicate-registration-{ign}", topic=f"{ctx.author.id}|",
                              category=discord.utils.get(ctx.guild.categories,
                                                         name=ticket_categories["registrees"]))
            guest_ticket = ticket

            embed = discord.Embed(title="Conflict during registration!",
                                  description=f"The account associated with {ign} is currently registered to "
                                              f"<@{original_owner}>\n" +
                                              f"Member of {guild_name}" if guild_name != "Guildless" else "Guildless",
                                  color=neg_color)
            embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
            embed.set_footer(text="If you no longer have access to the other discord account/"
                                  "would like to transfer to this discord account, let staff know. "
                                  "They will use `/forcesync`.")
            await ticket.send(embed=embed)
        elif any(discord_account_already_linked):
            original_account_uuid = discord_account_already_linked[1]
            original_username = discord_account_already_linked[0]
            await ctx.author.add_roles(bot.processing, reason="Registration - Processing")
            ticket = await create_ticket(ctx.author, f"ticket-{ign}",
                                         category_name=ticket_categories["registrees"])
            await ticket.purge(limit=1000)
            await ticket.edit(name=f"duplicate-registration-{ign}-{original_username}", topic=f"{ctx.author.id}|",
                              category=discord.utils.get(ctx.guild.categories,
                                                         name=ticket_categories["registrees"]))
            guest_ticket = ticket

            embed = discord.Embed(title="Conflict during registration!",
                                  description=f"<@{self.user.id}> is already registered to {original_username}. \
                                  Miscellaneous does not support multiple accounts for a single discord account.\n",
                                  color=neg_color)
            embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
            embed.set_footer(text="If you no longer have access to the other minecraft account/"
                                  "would like to transfer to this discord account, let staff know. "
                                  "They will use `/forcesync`.")
            await ticket.send(embed=embed)
        # User is a member
        elif guild_name == guild_handle:
            await ctx.author.add_roles(bot.member_role, reason="Registration - Member")
            guest_ticket = None

        # User is in an allied guild
        elif guild_name in allies:
            await ctx.author.add_roles(bot.guest, bot.ally, reason="Registration - Ally")

            # Add guild tag as nick
            gtag = "" if "tag" not in guild_data else guild_data["tag"]
            if not ctx.author.nick or gtag not in ctx.author.nick:
                ign = ign + " " + f"[{gtag}]"
            guest_ticket = None

        # User is a guest
        else:
            await ctx.author.add_roles(bot.processing, reason="Registration - Processing")
            ticket = await create_ticket(ctx.author, f"ticket-{ign}",
                                         category_name=ticket_categories["registrees"])
            await ticket.purge(limit=1000)
            await ticket.edit(name=f"join-request-{ign}", topic=f"{ctx.author.id}|",
                              category=discord.utils.get(ctx.guild.categories,
                                                         name=ticket_categories["registrees"]))
            guest_ticket = ticket

            class Join_Misc_Buttons(discord.ui.Button):
                def __init__(self, button_fields: list):
                    """
                    2 buttons for 2 registration actions. `custom_id` is needed for persistent views.
                    """
                    super().__init__(label=button_fields[0], custom_id=button_fields[1], style=button_fields[2])

                async def callback(self, interaction: discord.Interaction):
                    # if bot.staff not in interaction.user.roles and ticket.id != interaction.channel_id: return
                    if interaction.custom_id == "Yes":
                        await ticket.purge(limit=100)
                        await ticket.send(
                            embed=join_request_embed.set_author(name=f"{ign} wishes to join Miscellaneous"))
                        await interaction.user.add_roles(bot.guest, reason="Registration - Guest")

                        if guild_name != "Guildless":
                            await ticket.send(
                                f"{interaction.user.mention} kindly leave your current guild so that"
                                f" we can can invite you to Miscellaneous.")

                    elif interaction.custom_id == "No":
                        await ticket.purge(limit=100)
                        await interaction.user.remove_roles(bot.processing, reason="Registration - Guest")
                        await interaction.user.add_roles(bot.guest, reason="Registration - Guest")
                        await ticket.send(
                            embed=discord.Embed(
                                title="You have been given the Guest role!\n"
                                      "**This ticket will be deleted in 10 seconds.** "
                                      "\n\n*If you need assistance with anything else,"
                                      " create a new ticket using* `,new`",
                                color=neg_color))
                        await asyncio.sleep(10)
                        await discord.TextChannel.delete(ticket)

            view = discord.ui.View(timeout=None)
            buttons = [["Yes", "Yes", discord.enums.ButtonStyle.primary],
                       ["No", "No", discord.enums.ButtonStyle.red]]
            # Loop through the list of roles and add a new button to the view for each role.
            for button in buttons:
                # Get the role from the guild by ID.
                view.add_item(Join_Misc_Buttons(button))

            await ticket.send(
                embed=discord.Embed(title="Do you wish to join Miscellaneous in-game?", color=neutral_color),
                view=view)

        # Remove new member role, edit nick and delete message
        await ctx.author.remove_roles(bot.new_member_role, reason="Register")
        await ctx.author.edit(nick=ign)

        return (embed, guest_ticket) if guild_name != guild_handle else (embed, None)

    async def add(self, ctx: discord.ApplicationContext) -> discord.Embed | str:
        if ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        # Set perms
        await ctx.channel.set_permissions(self.user, send_messages=True, read_messages=True, add_reactions=True,
                                          embed_links=True, attach_files=True, read_message_history=True,
                                          external_emojis=True)
        return discord.Embed(title=f"{self.user.name} has been added to the ticket!", color=pos_color)

    async def remove(self, ctx: discord.ApplicationContext) -> discord.Embed | str:
        if ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        # Set perms
        await ctx.channel.set_permissions(self.user, send_messages=False, read_messages=False,
                                          add_reactions=False, embed_links=False,
                                          attach_files=False,
                                          read_message_history=False, external_emojis=False)
        return discord.Embed(title=f"{self.user.name} has been removed from the ticket!", color=pos_color)

    async def avatar(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"{self.user}'s avatar:", color=neutral_color)
        return embed.set_image(url=self.user.avatar)

    async def whois(self) -> discord.Embed:
        username, uuid = await get_db_uuid_username(discord_id=self.user.id)
        embed = discord.Embed(
            title=username,
            description=f"Discord Username: {self.user.name}\n"
                        f"Discord Nick: {self.user.nick}",
            color=neutral_color
        )
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        embed.set_footer(text=f"UUID: {uuid}")
        return embed

    async def do_pings(self, setting: int) -> discord.Embed:
        uuid = await set_do_ping_db(self.user.id, setting)
        embed = discord.Embed(
            title="Ping Settings Updated!",
            description=f"You will **{'now' if bool(setting) else 'not'}** be pinged in automatic daily and weekly leaderboard messages!",
            color=neutral_color
        )
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        return embed

    async def me(self):
        username, uuid = await get_db_uuid_username(discord_id=self.user.id)
        is_booster, is_sponsor, is_gvg, is_creator, is_indefinite, expiry = await get_elite_member(uuid) or (
            False, False, False, False, False, None)
        historical_gexp_data = await get_member_gexp_history(uuid)
        guild = await get_player_guild(uuid)

        if not guild:
            return guildless_embed
        if guild["name"] != guild_handle:
            return discord.Embed(
                title="You are not a member of Miscellaneous!",
                description=f"Member of {guild['name']}",
                color=neg_color
            )

        member = next((m for m in guild["members"] if m["uuid"] == uuid), None)
        weekly_gexp_history = member["expHistory"]

        guild_rank = member["rank"]
        weekly_gexp = sum(weekly_gexp_history.values())
        monthly_gexp = 0
        yearly_gexp = 0

        if historical_gexp_data:
            monthly_gexp = await get_monthly_gexp(historical_gexp_data)
            yearly_gexp = sum(historical_gexp_data.values())

        invitation_stats = await get_invitation_stats(uuid)

        embed = discord.Embed(
            title=username,
            description=f"**Discord Username:** {self.user.name}\n"
                        f"**Discord Nick:** {self.user.nick}\n"
                        f"**Mentions:** {'✅' if (await get_do_ping(uuid))[1] else '❌'}\n",
            color=neutral_color
        )
        if any([is_booster, is_sponsor, is_gvg, is_creator]):
            expiry_str = expiry if not is_indefinite else None
            if expiry_str:
                expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                unix_ts = int(expiry_dt.timestamp())
                expiry_display = f"<t:{unix_ts}:R>"
            else:
                expiry_display = "Never"

            embed.add_field(name="Elite Member", value=f"`✚` Server Booster: {'✅' if is_booster else '❌'}\n"
                                                       f"`✚` Event Sponsor: {'✅' if is_sponsor else '❌'}\n"
                                                       f"`✚` Exceptional GvG Team Member: {'✅' if is_gvg else '❌'}\n"
                                                       f"`✚` Content Creator: {'✅' if is_creator else '❌'}\n"
                                                       f"`✚` Expiry: {expiry_display}", inline=False)
        elif guild_rank == "Elite Member":
            embed.add_field(name="Current Rank", value=f"Elite Member - Active", inline=False)
        else:
            embed.add_field(name="Current Rank", value=f"{guild_rank}", inline=False)
        embed.add_field(name="GEXP History", value=f"`✚` Weekly: {format(weekly_gexp, ',d')}\n"
                                                   f"`✚` Monthly: {format(monthly_gexp, ',d')}\n"
                                                   f"`✚` Yearly: {format(yearly_gexp, ',d')}", inline=True)

        embed.add_field(name="Invites",
                        value=f"`✚` Weekly Valid: {format(invitation_stats.weekly.valid, ',d')}\n"
                              f"`✚` Weekly: {format(invitation_stats.weekly.total, ',d')}\n"
                              f"`✚` Total Valid: {format(invitation_stats.valid, ',d')}\n"
                              f"`✚` Total: {format(invitation_stats.total, ',d')}\n", inline=True)

        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        return embed
