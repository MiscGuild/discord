# The following file contains: on_member_join, on_error, on_command_error, reactionroles, tickets, on_interaction
import traceback
from __main__ import bot

import discord
from discord.ext import commands

from src.func.String import String
from src.utils.calculation_utils import (
    extract_usernames, classify_error_embed, safe_reply, build_usage_embed, log_traceback_to_channel
)
from src.utils.consts import (
    error_channel_id, invalid_command_embed,
    staff_bridge_channel, log_channel_id,
    registration_channel_id, registration_embed, err_404_embed,
    qotd_thread_id, geoguessr_thread_id
)
from src.utils.discord_utils import create_ticket, send_thread_message
from src.utils.referral_utils import validate_invites


class Listener:
    def __init__(self, bot, obj=None):
        self.bot = bot
        self.obj = obj

    async def on_member_join(self, member: discord.Member) -> None:
        await member.add_roles(self.bot.new_member_role)
        await self.bot.get_channel(registration_channel_id).send(embed=registration_embed)

    async def on_error(self, event_name: str) -> None:
        tb = traceback.format_exc()
        await self.bot.get_channel(error_channel_id).send(
            f"Ignoring exception in event {event_name}:\n```py\n{tb}\n```"
        )

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if ctx.command and (hasattr(ctx.command, "on_error") or (ctx.cog and hasattr(ctx.cog, "cog_command_error"))):
            return
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            await safe_reply(ctx, embed=invalid_command_embed)
            return

        embed = classify_error_embed(error)
        if embed:
            await safe_reply(ctx, embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            await safe_reply(ctx, embed=build_usage_embed(ctx))
        else:
            await safe_reply(ctx, embed=err_404_embed)
            await log_traceback_to_channel(self.bot, error_channel_id, ctx, error)

    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        if (ctx.command and getattr(ctx.command, "has_error_handler", lambda: False)()) or \
                (ctx.cog and getattr(ctx.cog, "has_error_handler", lambda: False)()):
            return
        error = getattr(error, "original", error)

        embed = classify_error_embed(error)
        if embed:
            await safe_reply(ctx, embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            await safe_reply(ctx, embed=build_usage_embed(ctx))
        else:
            await safe_reply(ctx, embed=err_404_embed)
            await log_traceback_to_channel(self.bot, error_channel_id, ctx, error)

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if not interaction.data or "custom_id" not in interaction.data:
            return

        if interaction.data["custom_id"] == "tickets":
            await interaction.response.send_message("Creating your ticket...", ephemeral=True)
            ticket = await create_ticket(interaction.user, f"ticket-{interaction.user.name}")
            await interaction.edit_original_response(
                content=f"Ticket created!\n**Click the link below to view your ticket.**\n<#{ticket.id}>"
            )

    async def on_invitation_message(self, message: discord.Message) -> None:
        if not message.author.bot:
            return
        if message.channel.id != staff_bridge_channel:
            return
        if not message.embeds:
            return
        embed = message.embeds[0]
        if not embed.description or "invited" not in embed.description.lower():
            return

        inviter, invitee = await extract_usernames(embed.description)
        if not all((inviter, invitee)):
            return

        return_message = await validate_invites(inviter, invitee)
        await message.channel.send(return_message)

    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.premium_since is None and after.premium_since is not None:
            await String(string="Server Booster").elite_member(is_automatic=True, discord_member=after)
            e = discord.Embed(
                title=f"{after.name} just boosted the server!",
                description="They have been added to the list of Elite Members",
                color=0xFFD700
            ).set_thumbnail(url=after.display_avatar.url)
            await self.bot.get_channel(log_channel_id).send(embed=e)

        elif before.premium_since is not None and after.premium_since is None:
            await String(string="Server Booster").elite_member(is_automatic=True, discord_member=after)
            e = discord.Embed(
                title=f"{after.name} just unboosted the server!",
                description="They have been removed from the list of Elite Members",
                color=0xFFD700
            ).set_thumbnail(url=after.display_avatar.url)
            await self.bot.get_channel(log_channel_id).send(embed=e)

    async def on_thread_create(self, thread: discord.Thread) -> None:
        if not thread.parent or thread.parent.id not in (qotd_thread_id, geoguessr_thread_id):
            return

        try:
            await thread.join()
        except discord.Forbidden:
            await self.bot.get_channel(error_channel_id).send(
                f"Missing permissions to join thread {thread.id} in forum {thread.parent.id}."
            )
            return
        except Exception as e:
            await self.bot.get_channel(error_channel_id).send(f"Error joining thread {thread.id}: {e!r}")
            return

        try:
            await send_thread_message(thread)
        except discord.Forbidden:
            await self.bot.get_channel(error_channel_id).send(
                f"Missing permissions to send message in thread {thread.id}."
            )
        except Exception as e:
            await self.bot.get_channel(error_channel_id).send(f"Error sending message in thread {thread.id}: {e!r}")
