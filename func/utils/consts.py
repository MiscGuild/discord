from enum import Enum

import discord
import toml

# Define config
config = toml.load("config.toml")

# Gexp requirements
new_member_req = config["new_member_req"]
member_req = config["member_req"]
resident_req = config["resident_req"]
active_req = config["active_req"]
dnkl_req = config["dnkl_req"]

# GvG team requirements
gvg_requirements = {
    "bw_fkdr":  config["gvg_bw_fkdr"],
    "bw_wins":  config["gvg_bw_wins"],
    "sw_kdr": config["gvg_sw_kdr"],
    "sw_wins": config["gvg_sw_wins"],
    "duels_kills": config["gvg_duels_kills"],
    "duels_wlr": config["gvg_duels_wlr"],
}

# Define channels
error_channel_id = config["error_channel"]
dnkl_channel_id = config["dnkl_channel"]
ticket_channel_id = config["ticket_channel"]
log_channel_id = config["log_channel"]
registration_channel_id = config["registration_channel"]
staff_announcements_id = config["staff_announcements_channel"]
partner_channel_id = config["partner_channel"]
qotd_channel_id = config["qotd_channel"]
qotd_ans_channel_id = config["qotd_ans_channel"]
milestones_channel = config["milestones_channel"]

# Other variables
guild_handle = config["guild_handle"]
ticket_categories = config["ticket_categories"]
allies = config["allies"]
milestones_category = config['milestones_category']

# Colors
neg_color = 0xff3333
pos_color = 0x00A86B
neutral_color = 0x8368ff
error_color = 0xDE3163

# Pronoun roles
reaction_roles = {
    "Skyblock": "🪓",
    "Minigames": "🕹",
    "QOTD Ping": "❓",
    "Giveaways/Events": "🎉",
    "Storytimes": "📖",
}

pronoun_roles = {
    "He/Him": "👨",
    "She/Her": "👩",
    "They/Them": "🏳️‍🌈",
    "Other": "❓",
}

milestone_emojis = {
    "Hypixel": "<:hypixel:823036946984730662>",
    "Bedwars": "<:BedWars64:823036962150547477>",
    "Skywars": "<:Skywars:823036980526972948>",
    "Duels": "<:Duels:823036885089255434>",
    "Skyblock": "<:sb:732824932177805405>",
    "Build Battle": "<:buildbattle:828113746978406481>",
    "Arcade": "<:arcade:825723888477929472>",
    "Turbo Kart Racers": "<:TurboKartRacers64:846306861950304267>",
    "Pit": "<:pit:851361342744690728>",
    "Murder Mystery": "<:MurderMystery64:823036899974447105>",
    "Miscellaneous": "<:Misc:540990817872117780>",
    "Discord": "<:discord:977349801412788266>",
    "Other": "❓"
}

# General embeds
registration_embed = discord.Embed(title=f"Welcome to the {guild_handle} Discord!",
                    description="Before you can view the server, please register with your Minecraft username.",
                    color=neutral_color).add_field(name="To register use the following command:",
                                                    value=",register `Your Minecraft Name`\n\nExample:\n,register John",
                                                    inline=False)

staff_impersonation_embed = discord.Embed(title="Staff impersonation is a punishable offense!",
                                        color=neg_color)

accepted_staff_application_embed = discord.Embed(title="Congratulations, your staff application has been accepted!",
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

gvg_info_embed = discord.Embed(title="GvG Information", 
                                description="Following is some general information and the requiurements for the GvG team.",
                                color=neutral_color).add_field(
                                    name="Information",
                                    value="In a GvG (Guild vs Guild), players are organised by guild and play various gamemodes. The guild that wins the most games wins the GvG.",
                                    inline=False
                                ).add_field(
                                    name="Requirements",
                                    value=f"""Bedwars Wins: `{gvg_requirements["bw_wins"]}`
                                            Bedwars FKDR: `{gvg_requirements["bw_fkdr"]}`
                                            Skywars Wins: `{gvg_requirements["sw_wins"]}`
                                            Skywars KDR: `{gvg_requirements["sw_kdr"]}`
                                            Duels WLR: `{gvg_requirements["duels_wlr"]}`
                                            Duels Kills: `{gvg_requirements["duels_kills"]}`""",
                                    inline=False
                                )

# Errors
unknown_ign_msg = "Unknown IGN!"

invalid_date_msg = "This date is invalid! You have entered a date that has already passed!\n Enter dates in the form `YYYY/MM/DD`"

missing_permissions_msg = "Your soul lacks the strength to utilize this command!"

invalid_command_embed = discord.Embed(title="Invalid Command!",
                                    description="Use `,help` to view a list of all commands!",
                                    color=error_color)

not_owner_embed = discord.Embed(title=missing_permissions_msg,
                                description="You are not the owner of this bot!",
                                color=error_color)

missing_role_embed = discord.Embed(title=missing_permissions_msg,
                                description="You do not have the required roles to access this restricted command!",
                                color=error_color)

missing_permissions_embed = discord.Embed(title=missing_permissions_msg,
                                    description="You do not have the required permissions to access this restricted command!",
                                    color=error_color)

member_not_found_embed = discord.Embed(title="Member not found",
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

discord_not_linked_embed = discord.Embed(title="This account is not linked to your discord account!",
                                        description="Please follow the following steps to link your Hypixel profile with discord:\nGo to 'Your Profile' > Social Media > DISCORD and paste your discord info.",
                                        color=error_color)
discord_not_linked_embed.set_image(url="https://media.discordapp.net/attachments/796061149593731128/953770877395284008/osl_.gif")

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

staff_application_questions = {
    1: "What is your age?",
    2: "How long have you been in the guild for?",
    3: "Have you had any past infractions on Hypixel?",
    4: "Why have you decided to apply for staff?",
    5: "What has brought you to Miscellaneous, and what has kept you here?",
    6: "What is something you could suggest that would improve the guild?",
    7: "You have just started as a helper and a moderator starts arguing with another member. This argument starts to get serious quite quickly. What do you do?",
    8: "Suppose it's your first week of being a helper and you guild-mute a well-known player. Your guildmates start spamming you calling you a bad moderator and telling you to unmute them. What would you do?",
    9: "Upon joining a game and you discover that a guild member is in your game and is hacking. What do you do?",
    10: "Have you been staff in any other guild or on any server? If yes, which one?",
    11: "How much time do you have to contribute to the role? (Per day)",
    12: "Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?",
    13: "Anything else you would us to know?"
}
