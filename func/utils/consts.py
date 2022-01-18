import discord
from enum import Enum
import toml

# Define config
config = toml.load("config.toml")

# Requirements
new_member_req = config["new_member_req"]
member_req = config["member_req"]
resident_req = config["resident_req"]
active_req = config["active_req"]
dnkl_req = config["dnkl_req"]

# Other variables
guild_handle = config["guild_handle"]
ticket_categories = config["ticket_categories"]
allies = config["allies"]

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

accepted_staff_application_embed = discord.Embed(title=f"Congratulations, your staff application has been accepted!",
                                                description="Please view `https://bit.ly/MiscStaffGuide` and the `#staff-faq` channel to help you get started!",
                                                color=neutral_color)

requirements_embed = discord.Embed(title="Miscellaneous Guild Requirements", description="These requirements are subject to change!", color=neutral_color).add_field(
                                                name="New Member",
                                                value=f"•  {format(new_member_req, ',d')} Daily Guild Experience",
                                                inline=False).add_field(name="Member",
                                                value=f"•  {format(member_req, ',d')} Weekly Guild Experience",
                                                inline=False).add_field(name="Resident",
                                                value=f"•  {format(resident_req, ',d')} Weekly Guild Experience",
                                                inline=False).add_field(
                                                name="Active",
                                                value=f"•  {format(active_req, ',d')} Weekly Guild Experience",
                                                inline=False).add_field(name="Do-not-kick-list Eligibility",
                                                value=f"•  {format(dnkl_req, ',d')} Weekly Guild Experience",
                                                inline=False).set_footer(
                                                text="You are considered a New Member for the first 7 days after joining the guild"
                                                    "\nIf you fail to meet these requirements, you will be kicked!")

resident_embed = discord.Embed(title="How can I get Resident?",
                                description="To be eligible for Resident, you must be satisfy at least one of the following requirements:", color=neutral_color).add_field(name="Youtuber",
                                value="If you're a youtuber with more than 5,000 subscribers, you aren't subject to any guild requirements.",
                                inline=False).add_field(name="Rich Kid", value="Spend Money on the guild by doing giveaways and or sponsoring events!",
                                inline=False).add_field(name="Server Booster", value="Boost the guild discord!",
                                inline=False).add_field(name="GvG Team", value="Be an exceptional GvG player.",
                                inline=False).set_footer(
                                text=f"Unless otherwise specified, all residents must get {format(resident_req, ',d')} weekly guild experience.")

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
