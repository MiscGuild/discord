from __main__ import bot
import discord
from enum import Enum

# Colors
neg_color = 0xff3333
pos_color = 0x00A86B
neutral_color = 0x8368ff
error_color = 0xDE3163

# General embeds
registration_embed = discord.Embed(title="Welcome to the Miscellaneous Discord!",
                    description="Before you can view the server, please register with your Minecraft username.",
                    color=neutral_color)\
                        .add_field(name="To register use the following command:",
                                value=",register `Your Minecraft Name`\n\nExample:\n,register John",
                                inline=False)

staff_impersonation_embed = discord.Embed(title="Staff impersonation is a punishable offense!",
                                        color=neg_color)

async def get_requirements_embed(): return discord.Embed(title="Miscellaneous Guild Requirements", description="These requirements are subject to change!", color=neutral_color).add_field(
                                                name="Active",
                                                value=f"•  {format(bot.active_req, ',d')} Weekly Guild Experience",
                                                inline=False).add_field(name="DNKL Eligibility",
                                                value=f"•  {format(bot.dnkl_req, ',d')} Weekly Guild Experience",
                                                inline=False).add_field(name="Resident",
                                                value=f"•  {format(bot.resident_req, ',d')} Weekly Guild Experience",
                                                inline=False).add_field(name="Member",
                                                value=f"•  {format(bot.inactive, ',d')} Weekly Guild Experience",
                                                inline=False).add_field(name="New Member",
                                                value=f"•  {format(bot.new_member, ',d')} Daily Guild Experience",
                                                inline=False).set_footer(
                                                text="You are considered a New Member for the first 7 days after joining the guild"
                                                    "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")

# Errors
invalid_command_embed = discord.Embed(title=f"Invalid Command!",
                                    descrption="Use `,help` to view a list of all commands!",
                                    color=error_color)

not_owner_embed = discord.Embed(title=f"Your soul lacks the strength to utilize this command!",
                                description="You are not the owner of this bot!",
                                color=error_color)

missing_role_embed = discord.Embed(title=f"Your soul lacks the strength to utilize this command!",
                                description="You do not have the required roles to access this restricted command!",
                                color=error_color)

missing_permissions_embed = discord.Embed(title=f"Your soul lacks the strength to utilize this command!",
                                    description="You do not have the required permissions to access this restricted command!",
                                    color=error_color)

member_not_found_embed = discord.Embed(title=f"Member not found",
                                    description="This member doesn't seem to exist.\nCheck you have their ID or tag's capitalization and spelling correct!",
                                    color=error_color)

err_404_embed = discord.Embed(title="404 - Not Found",
                            description="The bot encountered an error 404 while performing this action!",
                            color=error_color)

bot_missing_perms_embed = discord.Embed(title="Missing permissions!",
                                        description="Due to the role hierarchy, the bot does not have the permission to do that!",
                                        color=error_color)

guildless_embed = discord.Embed(title="Guildless!", 
                                description="This player is not in a guild!",
                                color=error_color)

invalid_guild_embed = discord.Embed(title="Invalid guild!",
                                    description="This guild doesn't seem to exist!",
                                    color=error_color)

unknown_ign_embed = discord.Embed(title="Please enter a valid Minecraft username!",
                                color=error_color)

unknown_ign_msg = "Unknown IGN!"

invalid_date_msg = "This date is invalid! This date may not be within the last week. Enter dates in the form `YYYY/MM/DD`"

class ChatColor(Enum):
    RED = "&c"
    GOLD = "&6"
    GREEN = "&a"
    YELLOW = "&e"
    LIGHT_PURPLE = "&d"
    WHITE = "&f"
    BLUE = "&9"
    DARK_GREEN = "&2"
    DARK_RED = "&4"
    DARK_AQUA = "&3"
    DARK_PURPLE = "&5"
    DARK_GRAY = "&8"
    BLACK = "&0"
    DARK_BLUE = "&1"

months = {
    1: "January",
    2: "February", 
    3: "March", 
    4: "April",
    5: "May",
    6: "June", 
    7: "July", 
    8: "August", 
    9: "September",
    10: "October", 
    11: "November", 
    12: "December"
}
