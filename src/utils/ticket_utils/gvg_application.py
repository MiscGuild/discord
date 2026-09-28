from __main__ import bot

import discord

import src.utils.ui_utils as uiutils
from src.utils.calculation_utils import create_stats_text
from src.utils.consts import UNKNOWN_IGN_EMBED, NEUTRAL_COLOR, NEG_COLOR, GVG_REQUIREMENTS, \
    MISSING_PERMS_EMBED
from src.utils.request_utils import get_hypixel_player


async def gvg_approve(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                      interaction: discord.Interaction):
    if bot.staff not in interaction.user.roles:
        await channel.send(embed=MISSING_PERMS_EMBED)
        return None

    await interaction.response.send_message(embed=discord.Embed(
        title="Your application has been accepted!",
        description="Please await staff assistance for more information!",
        color=NEUTRAL_COLOR))
    member = await bot.guild.fetch_member(author.id)
    await member.add_roles(bot.gvg)

    return True


async def gvg_deny(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, embed: discord.Embed,
                   interaction: discord.Interaction):
    if bot.staff not in interaction.user.roles:
        await channel.send(embed=MISSING_PERMS_EMBED)
        return None

    await interaction.response.send_message(embed=discord.Embed(
        title="Your application has been denied!",
        description="Please await staff assistance for more information!",
        color=NEG_COLOR))

    return True


async def gvg_application(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str, uuid: str,
                          user: discord.Member):
    await ticket.edit(name=f"gvg-application-{ign}")

    # Fetch player data
    player_data = await get_hypixel_player(uuid=uuid)
    if not player_data:
        return await ticket.send(embed=UNKNOWN_IGN_EMBED)
    player_data = player_data["stats"]

    # Set vars for each stat
    bw_wins = player_data["Bedwars"]["wins_bedwars"] if "Bedwars" in player_data and "wins_bedwars" in player_data[
        "Bedwars"] else 0
    final_kills = player_data["Bedwars"]["final_kills_bedwars"] if "Bedwars" in player_data and "final_kills_bedwars" in \
                                                                   player_data["Bedwars"] else 0
    final_deaths = player_data["Bedwars"][
        "final_deaths_bedwars"] if "Bedwars" in player_data and "final_deaths_bedwars" in player_data["Bedwars"] else 0
    bw_fkdr = round(final_kills / final_deaths, 2) if final_deaths else final_kills

    sw_wins = player_data["SkyWars"]["wins"] if "SkyWars" in player_data and "wins" in player_data["SkyWars"] else 0
    sw_kills = player_data["SkyWars"]["kills"] if "SkyWars" in player_data and "kills" in player_data["SkyWars"] else 0
    sw_deaths = player_data["SkyWars"]["deaths"] if "SkyWars" in player_data and "deaths" in player_data[
        "SkyWars"] else 0
    sw_kdr = round(sw_kills / sw_deaths, 2) if sw_deaths else sw_kills

    duels_wins = player_data["Duels"]["wins"] if "Duels" in player_data and "wins" in player_data["Duels"] else 0
    duels_losses = player_data["Duels"]["losses"] if "Duels" in player_data and "losses" in player_data["Duels"] else 0
    duels_wlr = round(duels_wins / duels_losses, 2) if duels_losses else duels_wins
    duels_kills = player_data["Duels"]["kills"]

    # Define dict for eligibility and set each gamemode boolean
    # Define eligibility for each GvG team
    eligibility = {
        "bedwars": (
                bw_wins >= GVG_REQUIREMENTS["bw_wins"]
                and bw_fkdr >= GVG_REQUIREMENTS["bw_fkdr"]
        ),
        "skywars": (
                sw_wins >= GVG_REQUIREMENTS["sw_wins"]
                and sw_kdr >= GVG_REQUIREMENTS["sw_kdr"]
        ),
        "duels": (
                duels_wlr >= GVG_REQUIREMENTS["duels_wlr"]
                and duels_kills >= GVG_REQUIREMENTS["duels_kills"]
        )
    }

    # Store the stats and requirements for each gamemode
    gamemode_data = {
        "bedwars": {
            "name": "Bedwars",
            "stats": [
                ("Wins", bw_wins, GVG_REQUIREMENTS["bw_wins"]),
                ("FKDR", bw_fkdr, GVG_REQUIREMENTS["bw_fkdr"])
            ]
        },

        "skywars": {
            "name": "Skywars",
            "stats": [
                ("Wins", sw_wins, GVG_REQUIREMENTS["sw_wins"]),
                ("KDR", sw_kdr, GVG_REQUIREMENTS["sw_kdr"])
            ]
        },

        "duels": {
            "name": "Duels",
            "stats": [
                ("WLR", duels_wlr, GVG_REQUIREMENTS["duels_wlr"]),
                ("Kills", duels_kills, GVG_REQUIREMENTS["duels_kills"])
            ]
        }
    }


    if all(eligibility.values()):
        embed = discord.Embed(
            title="✅ You are eligible for the Polyvalent GvG Team!",
            description=(
                "You meet the requirements for **all three GvG teams**.\n\n"
                "Your statistics for each gamemode are shown below."
            ),
            color=NEUTRAL_COLOR
        )

        for mode in ["bedwars", "skywars", "duels"]:
            embed.add_field(
                name=f"✅ {gamemode_data[mode]['name']} — Qualified",
                value=await create_stats_text(gamemode_data, mode),
                inline=False
            )


    elif not any(eligibility.values()):
        embed = discord.Embed(
            title="❌ You currently do not meet the GvG Team requirements",
            description=(
                "Unfortunately, you do not currently meet the minimum "
                "requirements for any of our GvG teams.\n\n"
                "Below you can see your current statistics compared with "
                "the requirements for each team."
            ),
            color=NEG_COLOR
        )

        for mode in ["bedwars", "skywars", "duels"]:
            embed.add_field(
                name=f"❌ {gamemode_data[mode]['name']} — Not Qualified",
                value=await create_stats_text(gamemode_data, mode),
                inline=False
            )


    else:
        eligible_teams = [
            gamemode_data[mode]["name"]
            for mode in eligibility
            if eligibility[mode]
        ]

        embed = discord.Embed(
            title="✅ You are eligible for one or more GvG teams!",
            description=(
                f"You currently qualify for: "
                f"**{', '.join(eligible_teams)}**.\n\n"
                "Your results for every GvG team are shown below. "
                "For teams you did not qualify for, you can also see "
                "the requirements you are currently missing."
            ),
            color=NEUTRAL_COLOR
        )

        # First show teams that the player qualifies for
        for mode in ["bedwars", "skywars", "duels"]:
            if eligibility[mode]:
                embed.add_field(
                    name=f"✅ {gamemode_data[mode]['name']} — Qualified",
                    value=await create_stats_text(gamemode_data, mode),
                    inline=False
                )

        # Then show teams that the player did not qualify for
        for mode in ["bedwars", "skywars", "duels"]:
            if not eligibility[mode]:
                embed.add_field(
                    name=f"❌ {gamemode_data[mode]['name']} — Not Qualified",
                    value=await create_stats_text(gamemode_data, mode),
                    inline=False
                )

    embed.set_footer(
        text="Please await staff assistance for further information regarding your application."
    )
    GvGView = discord.ui.View(timeout=None)

    buttons = (
        ("Accept", "GvG_Application_Positive",
         discord.enums.ButtonStyle.green, gvg_approve),
        ("Deny", "GvG_Application_Negative",
         discord.enums.ButtonStyle.red, gvg_deny)
    )

    for button in buttons:
        GvGView.add_item(
            uiutils.Button_Creator(
                channel=ticket,
                ign=ign,
                button=button,
                author=user,
                uuid=uuid,
                function=button[3]
            )
        )

    await ticket.send(
        "Staff, what do you wish to do with this application?",
        embed=embed,
        view=GvGView
    )
