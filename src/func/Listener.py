# The following file contains: on_member_join, on_error, on_command_error, reactionroles, tickets, on_interaction

import traceback
from __main__ import bot

import discord
from discord.ext import commands
from discord.ui import Button, Select, View

from src.utils.calculation_utils import extract_usernames
from src.utils.consts import (error_channel_id, invalid_command_embed,
                              member_not_found_embed, missing_permissions_embed, missing_role_embed,
                              neutral_color, not_owner_embed, pronoun_roles, staff_bridge_channel,
                              reaction_roles, registration_channel_id,
                              registration_embed, err_404_embed, bot_missing_perms_embed, tickets_embed)
from src.utils.discord_utils import create_ticket
from src.utils.referral_utils import validate_invites
from src.utils.request_utils import get_jpg_file


class Listener:
    def __init__(self, obj):
        self.obj = obj

    async def on_member_join(self) -> None:
        # Remove user's speaking perms and send info embed
        await self.obj.add_roles(bot.new_member_role)
        await bot.get_channel(registration_channel_id).send(embed=registration_embed)

    async def on_error(self) -> None:
        # Grabs the error being handled, formats it and sends it to the error channel
        tb = traceback.format_exc()
        await bot.get_channel(error_channel_id).send(f"Ignoring exception in event {self.obj}:\n```py\n{tb}\n```")

    async def on_command_error(self, ctx: discord.ApplicationContext) -> None | int:
        # Prevents commands with local handlers or cogs with overwrritten on_command_errors being handled here
        if isinstance(self.obj, commands.CommandNotFound):
            return await ctx.send(embed=invalid_command_embed)
        elif ctx.command.has_error_handler() or ctx.cog.has_error_handler():
            return None

        # Checks for the original exception raised and send to CommandInvokeError
        self.obj = getattr(self.obj, "original", self.obj)

        # Catch a series of common errors
        if isinstance(self.obj, commands.NotOwner):
            await ctx.respond(embed=not_owner_embed)
        elif isinstance(self.obj, commands.MissingRole):
            await ctx.respond(embed=missing_role_embed)
        elif isinstance(self.obj, commands.MissingPermissions):
            await ctx.respond(embed=missing_permissions_embed)
        elif isinstance(self.obj, discord.ext.commands.MissingAnyRole):
            await ctx.respond(embed=missing_permissions_embed)
        elif isinstance(self.obj, commands.MemberNotFound):
            await ctx.respond(embed=member_not_found_embed)
        elif isinstance(self.obj, discord.errors.Forbidden):
            await ctx.respond(embed=bot_missing_perms_embed)
        elif isinstance(self.obj, discord.errors.NotFound):
            await ctx.respond(embed=err_404_embed)
        elif isinstance(self.obj, commands.MissingRequiredArgument):
            usage = f"{ctx.prefix}{ctx.command.name}"
            for key, value in ctx.command.clean_params.items():
                if not value.default:
                    usage += " [" + key + "]"
                else:
                    usage += " <" + key + ">"
            embed = discord.Embed(title=f"Invalid Syntax",
                                  description=f"Command usage:\n`{usage}`\nFor more help, see `{ctx.prefix}help {ctx.command}`",
                                  color=0xDE3163)
            await ctx.send(embed=embed)

        # All other errors get sent to the error channel
        else:
            await ctx.respond(embed=err_404_embed)
            tb = "".join(traceback.format_exception(
                type(self.obj), self.obj, self.obj.__traceback__))
            if len(tb) <= 1955:
                await bot.get_channel(error_channel_id).send(
                    f"Ignoring exception in command {ctx.command}:\n```py\n{tb}\n```")

            else:
                await bot.get_channel(error_channel_id).send(
                    f"```An error occurred in command '{ctx.command}' that could not be sent in this channel, check the console for the traceback. \n\n'{self.obj}'```")
                print("The below exception could not be sent to the error channel:")
                print(tb)

    async def on_application_command_error(self, ctx: discord.ApplicationContext) -> None:
        if ctx.command.has_error_handler() or ctx.cog.has_error_handler():
            return

        # Checks for the original exception raised and send to CommandInvokeError
        self.obj = getattr(self.obj, "original", self.obj)

        # Catch a series of common application errors
        if isinstance(self.obj, commands.NotOwner):
            await ctx.respond(embed=not_owner_embed)
        elif isinstance(self.obj, commands.MissingRole):
            await ctx.respond(embed=missing_role_embed)
        elif isinstance(self.obj, commands.MissingPermissions):
            await ctx.respond(embed=missing_permissions_embed)
        elif isinstance(self.obj, discord.ext.commands.MissingAnyRole):
            await ctx.respond(embed=missing_permissions_embed)
        elif isinstance(self.obj, commands.MemberNotFound):
            await ctx.respond(embed=member_not_found_embed)
        elif isinstance(self.obj, discord.errors.Forbidden):
            await ctx.respond(embed=bot_missing_perms_embed)
        elif isinstance(self.obj, discord.errors.NotFound):
            await ctx.respond(embed=err_404_embed)
        elif isinstance(self.obj, commands.MissingRequiredArgument):
            usage = f"{ctx.prefix}{ctx.command.name}"
            for key, value in ctx.command.clean_params.items():
                if not value.default:
                    usage += " [" + key + "]"
                else:
                    usage += " <" + key + ">"
            embed = discord.Embed(title=f"Invalid Syntax",
                                  description=f"Command usage:\n`{usage}`\nFor more help, see `{ctx.prefix}help {ctx.command}`",
                                  color=0xDE3163)
            await ctx.send(embed=embed)

        # All other errors get sent to the error channel
        else:
            tb = "".join(traceback.format_exception(
                type(self.obj), self.obj, self.obj.__traceback__))
            if len(tb) <= 1955:
                await bot.get_channel(error_channel_id).send(
                    f"Ignoring exception in command {ctx.command}:\n```py\n{tb}\n```")

            else:
                await bot.get_channel(error_channel_id).send(
                    f"```An error occurred in command '{ctx.command}' that could not be sent in this channel, check the console for the traceback. \n\n'{self.obj}'```")
                print("The below exception could not be sent to the error channel:")
                print(tb)

    async def on_interaction(self) -> None:
        self.obj: discord.Interaction
        if "custom_id" not in self.obj.data:
            pass
        elif self.obj.data["custom_id"] == "tickets":
            await self.obj.response.send_message("Creating your ticket...", ephemeral=True)
            ticket = await create_ticket(self.obj.user, f"ticket-{self.obj.user.name}")

            await self.obj.edit_original_response(
                content=f"Ticket created!\n**Click the link below to view your ticket.**\n<#{ticket.id}>")

        # Reaction roles
        elif self.obj.data["custom_id"] in reaction_roles.keys():
            role = discord.utils.get(
                self.obj.guild.roles, name=self.obj.data["custom_id"])
            if role in self.obj.user.roles:
                await self.obj.user.remove_roles(role)
                await self.obj.response.send_message(f"Removed {role.name} role from you.", ephemeral=True)
            else:
                await self.obj.user.add_roles(role)
                await self.obj.response.send_message(f"Added {role.name} role to you.", ephemeral=True)

        # Pronouns
        elif self.obj.data["custom_id"] == "pronouns":
            label = self.obj.data["values"][0] if self.obj.data["values"] else None
            await self.obj.user.remove_roles(
                *[discord.utils.get(self.obj.guild.roles, name=k) for k in pronoun_roles.keys()])

            # User selected none, remove all roles
            if not label:
                await self.obj.response.send_message(content=f"Removed all pronoun roles!")
            else:
                # Fetch role
                role = discord.utils.get(self.obj.guild.roles, name=label)
                # Remove single role if user already has it
                if role in self.obj.user.roles:
                    await self.obj.response.send_message(content=f"Removed {label}", ephemeral=True)
                # Add the clicked role and remove all others
                else:
                    await self.obj.user.add_roles(role)
                    await self.obj.response.send_message(content=f"Added {label}", ephemeral=True)

    async def reactionroles(ctx: discord.ApplicationContext) -> tuple[list, list]:
        # Reaction roles
        reaction_roles_embed = discord.Embed(title="To get your desired role, click its respective button!",
                                             description="🪓 __**SkyBlock**__\nGives you the access to the SkyBlock category!\n\n"
                                                         "🕹 __**Minigames**__\nAllows you to play some Discord minigames!\n\n"
                                                         "❓  __**QOTD Ping**__\nThe staff team will mention this role when there's a new question of the day!\n\n"
                                                         "🎉 __**Giveaways/Events**__\nReact so you don't miss any giveaway or event\n\n"
                                                         "📖 __**Storytime Pings**__\nGet pinged whenever a storytime happens",
                                             color=neutral_color)

        class ReactionRoleButton(Button):
            def __init__(self, label: str, emoji: str):
                super().__init__(label=label, custom_id=label, emoji=emoji)

        class ReactionRolesView(View):
            def __init__(self):
                super().__init__()

                # Add all buttons
                for k, v, in reaction_roles.items():
                    self.add_item(ReactionRoleButton(k, v))

        # Pronouns
        pronouns_embed = discord.Embed(title="Please select your pronouns",
                                       description="".join(
                                           [k + v + "\n" for k, v in pronoun_roles.items()]),
                                       color=neutral_color)

        class PronounsSelect(Select):
            def __init__(self):
                options = [discord.SelectOption(
                    label=k, emoji=v) for k, v in pronoun_roles.items()]
                super().__init__(placeholder="Select your pronouns (Max 1)",
                                 min_values=0, max_values=1, options=options, custom_id="pronouns")

        pronouns_view = View(timeout=10.0)
        pronouns_view.add_item(PronounsSelect())

        return [reaction_roles_embed, ReactionRolesView()], [pronouns_embed, pronouns_view]

    async def tickets(ctx) -> tuple[discord.File, discord.Embed, any]:
        image = await get_jpg_file(
            "https://media.discordapp.net/attachments/650248396480970782/873866686049189898/tickets.jpg")

        class TicketView(View):
            def __init__(self):
                super().__init__()
                self.add_item(Button(label="Create Ticket", custom_id="tickets",
                                     style=discord.ButtonStyle.blurple, emoji="✉️"))

        return image, tickets_embed, TicketView()

    async def on_invitation_message(self) -> None:
        if not self.obj.author.bot:
            return
        if self.obj.channel.id != staff_bridge_channel:
            return
        if not self.obj.embeds:
            return

        embed = self.obj.embeds[0]

        if not embed.description:
            return

        if "invited" not in embed.description.lower():
            return

        description = embed.description

        inviter, invitee = await extract_usernames(description)

        if not all((inviter, invitee)):
            return

        return_message = await validate_invites(inviter, invitee)

        await self.obj.channel.send(return_message)
