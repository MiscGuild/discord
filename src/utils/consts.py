from enum import Enum

import discord
import toml

# Define config
config = toml.load("config.toml")

# Gexp requirements
member_req = config["member_req"]
resident_req = config["resident_req"]
active_req = config["active_req"]
dnkl_req = config["dnkl_req"]

# GvG team requirements
gvg_requirements = {
    "bw_fkdr": config["gvg_bw_fkdr"],
    "bw_wins": config["gvg_bw_wins"],
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
weekly_lb_channel = config["weekly_gexp_lb"]
daily_lb_channel = config["daily_gexp_lb"]
rank_upgrade_channel = config["rank_upgrade_channel"]
staff_bridge_channel = config["staff_bridge_channel"]

# Other variables
guild_handle = config["guild_handle"]
ticket_categories = config["ticket_categories"]
allies = config["allies"]

# Colors
neg_color = 0xff3333
pos_color = 0x00A86B
neutral_color = 0x8369ff
error_color = 0xDE3163

# Pronoun roles
reaction_roles = {
    "Skyblock": "🪓",
    "Minigames": "🕹",
    "QOTD Ping": "❓",
    "Giveaways/Events": "🎉",
    "Geoguessr": "🌏",
}

pronoun_roles = {
    "He/Him": "👨",
    "She/Her": "👩",
    "They/Them": "🏳️‍🌈",
    "Other": "❓",
}

milestone_categories = {
    "hypixel": "Hypixel",
    "bedwars": "BedWars",
    "skywars": "SkyWars",
    "duels": "Duels",
    "skyblock": "SkyBlock",
    "build_battle": "Build Battle",
    "arcade": "Arcade",
    "turbo_kart_racers": "Turbo Kart Racers",
    "pit": "The Pit",
    "murder_mystery": "Murder Mystery",
    "copsvcrims": "Cops and Crims",
    "miscellaneous": "Miscellaneous",
    "discord": "Discord",
    "other": "Other"
}

milestone_emojis = {
    "hypixel": "<:hypixel:823036946984730662>",
    "bedwars": "<:BedWars64:823036962150547477>",
    "skywars": "<:Skywars:823036980526972948>",
    "duels": "<:Duels:823036885089255434>",
    "skyblock": "<:sb:732824932177805405>",
    "build_battle": "<:buildbattle:828113746978406481>",
    "arcade": "<:arcade:825723888477929472>",
    "turbo_kart_racers": "<:TurboKartRacers64:846306861950304267>",
    "pit": "<:pit:851361342744690728>",
    "murder_mystery": "<:MurderMystery64:823036899974447105>",
    "copsvcrims": "<:CVC64:846306846717378560>",
    "miscellaneous": "<:Misc:540990817872117780>",
    "discord": "<:discord:977349801412788266>",
    "other": "❓"
}

elite_member_categories = ("Event Sponsor", "GvG Team", "YouTuber", "Other")

# General embeds
registration_embed = discord.Embed(title=f"Welcome to the {guild_handle} Discord!",
                                   description="Before you can view the server, please register with your Minecraft username.",
                                   color=neutral_color).add_field(name="To register use the following command:",
                                                                  value="/register `Your Minecraft Name`\n\nExample:\n/register John",
                                                                  inline=False)

ticket_deleted_embed = discord.Embed(title="Your ticket was deleted!",
                                     description="The file above is the transcript",
                                     color=neutral_color).set_footer(
    text="If your issue was not resolved, please make a new ticket!")

staff_impersonation_embed = discord.Embed(title="Staff impersonation is a punishable offense!",
                                          color=neg_color)

accepted_staff_application_embed = discord.Embed(title="Congratulations, your staff application has been accepted!",
                                                 description="Please view `https://bit.ly/MiscStaffGuide` and the `#staff-faq` channel to help you get started!",
                                                 color=neutral_color)

requirements_embed = discord.Embed(title="Miscellaneous Guild Requirements",
                                   description="These requirements are subject to change!",
                                   color=neutral_color).add_field(
    name="Active",
    value=f"•  {format(active_req, ',d')} Weekly Guild Experience",
    inline=False).add_field(name="Member",
                            value=f"•  {format(member_req, ',d')} Weekly Guild Experience",
                            inline=False).add_field(name="Resident",
                                                    value=f"•  {format(resident_req, ',d')} Weekly Guild Experience",
                                                    inline=False).add_field(name="Do-not-kick-list Eligibility",
                                                                            value=f"•  {format(dnkl_req, ',d')} Weekly Guild Experience",
                                                                            inline=False).set_footer(
    text="If you fail to meet these requirements, you will be kicked!")

dnkl_entries_not_found = discord.Embed(title="No entries!",
                                       description="There are no users on the do-not-kick-list!",
                                       color=neg_color)

information_embed = discord.Embed(title="Miscellaneous", url="https://plancke.io/hypixel/guild/name/Miscellaneous",
                                  description="Miscellaneous is an all games Hypixel guild. "
                                              "Our primary goal is to be a guild that is friendly to everyone. "
                                              "All of our guild requirements are well thought out. "
                                              "Miscellaneous strives to be a good community while maintaining its position on the guild leaderboards. "
                                              "We were founded in 2014 by Fantastic_Doge making us one of the oldest guilds on the Hypixel Network. "
                                              "We, the miscellaneous staff team will do anything to protect the legacy of this spectacle of a guild.",
                                  color=neutral_color).add_field(name="Partners",
                                                                 value="XL - https://discord.gg/XvqCvYn\n"
                                                                       "Lucid - https://discord.gg/DDTMad2pYR\n"
                                                                       "OUT - https://discord.gg/td75grErXq\n"
                                                                       "Betrayed - https://discord.gg/kcJkAr2tW2\n"
                                                                       "Blight - https://discord.gg/dgTWpgy\n"
                                                                       "The Happy Pixels - https://discord.gg/JVTqPr9t\n"
                                                                       "FireTree V2 - https://discord.gg/UcrACnWTpE\n"
                                                                       "High Altitude - https://discord.gg/highaltitude\n"
                                                                       "Alpha Project - https://discord.gg/cN6fSAErtz\n"
                                                                       "Cubelify - https://cubelify.com/ / https://discord.gg/cubelify",
                                                                 inline=False).add_field(
    name="Useful Resources",
    value="Guild Thread: https://bit.ly/MiscThread\n"
          "Discord: https://discord.gg/bHFWukp",
    inline=False).add_field(name="Requirements",
                            value="__**Active**__\n"
                                  f"➤ {format(active_req, ',d')} Weekly Guild Experience\n"
                                  "__**Member**__\n"
                                  f"➤ {format(member_req, ',d')} Weekly Guild Experience\n"
                                  f"__**Resident**__\n"
                                  f"➤ {format(resident_req, ',d')} Weekly Guild Experience\n",
                            inline=False).set_thumbnail(
    url="https://images-ext-2.discordapp.net/external/c1AaQE93xCcn0mQDOLY1-d14TTEVIOg78IRhqaAnk1I/https/images-ext-1.discordapp.net/external/rey4uPv9eHzVTkM9_GVWvWiK1jyrtBy_sUQjBaE5qbE/"
        "https/images-ext-2.discordapp.net/external/oTPK3H5eQJWBw_syuTTVUJ3yP7YkvvXTb0JbMX0cdJQ/https/"
        "images-ext-1.discordapp.net/external/ziYSZZe7dPyKDYLxA1s2jqpKi-kdCvPFpPaz3zft-wo/"
        "%2525253Fwidth%2525253D671%25252526height%2525253D671/https/media.discordapp.net/"
        "attachments/523227151240134664/803843877999607818/misc.png").set_footer(
    text="If you have any queries, kindly make a ticket!")

tickets_embed = discord.Embed(title="Tickets",
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
                              color=neutral_color).add_field(name="Do-not-kick-list Application",
                                                             value="You must have a valid reason for applying and also meet the DNKL requirements.\n"
                                                                   "Accepted Reasons:\n"
                                                                   "> Exams\n"
                                                                   "> Medical Reasons\n"
                                                                   "> Computer Problems\n"
                                                                   "> Vacation\n"
                                                                   "> Other (subject to staff judgment)\n"
                                                                   "If your account is banned, it may be temporarily kicked until unbanned.",
                                                             inline=False).add_field(name="Player Report",
                                                                                     value="When reporting a player, you're expected to explain the situation in maximum detail. Providing the following is considered the bare minimum:\n"
                                                                                           "> Username of the accused\n"
                                                                                           "> Explanantion of the offense\n"
                                                                                           "> Time of offense\n"
                                                                                           "> Proof of offense\n"
                                                                                           "If you wish to report a staff member, please DM the acting guild master with your report.",
                                                                                     inline=False).add_field(
    name="Milestone",
    value="You'll be prompted to present the milestone you've achieved and proof of its occurence. "
          "Staff will review your milestone and if accepted, will be include it in the next week's milestone post!",
    inline=False).add_field(name="Staff Application",
                            value="After you're done with your application, the staff team will review your it and make a decision to accept or deny it.",
                            inline=False).set_thumbnail(
    url=f"https://images-ext-1.discordapp.net/external/ziYSZZe7dPyKDYLxA1s2jqpKi-kdCvPFpPaz3zft-wo/%3Fwidth%3D671%26height%3D671/https/media.discordapp.net/attachments/523227151240134664/803843877999607818/misc.png")

resident_embed = discord.Embed(title="How can I get Resident?",
                               description="To be eligible for Resident, you must be satisfy at least one of the following requirements:",
                               color=neutral_color).add_field(name="Youtuber",
                                                              value="If you're a youtuber with more than 5,000 subscribers, you aren't subject to any guild requirements.",
                                                              inline=False).add_field(name="Rich Kid",
                                                                                      value="Spend Money on the guild by doing giveaways and or sponsoring events!",
                                                                                      inline=False).add_field(
    name="Server Booster", value="Boost the guild discord!",
    inline=False).add_field(name="GvG Team", value="Be an exceptional GvG player.",
                            inline=False).set_footer(
    text=f"Unless otherwise specified, all residents must get {format(resident_req, ',d')} weekly guild experience.")

gvg_info_embed = discord.Embed(title="GvG Information",
                               description="Following is some general information and the requirements for the GvG team.",
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

positive_responses = (
    "yes", "yeah", "yup", "yea", "sure", "ok", "okay", "affirmative", "y", "ye", "yea", "yep", "yuppers", "yessir",
    "yessum", "yessirree", "yessumree", "yessiree", "yessumree")

# Errors
unknown_ign_msg = "Unknown IGN!"

invalid_date_msg = "This date is invalid!\n*Enter dates in the format* **YYYY/MM/DD**\n\n For example,\n" \
                   "January 23rd 2022 would be 2022/01/23"

missing_permissions_msg = "Your soul lacks the strength to utilize this feature!"

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
                                        description="Due to the role hierarchy, I do not have the permission to do that!",
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
                                         description="Please follow the following steps to link your Hypixel profile with discord:\nGo to 'Your Profile' > Social Media > DISCORD",
                                         color=error_color)
join_request_embed = discord.Embed(color=neutral_color).add_field(name="Our requirements are as follows:",
                                                                  value="__Active__\n"
                                                                        f"➤ {format(active_req, ',d')} Weekly Guild Experience\n"
                                                                        "__Member__\n"
                                                                        f"➤ {format(member_req, ',d')} Weekly Guild Experience\n"
                                                                        f"__Resident__\n"
                                                                        f"➤ {format(resident_req, ',d')} Weekly Guild Experience\n\n"
                                                                        f"You will join the guild as a Member.\n\n",
                                                                  inline=False).set_footer(
    text="Staff should invite you to the guild within 2 hours.\nWhile you wait, you can explore the guild discord!")
discord_not_linked_embed.set_image(
    url="https://media.discordapp.net/attachments/796061149593731128/953770877395284008/osl_.gif")

dnkl_creation_embed = discord.Embed(title="Do-not-kick-list",
                                    description="In order to create a do-not-kick-list entry, you need to have a valid reason and meet the DNKL requirements.",
                                    color=neutral_color
                                    ).add_field(
    name="Accepted Reasons",
    value="- Exams\n" \
          "- Vacation\n" \
          "- Medical reasons\n" \
          "- Computer Problems\n" \
          "- Other (Subject to staff judgement)",
    inline=False
).add_field(
    name="Requirements",
    value=f"- {format(dnkl_req, ',d')} weekly guild experience\n" \
          f"- DNKL period must be less than 3 weeks",
    inline=False
)

rules_embed = discord.Embed(title="Rules", description='''## In-Game Rules\n:small_blue_diamond: All Hypixel Rules apply.
:small_blue_diamond: Be respectful of all guild members.
:small_blue_diamond: Keep chat appropriate at all times.
:small_blue_diamond: Cheating is prohibited.
:small_blue_diamond: Refrain from spamming messages in guild chat or guild party chat.\n## Discord Rules\n:smiley: 1. **Be cool, kind, and civil.** Treat all members with respect and express your thoughts in a constructive manner.
:abc: 2. **Use English only.** Communicate in English, but be considerate of all languages.
:card_index: 3. **Use an appropriate name and avatar.** Avoid special characters, emoji, obscenities, and impersonation.
:incoming_envelope: 4. **Do not spam.** Avoid excessive messages, images, formatting, emoji, commands, and @mentions.
:no_bell: 5. **Do not @mention or direct message Miscellaneous Staff.** Respect their time, they are people too.
:loudspeaker: 6. **No self-promotion or advertisements.** This includes unsolicited references and links to other social media, servers, communities, and services in chat or direct messages.
7. **No personal information.** Protect your privacy and the privacy of others.
:head_bandage: 8. **No harassment, abuse, or bullying**. We have zero-tolerance for harming others.
:anger_right: 9. **No racist, sexist, anti-LGBTQ+, or otherwise offensive content.** We have zero-tolerance for hate speech.
:classical_building: 10. **No political or religious topics.** These complex subjects result in controversial and offensive posts.
:rotating_light: 11. **No piracy, sexual, NSFW, or otherwise suspicious content.** We do not condone illegal or suspicious discussions and activity.
:thinking: 12. **Rules are subject to common sense.** These rules are not comprehensive and use of loopholes to violate the spirit of these rules is subject to enforcement.
:scroll: 13. **Discord Terms of Service and Community Guidelines apply.** You must be at least 13 years old to use Discord, and abide by all other terms and guidelines.
''', color=neutral_color).set_thumbnail(
    url="https://media.discordapp.net/attachments/523227151240134664/803843877999607818/misc.png?ex=660cdaf3&is=65fa65f3&hm=beee26fd9f9b9f571893884ce18299d96a8b4a7f0ca7ad2ee4bc16758a0d31a5&=&format=webp&quality=lossless")
rank_upgrade_winner_announcement = '''# RANK UPGRADE
{date}

**The winner is....**
## {winner}
> Total Guild Experience:- `{winner_gexp}`
> Valid Invites:- `{winner_invites}`
> Total Entries:- `{winner_entries}`

This rank upgrade must be claimed within a week of this message by creating a ticket. If not claimed, it will be voided.

### Here are some statistics for the past week
- Total unscaled guild experience earned - `{total_gexp}`
- Total players invited (valid) - `{total_invites}`
- Total entries - `{total_entries}`

*To know how the winner is picked, go here https://discord.com/channels/522586672148381726/1152480866585554994/1164962591198683146*'''

# Do not change to https. Divider breaks.
rainbow_separator = "http://rainbowdivider.com/images/dividers/movrblin02.gif"


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
    8: "Suppose it's your first week of being a helper and you guild-mute a well-known player. Your guild-mates start spamming you calling you a bad moderator and telling you to unmute them. What would you do?",
    9: "Upon joining a game and you discover that a guild member is in your game and is hacking. What do you do?",
    10: "Have you been staff in any other guild or on any server? If yes, which one?",
    11: "How much time do you have to contribute to the role? (Per day)",
    12: "Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?",
    13: "Anything else you like would us to know?"
}
