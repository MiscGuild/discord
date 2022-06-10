# The following file contains: on_member_join, on_error, on_command_error, reactionroles, tickets, on_interaction

import traceback
from __main__ import bot

import discord
from discord.ext import commands
from discord.ui import Button, Select, View

from func.utils.consts import (error_channel_id, invalid_command_embed,
                               member_not_found_embed,
                               missing_permissions_embed, missing_role_embed,
                               neutral_color, not_owner_embed, pronoun_roles,
                               reaction_roles, registration_channel_id,
                               registration_embed)
from func.classes.Union import Union
from func.utils.discord_utils import create_ticket
from func.utils.request_utils import get_jpg_file


class Listener:
    def __init__(self, obj):
        self.obj = obj

    async def on_member_join(self):
        # Remove user's speaking perms and send info embed
        await self.obj.add_roles(bot.new_member_role)
        await bot.get_channel(registration_channel_id).send(embed=registration_embed)

    async def on_error(self):
        # Grabs the error being handled, formats it and sends it to the error channel
        tb = traceback.format_exc()
        await bot.get_channel(error_channel_id).send(f"Ignoring exception in event {self.obj}:\n```py\n{tb}\n```")

    async def on_command_error(self, ctx):
        # Prevents commands with local handlers or cogs with overwrritten on_command_errors being handled here
        if isinstance(self.obj, commands.CommandNotFound):
            return await ctx.send(embed=invalid_command_embed)
        elif ctx.command.has_error_handler() or ctx.cog.has_error_handler():
            return

        # Checks for the original exception raised and send to CommandInvokeError
        self.obj = getattr(self.obj, "original", self.obj)

        # Catch a series of common errors
        if isinstance(self.obj, commands.NotOwner):
            await ctx.send(embed=not_owner_embed)
        elif isinstance(self.obj, commands.MissingRole):
            await ctx.send(embed=missing_role_embed)
        elif isinstance(self.obj, commands.MissingPermissions):
            await ctx.send(embed=missing_permissions_embed)
        elif isinstance(self.obj, commands.MissingAnyRole):
            await ctx.send(embed=missing_permissions_embed)
        elif isinstance(self.obj, commands.MemberNotFound):
            await ctx.send(embed=member_not_found_embed)
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

    async def reactionroles(ctx):
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

    async def tickets(ctx):
        embed = discord.Embed(title="Tickets",
                              description="""Tickets can be created for any of the following reasons:
                                        > Player Report
                                        > Problems/Queries
                                        > Milestone
                                        > Do-not-kick-list Application
                                        > Staff Application
                                        > GvG Team Application
                                        > Event (When applicable)
                                        > Other
                                        Once you have created a ticket by clicking the button, you will be linked to your ticket\n
                                        The bot will ask you to choose the reason behind the creation of your ticket from a given list. Choose the appropriate reason and then proceed!\n
                                        Once you have created your ticket, staff will respond within 24 hours.""",
                              color=neutral_color)
        embed.add_field(name="Do-not-kick-list Application",
                        value="You  must have a valid reason for applying and also meet the DNKL requiremnets.\n"
                              "Accepted Reasons:\n"
                              "> School\n"
                              "> Medical Reasons\n"
                              "> Situations out of your control\n"
                              "> Vacation\n\n"
                              "If your account is banned, it may be temporarily kicked until unbanned.",
                        inline=False)
        embed.add_field(name="Player Report",
                        value="When reporting a player, you're expected to explain the situation in maximum detail. Providing the following is considered the bare minimum:\n"
                              "> Username of the accused\n"
                              "> Explanantion of the offense\n"
                              "> Time of offense\n"
                              "> Proof of offense\n"
                              "If you wish to report a staff member, please DM the acting guild master with your report.",
                        inline=False)
        embed.add_field(name="Milestone",
                        value="You'll be prompted to present the milestone you've achieved and proof of its occurence. "
                              "Staff will review your milestone and if accepted, will be include it in the next week's milestone post!",
                        inline=False)
        embed.add_field(name="Staff Application",
                        value="After you're done with your application, the staff team will review your it and make a decision to accept or deny it.",
                        inline=False)
        embed.set_thumbnail(
            url=f"https://images-ext-1.discordapp.net/external/ziYSZZe7dPyKDYLxA1s2jqpKi-kdCvPFpPaz3zft-wo/%3Fwidth%3D671%26height%3D671/https/media.discordapp.net/attachments/523227151240134664/803843877999607818/misc.png")

        image = await get_jpg_file(
            "https://media.discordapp.net/attachments/650248396480970782/873866686049189898/tickets.jpg")

        class TicketView(View):
            def __init__(self):
                super().__init__()
                self.add_item(Button(label="Create Ticket", custom_id="tickets",
                                     style=discord.ButtonStyle.blurple, emoji="✉️"))

        return image, embed, TicketView()

    async def on_interaction(self):
        self.obj: discord.Interaction
        # Ticket creation
        if self.obj.data["custom_id"] == "tickets":
            await Union(user=self.obj.user).sync(None, self.obj.user.nick, None, True)
            ticket = await create_ticket(self.obj.user, f"ticket-{self.obj.user.name}")
            await self.obj.response.send_message(f"Click the following link to go to your ticket! <#{ticket.id}>",
                                                 ephemeral=True)

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
