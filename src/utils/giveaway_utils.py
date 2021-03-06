import random
from datetime import datetime, timedelta

import discord
from __main__ import bot
from discord.ext import tasks
from src.utils.consts import neutral_color
from src.utils.db_utils import (connect_db, select_all, select_one,
                                set_giveaway_inactive)
from src.utils.discord_utils import name_grabber
from src.utils.minecraft_utils import get_player_gexp
from src.utils.request_utils import get_mojang_profile


async def roll_giveaway(message_id: int, reroll_target: int = None):
    # Fetch data
    channel_id, prize, number_winners, time_of_finish, req_gexp, all_roles_required, req_roles, sponsors = await select_one(
        "SELECT channel_id, prize, number_winners, time_of_finish, required_gexp, all_roles_required, required_roles, sponsors FROM giveaways WHERE message_id = (?)",
        (message_id,))

    req_roles = None if not req_roles else [int(role) for role in req_roles.split(" ")]

    # Channel and message vars
    channel: discord.TextChannel = bot.get_channel(channel_id)
    message: discord.Message = await channel.fetch_message(message_id)

    # Only fetch 🎉 reaction
    for reaction in message.reactions:
        if str(reaction.emoji) != "🎉":
            continue

        # Set vars
        if reroll_target:
            number_winners = reroll_target
        # Get all users, remove bot's own reaction
        entrants = await reaction.users().flatten()
        del entrants[0]
        winners: list[discord.Member] = []

        # Pick winners
        while len(winners) < number_winners:
            # No eligible winners
            if not len(entrants) and not len(winners):
                await set_giveaway_inactive(message_id)
                return await channel.send(
                    f"There were no eligible winners for `{prize}`, the giveaway has been ended. Message ID `{message_id}`")

            # Less eligible winners than number_winners
            elif not len(entrants):
                announcement = ",".join([user.mention for user in winners])
                await set_giveaway_inactive(message_id)
                return await channel.send(
                    f"🎉 Congrats {announcement} you won the giveaway for {prize}! Please make a ticket to claim.\nThere were less eligible winners than the expected number.")

            # Otherwise pick a new entrant and check they meet reqs
            winner = random.choice(entrants)

            # Remove entrant if they do not meet role reqs
            if req_roles:
                if not all_roles_required and not any(
                        role.id in req_roles for role in winner.roles) or all_roles_required and not all(
                        role.id in req_roles for role in winner.roles):
                    entrants.remove(winner)
                    continue

            # Gexp requirements
            if req_gexp != 0:
                _, uuid = await get_mojang_profile(await name_grabber(winner))
                _, weekly_exp = await get_player_gexp(uuid)

                # Player meets gexp req
                if weekly_exp and weekly_exp >= req_gexp:
                    winners.append(winner)
                entrants.remove(winner)
                continue

            # By default, that user is a winner
            winners.append(winner)

        # Create announcement
        announcement = ",".join([user.mention for user in winners])
        await channel.send(
            f"🎉 Congratulations {announcement} you won the giveaway for {prize}!\nMake a ticket to claim!")

        # Edit embed
        embed = discord.Embed(
            title=prize, description=f"Winners: {announcement}\nSponsored by: {sponsors}", color=neutral_color)
        embed.set_footer(text=f"This giveaway ended at  {time_of_finish}")
        await set_giveaway_inactive(message_id)
        return await message.edit(embed=embed)

    # Message does not have 🎉 reaction
    await set_giveaway_inactive(message_id)
    return await channel.send(f"Yikes! The giveaway for {prize} doesn't seem to have the 🎉 reaction :(")


@tasks.loop(minutes=1)
async def check_giveaways():
    # Get all giveaway data
    all_giveaways = await select_all("SELECT message_id, time_of_finish, is_active FROM giveaways")

    for message_id, time_of_finish, is_active in all_giveaways:
        time_of_finish = datetime.strptime(time_of_finish, "%Y-%m-%d %H:%M:%S")

        # Giveaway needs to be ended
        if is_active and time_of_finish < datetime.utcnow():
            await roll_giveaway(message_id)

        # Giveaway ended more than 10 days ago, delete it
        elif not is_active and datetime.utcnow() > time_of_finish + timedelta(days=10):
            await bot.db.execute("DELETE FROM Giveaways WHERE message_id = (?)", (message_id,))
            await bot.db.commit()


@check_giveaways.before_loop
async def before_giveaway_check():
    await bot.wait_until_ready()
    await connect_db()


check_giveaways.start()
