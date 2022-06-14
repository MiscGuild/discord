# The following file contains: mute, unmute, kick, ban, softban, unban, sync/forcesync, register, add, remove, avatar

import asyncio
from typing import Union

import discord
from __main__ import bot
from discord.errors import Forbidden, NotFound
from src.utils.consts import (active_req, allies, bot_missing_perms_embed,
                              discord_not_linked_embed, err_404_embed,
                              guild_handle, neg_color, neutral_color,
                              pos_color, registration_channel_id,
                              staff_impersonation_embed, ticket_categories,
                              unknown_ign_embed)
from src.utils.discord_utils import (check_tag, create_ticket, has_tag_perms,
                                     is_linked_discord)
from src.utils.request_utils import (get_gtag, get_hypixel_player,
                                     get_mojang_profile, get_player_guild)


class Union:
    def __init__(self, user: Union[discord.Member, discord.User]):
        self.user = user

    async def mute(self, author, guild_roles, reason: str = None):
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await self.user.add_roles(discord.utils.get(guild_roles, name="Muted"))
        return discord.Embed(title="Muted!", description=f"{self.user} was muted by {author}!", color=neg_color)

    async def unmute(self, guild_roles):
        await self.user.remove_roles(discord.utils.get(guild_roles, name="Muted"))
        embed = discord.Embed(title="Unmuted!",
                              description=f"{self.user} has been unmuted!",
                              color=neutral_color)
        return embed

    async def kick(self, author, reason: str = None):
        # Default reason is responsible moderator
        if not reason:
            reason = f"Responsible moderator: {author}"

        await self.user.kick(reason=reason)
        return discord.Embed(title="Kicked!",
                             description=f"{self.user} was kicked by {author}",
                             color=neg_color)

    async def ban(self, guild, author, reason: str = None):
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

    async def softban(self, guild, author, reason: str = None):
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

    async def unban(self, guild, author, reason: str = None):
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

    async def sync(self, ctx, name: str, tag: str = None, is_fs=False):
        ign, uuid = await get_mojang_profile(name)
        # Invalid username
        if not ign:
            return unknown_ign_embed

        # Fetch player & guild data
        player_data = await get_hypixel_player(uuid=uuid)
        guild_data = await get_player_guild(uuid)

        # Account is not linked to discord
        if not await is_linked_discord(player_data, self.user) and is_fs is False:
            return discord_not_linked_embed

        # Initialize vars for storing changes
        roles_to_add = []
        roles_to_remove = [bot.processing]
        new_nick = ign

        guild_name = "no guild" if not guild_data else guild_data["name"]
        can_tag = await has_tag_perms(self.user)

        # Check tag before other logic
        if tag and can_tag:
            tag_check_success, tag_check_reason = await check_tag(tag)
            if tag_check_success:
                new_nick += f" [{tag}]"
            else:
                return tag_check_reason

        # Users is a member
        if guild_name == guild_handle:
            roles_to_add.append(bot.member_role)
            roles_to_remove.extend([bot.guest])

            # Add active role if eligible
            for member in guild_data["members"]:
                if member["uuid"] == uuid and sum(member["expHistory"].values()) > active_req:
                    roles_to_add.append(bot.active_role)
                    break

        # User is an ally
        elif guild_name in allies:
            gtag = await get_gtag(guild_name)

            # Account for if user has nick perms
            new_nick = ign + " " + gtag
            roles_to_remove.extend([bot.new_member_role, bot.member_role])
            roles_to_add.extend([bot.guest, bot.ally])

        # User is a guest
        else:
            # Filter people who have not been approved to join the discord
            if not is_fs:
                return "You cannot use this command in a registration ticket!\nKindly await staff assistance!"

            roles_to_add.append(bot.guest)
            roles_to_remove.extend([bot.member_role, bot.new_member_role])

        # Create embed
        embed = discord.Embed(title=f"{ign}'s nick, roles, and tag have been successfully changed!",
                              description="If this wasn't the change you anticipated, please create a ticket!",
                              color=neutral_color)
        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
        embed.set_footer(text=f"• Member of {guild_name}" + "\n• Removed: " + ", ".join(
            [role.name for role in roles_to_remove]) + "\n• Added: " + ", ".join([role.name for role in roles_to_add]))

        # Set roles and nick
        try:
            await self.user.add_roles(*roles_to_add, reason="Sync")
            await self.user.remove_roles(*roles_to_remove, reason="Sync")
            await self.user.edit(nick=new_nick)
        except Forbidden:
            return bot_missing_perms_embed

        return embed

    async def register(self, ctx, name):
        async with ctx.channel.typing():
            # Make sure it is only used in registration channel
            if ctx.channel.id != registration_channel_id:
                return "This command can only be used in the registration channel!"

            ign, uuid = await get_mojang_profile(name)

            if not ign:
                return unknown_ign_embed

            # Filter out people impersonating staff
            if ign in bot.staff_names:
                return staff_impersonation_embed

            # Fetch player & guild data
            guild_data = await get_player_guild(uuid)

            guild_name = "Guildless" if not guild_data else guild_data["name"]

            await ctx.author.edit(nick=ign)

            # User is a member
            if guild_name == guild_handle:
                await ctx.author.add_roles(bot.member_role, reason="Registration - Member")


            # User is in an allied guild
            elif guild_name in allies:
                await ctx.author.add_roles(bot.guest, bot.ally, reason="Registration - Ally")

                # Add guild tag as nick
                gtag = "" if "tag" not in guild_data else guild_data["tag"]
                if not ctx.author.nick or gtag not in ctx.author.nick:
                    ign = ign + " " + gtag

            # User is a guest
            else:
                await ctx.author.add_roles(bot.processing, reason="Registration - Processing")
                ticket = await create_ticket(ctx.author, f"ticket-{ign}",
                                             category_name=ticket_categories["registrees"])
                await ticket.purge(limit=1000)
                await ticket.edit(name=f"join-request-{ign}", topic=f"{ctx.author.id}|",
                                  category=discord.utils.get(ctx.guild.categories,
                                                             name=ticket_categories["registrees"]))

                class Join_Misc_Buttons(discord.ui.Button):
                    def __init__(self, button: list):
                        """
                        2 buttons for 2 registration actions. `custom_id` is needed for persistent views.
                        """
                        super().__init__(label=button[0], custom_id=button[1], style=button[2])

                    async def callback(self, interaction: discord.Interaction):
                        # if bot.staff not in interaction.user.roles and ticket.id != interaction.channel_id: return
                        if interaction.custom_id == "Yes":
                            await ticket.purge(limit=100)
                            await ticket.send(
                                embed=discord.Embed(title=f"{ign} wishes to join Miscellaneous!",
                                                    description=f"Please await staff assistance!\nIn the meanwhile, you may explore the Discord!",
                                                    color=neutral_color))
                            await interaction.user.add_roles(bot.guest, reason="Registration - Guest")

                        elif interaction.custom_id == "No":
                            await ticket.purge(limit=100)
                            await interaction.user.remove_roles(bot.processing, reason="Registration - Guest")
                            await interaction.user.add_roles(bot.guest, reason="Registration - Guest")
                            await ticket.send(
                                embed=discord.Embed(
                                    title="You have been given the Guest role!\n**This ticket will be deleted in 10 seconds.** \n\n*If you need assistance with anything else, create a new ticket using* `,new`",
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
            await ctx.message.delete()

            # Send success embed
            embed = discord.Embed(
                title="Registration successful!", color=neutral_color)
            embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
            return embed.add_field(name=ign, value=f"Member of {guild_name}")

    async def add(self, ctx):
        if ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        # Set perms
        await ctx.channel.set_permissions(self.user, send_messages=True, read_messages=True, add_reactions=True,
                                          embed_links=True, attach_files=True, read_message_history=True,
                                          external_emojis=True)
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
        embed = discord.Embed(
            title=f"{self.user}'s avatar:", color=neutral_color)
        return embed.set_image(url=self.user.avatar)
