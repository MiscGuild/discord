# The following file contains: mute, unmute, kick, ban, softban, unban, sync/forcesync, add, remove, avatar

from typing import Union

import discord
from __main__ import bot
from discord.errors import Forbidden, NotFound
from func.utils.consts import (allies, bot_missing_perms_embed, err_404_embed,
                               guild_handle, neg_color, neutral_color,
                               pos_color, staff_impersonation_embed,
                               ticket_categories, unknown_ign_embed)
from func.utils.discord_utils import check_tag, has_tag_perms
from func.utils.request_utils import (get_gtag, get_mojang_profile,
                                      get_player_guild)


class Union:
    def __init__(self, user: Union[discord.Member, discord.User]):
        self.user = user

    async def mute(self, author, guild_roles, reason: str=None):
        # Default reason is responsible moderator
        if reason == None:
            reason == f"Responsible moderator: {author}"

        await self.user.add_roles(discord.utils.get(guild_roles, name="Muted"))
        return discord.Embed(title="Muted!", description=f"{self.user} was muted by {author}!", color=neg_color)

    async def unmute(self, guild_roles):
        await self.user.remove_roles(discord.utils.get(guild_roles, name="Muted"))
        embed = discord.Embed(title="Unmuted!",
                              description=f"{self.user} has been unmuted!",
                              color=neutral_color)
        return embed

    async def kick(self, author, reason: str=None):
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await self.user.kick(reason=reason)
        return discord.Embed(title="Kicked!",
                             description=f"{self.user} was kicked by {author}",
                             color=neg_color)

    async def ban(self, guild, author, reason: str=None):
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        # Catch MissingPermissions error
        try:
            await guild.ban(self.user, reason=reason)
            return discord.Embed(title="Banned!",
                                 description=f"{self.user} was banned by {author}",
                                 color=neg_color)
        except Forbidden:
            return bot_missing_perms_embed

    async def softban(self, guild, author, reason: str=None):
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        # Catch MissingPermissions error
        try:
            await guild.ban(self.user, reason=reason)
            await guild.unban(self.user, reason=reason)
            return discord.Embed(title="Softbanned!",
                                 description=f"{self.user} was softbanned by {author}",
                                 color=neg_color)
        except Forbidden:
            return bot_missing_perms_embed

    async def unban(self, guild, author, reason: str=None):
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        # Catch Unknown Ban error
        try:
            await guild.unban(self.user, reason=reason)
            return discord.Embed(title="Unbanned!",
                                 description=f"{self.user} was unbanned by {author}",
                                 color=neg_color)
        except NotFound:
            return err_404_embed

    async def sync(self, ctx, name, tag=None, is_fs=False):
        ign, uuid = await get_mojang_profile(name)
        # Invalid username
        if not ign:
            return unknown_ign_embed

        # User trying to sync with staff name
        elif ign in bot.staff_names and bot.staff not in self.user.roles:
            return staff_impersonation_embed

        # Initialize vars for storing changes
        roles_to_add = []
        roles_to_remove = []
        new_nick = ign

        guild_name = await get_player_guild(uuid)
        guild_name = "no guild" if not guild_name else guild_name["name"]
        can_tag = await has_tag_perms(self.user)

        # Check tag before other logic
        if tag and can_tag:
            tag_check_success, tag_check_reason = await check_tag(tag)
            if tag_check_success:
                new_nick += f"[{tag}]"
            else:
                return tag_check_reason

        # Users is a member
        if guild_name == guild_handle:
            roles_to_add.append(bot.member_role)
            roles_to_remove.extend([bot.guest, bot.awaiting_app])

        # User is an ally
        elif guild_name in allies:
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
        embed = discord.Embed(title="Your nick, roles, and tag have been successfully changed!",
                              description="If this wasn't the change you anticipated, please create a ticket!",
                              color=neutral_color)
        embed.set_footer(text=f"• Member of {guild_name}" + "\n• Removed: " + ", ".join([role.name for role in roles_to_remove]) + "\n• Added: " + ", ".join([role.name for role in roles_to_add]))

        # Set roles and nick
        try:
            await self.user.add_roles(*roles_to_add, reason="Sync")
            await self.user.remove_roles(*roles_to_remove, reason="Sync")
            await self.user.edit(nick=new_nick)
        except Forbidden:
            return bot_missing_perms_embed

        return embed

    async def add(self, ctx):
        if ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        # Set perms
        await ctx.channel.set_permissions(self.user, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
        return discord.Embed(title=f"{self.user.name} has been added to the ticket!", color=pos_color)
       
    async def remove(self, ctx):
        if ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        # Set perms
        await ctx.channel.set_permissions(self.user, send_messages=False, read_messages=False,
                                            add_reactions=False, embed_links=False,
                                            attach_files=False,
                                            read_message_history=False, external_emojis=False)
        return discord.Embed(title=f"{self.user.name} has been removed from the ticket!", color=pos_color)

    async def avatar(self):
        embed = discord.Embed(title=f"{self.user}'s avatar:", color=neutral_color)
        return embed.set_image(url=self.user.avatar_url)
