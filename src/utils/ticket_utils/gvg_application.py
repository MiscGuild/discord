from __main__ import bot

import discord

import src.utils.ui_utils as uiutils
from src.utils.consts import unknown_ign_embed, neutral_color, ticket_categories, neg_color, gvg_requirements, \
    missing_permissions_embed
from src.utils.minecraft_utils import get_hypixel_player


async def gvg_approve(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                      interaction: discord.Interaction):
    if bot.staff not in interaction.user.roles:
        await channel.send(embed=missing_permissions_embed)
        return None

    await interaction.response.send_message(embed=discord.Embed(
        title="Your application has been accepted!",
        description="Please await staff assistance for more information!",
        color=neutral_color))
    member = await bot.guild.fetch_member(author.id)
    await member.add_roles(bot.gvg)

    return True


async def gvg_deny(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                   interaction: discord.Interaction):
    if bot.staff not in interaction.user.roles:
        await channel.send(embed=missing_permissions_embed)
        return None

    await interaction.response.send_message(embed=discord.Embed(
        title="Your application has been denied!",
        description="Please await staff assistance for more information!",
        color=neg_color))

    return True


async def gvg_application(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str, uuid: str,
                          user: discord.User):
    await ticket.edit(name=f"gvg-application-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["generic"]))

    # Fetch player data
    player_data = await get_hypixel_player(uuid=uuid)
    if not player_data:
        return await ticket.send(embed=unknown_ign_embed)
    player_data = player_data["stats"]

    # Set vars for each stat
    bw_wins = player_data["Bedwars"]["wins_bedwars"]
    bw_fkdr = round(
        player_data["Bedwars"]["final_kills_bedwars"] / player_data["Bedwars"]["final_deaths_bedwars"],
        2)
    sw_wins = player_data["SkyWars"]["wins"]
    sw_kdr = round(player_data["SkyWars"]["kills"] / player_data["SkyWars"]["deaths"], 2)
    duels_wlr = round(player_data["Duels"]["wins"] / player_data["Duels"]["losses"], 2)
    duels_kills = player_data["Duels"]["kills"]

    # Define dict for eligibility and set each gamemode boolean
    eligibility = {}
    eligibility["bedwars"] = False if bw_wins < gvg_requirements["bw_wins"] and bw_fkdr < \
                                      gvg_requirements["bw_fkdr"] else True
    eligibility["skywars"] = False if sw_wins < gvg_requirements["sw_wins"] and sw_kdr < \
                                      gvg_requirements["sw_kdr"] else True
    eligibility["duels"] = False if duels_wlr < gvg_requirements["duels_wlr"] and duels_kills < \
                                    gvg_requirements["duels_kills"] else True

    # Polyvalent eligibility
    if all(eligibility.values()):
        embed = discord.Embed(title="You are eligible for the polyvalent team!", color=neutral_color)
        embed.set_footer(text="Please await staff assistance for further information!")
        embed.add_field(name="Bedwars Wins", value=f"`{bw_wins}`")
        embed.add_field(name="Bedwars FKDR", value=f"`{bw_fkdr}`")
        embed.add_field(name="Skywars Wins", value=f"`{sw_wins}`")
        embed.add_field(name="Skywars KDR", value=f"`{sw_kdr}`")
        embed.add_field(name="Duels WLR", value=f"`{duels_wlr}`")
        embed.add_field(name="Duels Kills", value=f"`{duels_kills}`")

    # User is not eligible for any team
    elif not all(eligibility.values()):
        embed = discord.Embed(
            title="You are ineligible for the GvG Team as you do not meet the requirements!",
            description="If you think this is incorrect, please await staff assistance",
            color=neg_color)
        embed.add_field(name="Bedwars Wins", value=f"`{bw_wins}`")
        embed.add_field(name="Bedwars FKDR", value=f"`{bw_fkdr}`")
        embed.add_field(name="Skywars Wins", value=f"`{sw_wins}`")
        embed.add_field(name="Skywars KDR", value=f"`{sw_kdr}`")
        embed.add_field(name="Duels WLR", value=f"`{duels_wlr}`")
        embed.add_field(name="Duels Kills", value=f"`{duels_kills}`")
        await ticket.send(embed=discord.Embed(
            title="You are ineligible for the GvG Team as you do not meet the requirements!",
            description="Please await staff assistance for further information!",
            color=neg_color))

    # User is eligible for at least one gamemode
    else:
        # loop through all GvG gamemodes
        for mode, req1_name, req1, req2_name, req2 in [["bedwars", "Wins", bw_wins, "FKDR", bw_fkdr],
                                                       ["skywars", "Wins", sw_wins, "KDR", sw_kdr],
                                                       ["duels", "WLR", duels_wlr, "Kills",
                                                        duels_kills]]:
            # If user is eligible for that gamemode, create embed
            if eligibility[mode]:
                embed = discord.Embed(title=f"You are eiligible for the {mode.capitalize()} team!",
                                      color=neutral_color)
                embed.set_footer(text="Please await staff assistance for further information!")
                embed.add_field(name=req1_name, value=f"`{req1}`")
                embed.add_field(name=req2_name, value=f"`{req2}`")

                # Send embed and end loop

    GvGView = discord.ui.View(timeout=None)  # View for staff members to approve/deny the DNKL
    buttons = (("Accept", "GvG_Application_Positive", discord.enums.ButtonStyle.green, gvg_approve),
               ("Deny", "GvG_Application_Negative", discord.enums.ButtonStyle.red, gvg_deny))
    # Loop through the list of roles and add a new button to the view for each role.
    for button in buttons:
        # Get the role from the guild by ID.
        GvGView.add_item(
            uiutils.Button_Creator(channel=ticket, ign=ign, button=button, author=user, uuid=uuid,
                                   function=button[3]))

    await ticket.send("Staff, what do you wish to do with this application?", embed=embed,
                      view=GvGView)
