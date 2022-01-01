# The following file contains: on_member_join, on_error, on_command_error, on_button_click, on_select_option, on_guild_channel_create

from __main__ import bot

from discord.ext import commands
import discord
import traceback

from func.utils.consts import registration_embed, not_owner_embed, missing_role_embed, missing_permissions_embed, member_not_found_embed

class Listener:
    def __init__(self, res):
        self.obj = res

    async def on_member_join(member):
        # Remove user's speaking perms and send info embed
        await member.add_roles(bot.new_member_role)
        await bot.registration_channel.send(embed=registration_embed)

    async def on_error(event):
        # Grabs the error being handled, formats it and sends it to the error channel
        tb = traceback.format_exc()
        await bot.error_channel.send(f"Ignoring exception in event {event}:\n```py\n{tb}\n```")

    async def on_command_error(ctx, error):
        # Prevents commands with local handlers or cogs with overwrritten on_command_errors being handled here
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(title=f"Invalid Command!",
                                descrption="Use `,help` to view a list of all commands!", color=0xDE3163)
            await ctx.send(embed=embed)
            return
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
                await bot.error_channel.send(f"Ignoring exception in command {ctx.command}:\n```py\n{tb}\n```")
            else:
                await bot.error_channel.send(
                    f"```An error occurred in command '{ctx.command}' that could not be sent in this channel, check the console for the traceback. \n\n'{error}'```")
                print("The below exception could not be sent to the error channel:")
                print(tb)

    # async def on_button_click():

    # async def on_select_option():

    # async def on_guild_channel_create():
