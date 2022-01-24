# The following file contains: on_member_join, on_error, on_command_error, on_select_option, on_guild_channel_create

from __main__ import bot
from time import time
import discord
from discord.ext import commands
from discord.ui import View, Select
import traceback

from func.utils.consts import neutral_color, registration_channel_id, error_channel_id, invalid_command_embed, registration_embed, not_owner_embed, missing_role_embed, missing_permissions_embed, member_not_found_embed


class Listener:
    def __init__(self, res):
        self.obj = res

    async def on_member_join(member):
        # Remove user's speaking perms and send info embed
        await member.add_roles(bot.new_member_role)
        await bot.get_channel(registration_channel_id).send(embed=registration_embed)

    async def on_error(event):
        # Grabs the error being handled, formats it and sends it to the error channel
        tb = traceback.format_exc()
        await bot.get_channel(error_channel_id).send(f"Ignoring exception in event {event}:\n```py\n{tb}\n```")

    async def on_command_error(ctx, error):
        # Prevents commands with local handlers or cogs with overwrritten on_command_errors being handled here
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(embed=invalid_command_embed)
        elif ctx.command.has_error_handler() or ctx.cog.has_error_handler():
            return

        # Checks for the original exception raised and send to CommandInvokeError
        error = getattr(error, "original", error)

        # Catch a series of common errors
        if isinstance(error, commands.NotOwner):
            await ctx.send(embed=not_owner_embed)
        elif isinstance(error, commands.MissingRole):
            await ctx.send(embed=missing_role_embed)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=missing_permissions_embed)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=member_not_found_embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            usage = f"{ctx.prefix}{ctx.command.name}"
            for key, value in ctx.command.clean_params.items():
                if not value.default:
                    usage += " [" + key + "]"
                else:
                    usage += " <" + key + ">"
            embed = discord.Embed(title=f" arguments",
                                description=f"Command usage:\n`{usage}`\nFor more help, see `{ctx.prefix}help {ctx.command}`",
                                color=0xDE3163)
            await ctx.send(embed=embed)

        # All other errors get sent to the error channel
        else:
            tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            if len(tb) <= 2000:
                await bot.get_channel(error_channel_id).send(f"Ignoring exception in command {ctx.command}:\n```py\n{tb}\n```")
            else:
                await bot.error_channel.send(
                    f"```An error occurred in command '{ctx.command}' that could not be sent in this channel, check the console for the traceback. \n\n'{error}'```")
                print("The below exception could not be sent to the error channel:")
                print(tb)

    # async def on_select_option():

    # async def on_guild_channel_create():

    async def reactionroles():
        # Reaction roles
        reaction_roles_embed = discord.Embed(title="To get your desired role, click its respective button!",
                                    description="🪓 __**SkyBlock**__\nGives you the access to the SkyBlock category!\n\n"
                                                "🕹 __**Discord Minigames**__\nAllows you to play some Discord minigames!\n\n"
                                                "❓  __**QOTD Ping**__\nThe staff team will mention this role when there's a new question of the day!\n\n"
                                                "🎉 __**Giveaways/Events**__\nReact so you don't miss any giveaway or event\n\n"
                                                "📖 __**Storytimes**__\nGet pinged whenever a storytime happens",
                                    color=neutral_color)

        class ReactionRolesView(View):
            @discord.ui.button(label="Skyblock", emoji="🪓")
            async def skyblock_callback(self, button, interaction):
                return True

            @discord.ui.button(label="Discord Minigames", emoji="🕹")
            async def minigames_callback(self, button, interaction):
                return True

            @discord.ui.button(label="QOTD Ping", emoji="❓")
            async def qotd_callback(self, button, interaction):
                return True

            @discord.ui.button(label="Giveaways/Events", emoji="🎉")
            async def events_callback(self, button, interaction):
                return True

            @discord.ui.button(label="Storytimes", emoji="📖")
            async def storytime_callback(self, button, interaction):
                return True

        # Pronouns
        pronouns_embed = discord.Embed(title="Please select your pronouns",
                                        description="👨 He/Him"
                                                    "\n👩 She/Her"
                                                    "\n🏳‍🌈 They/Them"
                                                    "\n❓ Other",
                                        color=neutral_color)

        class PronounsSelect(Select):
            def __init__(self):
                super().__init__(placeholder="Select your pronouns (Max 1)", min_values=1, max_values=1, options=[
                    discord.SelectOption(label="He/Him", value="849830869036040212", emoji="👨"),
                    discord.SelectOption(label="She/Her", value="849830936434704404", emoji="👩"),
                    discord.SelectOption(label="They/Them", value="849831004310077441", emoji="🏳️‍🌈"),
                    discord.SelectOption(label="Other", value="855598846843551744", emoji="❓"),
                ])

            async def callback(self, interaction: discord.Interaction):
                return True

        pronouns_view = View(timeout=10.0)
        pronouns_view.add_item(PronounsSelect())

        return [reaction_roles_embed, ReactionRolesView()], [pronouns_embed, pronouns_view]
