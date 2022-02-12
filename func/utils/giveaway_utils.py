import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import random

from __main__ import bot

from func.utils.discord_utils import name_grabber
from func.utils.minecraft_utils import get_player_gexp
from func.utils.consts import neutral_color
from func.utils.db_utils import select_one, select_all, set_giveaway_inactive, connect_db

async def roll_giveaway(message_id: int, reroll_target: int = None):
    # Fetch data
    channel_id, prize, number_winners, time_of_finish, req_gexp, all_roles_required, req_roles, sponsors = await select_one("SELECT channel_id, prize, number_winners, time_of_finish, req_gexp, all_roles_required, req_roles, sponsors FROM giveaways WHERE message_id = (?)", (message_id,))
    req_roles = [int(role) for role in req_roles.split(" ")]

    # Channel and message vars
    channel: discord.TextChannel = await bot.get_channel(channel_id)
    message: discord.Message = await channel.fetch_message(message_id)
    
    # Only fetch 🎉 reaction
    for reaction in message.reactions:
        if reaction.emoji.encode("unicode-escape") != b"\\U0001f389": continue

        # Set vars
        if reroll_target:
            number_winners = reroll_target
        entrants = await reaction.users().flatten()
        winners: list[discord.User] = []

        # Pick winners
        while len(winners) < number_winners:
            # No eligible winners
            if not len(entrants) and not len(winners):
                await set_giveaway_inactive(message_id)
                return await channel.send(f"There were no eligible winners for `{prize}`, the giveaway has been ended. Message ID `{message_id}`")

            # Less eligible winners than number_winners
            elif not len(entrants):
                announcement = ",".join([user.mention for user in winners])
                await set_giveaway_inactive(message_id)
                return await channel.send(f"🎉 Congrats {announcement} you won the giveaway for {prize}! Please make a ticket to claim.\nThere were less eligible winners than the expected number.")

            # Otherwise pick a new entrant and check they meet reqs
            winner = random.choice(entrants) 
            name = await name_grabber(winner)

            # Remove entrant if they do not meet role reqs
            if len(req_roles) and (not all_roles_required and not any(role.id in req_roles for role in winner.roles)) or not all(role.id in req_roles for role in winner.roles):
                entrants.remove(winner)
                continue

            # Gexp requirements
            if req_gexp != 0:
                _, weekly_exp = await get_player_gexp(name)

                # Player meets gexp req
                if weekly_exp and weekly_exp >= req_gexp:
                    winners.append(winner)  
                entrants.remove(winner)
                continue
            
            # By default, that user is a winner
            winners.append(winner)
        
        # Create announcement
        announcement = ",".join([user.mention for user in winners])
        await channel.send(f"🎉 Congratulations {announcement} you won the giveaway for {prize}!\nMake a ticket to claim!")

        # Edit embed
        embed = discord.Embed(title=prize, description=f"Winners: {announcement}\nSponsored by: {sponsors}", color=neutral_color)
        embed.set_footer(text=f"This giveaway ended at  {time_of_finish}")
        await message.edit(embed=embed)

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
