import math
import random
import re
from datetime import datetime, timedelta

import aiohttp
import discord
from discord.ext import commands, tasks

from cogs.utils import utilities as utils


class miscellaneous(commands.Cog, name="Miscellaneous"):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    @commands.command()
    @commands.has_role("Giveaway Creator")
    async def giveaway(self, ctx, action, message_ID=None, reroll_number=None):
        """Create, end, reroll, and list giveaways!
        """
        if action.lower() in ["create", "make", "start", "add"]:  # Create new giveaway
            while True:
                await ctx.send(
                    "What is the channel you would want the giveaway to be held in?\n\n`Please enter the name of a channel in this server.` \n`Alternatively, you can enter the channel ID.` \n\n**At any time, you can cancel the giveaway by replying with `cancel` to one of the upcoming prompts.**")
                destination = await self.bot.wait_for('message',
                                                      check=lambda
                                                          x: x.channel == ctx.channel and x.author == ctx.author)
                destination = destination.content.lower()

                if destination == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif destination[0] == "<":  # Channel shortcut was passed
                    destination = int(re.sub(r'[\W_]+', '', destination))
                    destination_channel = self.bot.get_channel(destination)
                elif destination.isnumeric() == True:  # Channel ID was passed
                    destination_channel = self.bot.get_channel(int(destination))
                else:  # Channel name was passed
                    destination = re.sub(r"\s+", "-", destination)
                    destination_channel = discord.utils.get(ctx.guild.channels, name=destination)

                if destination_channel != None:  # Channel exists
                    break
                else:  # Channel is non-existent - Redo step.
                    await ctx.send(f"The channel {destination} is invalid!")

            # Channel entered correctly
            await ctx.send(
                f"Sweet! The giveaway is going to be held in <#{destination_channel.id}>. Next, what is the prize going to be?\n\n`Please enter a small description of the prize.`")
            prize = await self.bot.wait_for('message',
                                            check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            prize = prize.content

            if prize.lower() == "cancel":
                await ctx.send("Giveaway cancelled!")
                return

            # Prize entered correctly    
            while True:
                await ctx.send(
                    f"Ok great! The prize of the giveaway will be '{prize}'. How many winners should the giveaway have?\n\n`Please enter a number from 1-20.`")
                number_winners = await self.bot.wait_for('message',
                                                         check=lambda
                                                             x: x.channel == ctx.channel and x.author == ctx.author)
                number_winners = number_winners.content.lower()

                if number_winners == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif number_winners.isnumeric() == False:  # Did not enter an integer
                    await ctx.send(f"The input {number_winners} is not valid! Please enter a number.")

                else:  # Entered an number
                    number_winners = round(int(number_winners))
                    if number_winners > 20 or number_winners < 1:  # Too many/too few winners
                        await ctx.send(
                            f"The input {number_winners} is not valid! It must be greater than 1 and less than 20.")
                    else:
                        break

            # No. winners entered correctly
            while True:
                await ctx.send(
                    f"Neat! There will be {number_winners} winner(s). Also, how long should the giveaway last for?\n\n`Please enter a duration. Use an 's' at the end for seconds, 'M' for minutes, 'D' for days, etc.`")
                duration = await self.bot.wait_for('message',
                                                   check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                duration = duration.content.lower()

                if duration == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return

                seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
                try:
                    if int(duration[:-1]) <= 0:
                        await ctx.send(f"The duration {duration} is not valid!")
                    else:
                        seconds_end = timedelta(seconds=int(duration[:-1]) * seconds_per_unit[duration[-1]])
                        break
                except Exception:
                    await ctx.send(f"The duration {duration} is not valid!")

            # Duration entered correctly
            while True:
                for_broken = False
                await ctx.send(
                    f"Alright. The giveaway will last for {duration}. Should there be any role requirements for the giveaway?\n\n`Please enter role names or role IDs.`\n`If you don't want any role requirements, reply with 'None'`. \n`If entrants only need ONE of the required roles, use ',' between role names/IDs.` \n`If entrants must have ALL required roles, use '&' between role names/IDs`")
                required_roles = await self.bot.wait_for('message',
                                                         check=lambda
                                                             x: x.channel == ctx.channel and x.author == ctx.author)
                required_roles = required_roles.content.lower()
                required_roles = re.sub(r"\s+", "", required_roles)

                if required_roles == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif required_roles == "none":
                    r_requirements = None
                    role_requirement_type = "none"
                    required_roles = ""
                    break
                else:
                    # Convert string to list of all required roles
                    if "," in required_roles:
                        role_requirement_type = "optional"
                        required_roles = required_roles.split(",")
                    elif "&" in required_roles:
                        role_requirement_type = "required"
                        required_roles = required_roles.split("&")
                    else:  # Still turn string into list
                        role_requirement_type = "optional"
                        required_roles = [required_roles]

                    r_requirements = []
                    for required_role in required_roles:
                        required_role = required_role.title()
                        if re.search("[a-zA-Z]", required_role) != None:  # Role name was passed
                            req_role = discord.utils.get(ctx.guild.roles, name=required_role)
                            if req_role != None:
                                r_requirements.append(req_role.id)
                            else:
                                await ctx.send(f"The role {required_role} does not exist!")
                                for_broken = True
                                break

                        else:  # Role ID was passed
                            # Force to integer
                            required_role = int(required_role)
                            req_role = ctx.guild.get_role(required_role)
                            if req_role != None:
                                r_requirements.append(req_role.id)

                            else:
                                await ctx.send(f"The role {required_role} does not exist!")
                                for_broken = True
                                break

                    if for_broken:
                        continue
                    else:
                        break

                        # Role requirements entered correctly
            while True:
                await ctx.send(
                    f"Ok then, there will be {len(required_roles)} required role(s). Should there be a weekly gexp requirement for the giveaway?\n\n`If you don't want any gexp requirements, reply with 'None'.`\n`Otherwise, enter a required amount of weekly gexp. Add 'k' at the end to multiply it by one thousand, or 'm' for a million.`")

                required_gexp = await self.bot.wait_for('message',
                                                        check=lambda
                                                            x: x.channel == ctx.channel and x.author == ctx.author)
                required_gexp = required_gexp.content.lower()

                if required_gexp == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif required_gexp != "none":
                    multiplier_per_unit = {"k": 1000, "m": 1000000}
                    if required_gexp.isnumeric():  # No multiplier attached
                        raw_required_gexp = int(required_gexp)
                        break
                    else:
                        try:
                            raw_required_gexp = int(required_gexp[:-1]) * multiplier_per_unit[required_gexp[-1]]
                            break
                        except Exception:
                            await ctx.send(f"The gexp requirement {required_gexp} is not valid!")
                else:
                    required_gexp = 0
                    raw_required_gexp = 0
                    break

            # Gexp requirements entered correctly
            await ctx.send(
                f"Excellent! There will be a weekly gexp requirement of {required_gexp}. Finally, who has sponsored this giveaway?\n\n`Please ping or provide the tag(s) of the sponsors of this giveaway.`")
            sponsors = await self.bot.wait_for('message',
                                               check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            sponsors = sponsors.content

            if sponsors.lower() == "cancel":
                await ctx.send("Giveaway Cancelled!")
                return

            # Sponsors entered correctly
            while True:
                # Check if user needs one, all, or none of the required roles. Formulate message accordingly
                if role_requirement_type == "optional":
                    role_requirement_type_message = "You must have at least one of the following roles:"
                    for required_role in r_requirements:
                        role_requirement_type_message = role_requirement_type_message + f"\n- <@&{required_role}>"
                elif role_requirement_type == "none":
                    role_requirement_type_message = "There are no required roles."
                else:
                    role_requirement_type_message = "You must have all of the following roles:"
                    for required_role in r_requirements:
                        role_requirement_type_message = role_requirement_type_message + f"\n- <@&{required_role}>"

                # Confirmation message
                embed = discord.Embed(title="Giveaway Confirmation!",
                                      description="Please reply with `confirm` to start the giveaway.\nOtherwise, please reply with `cancel` to cancel the giveaway.",
                                      color=0x8368ff).set_footer(
                    text="This is your last opportunity to cancel this giveaway, to cancel it, say `cancel`.")
                embed.add_field(name="[-] Giveaway information",
                                value=f"**Prize:** {prize}\n**No. Winners:** {number_winners}\n**Duration:** {duration}",
                                inline=False)
                embed.add_field(name="[-] Requirements",
                                value=f"**Role Requirements** - {role_requirement_type_message}\n**Weekly Gexp Requirement** - {required_gexp}",
                                inline=False)
                await ctx.send(embed=embed)
                confirmation = await self.bot.wait_for('message',
                                                       check=lambda
                                                           x: x.channel == ctx.channel and x.author == ctx.author)
                confirmation = confirmation.content.lower()

                if confirmation in ["no", "cancel", "stop", "exit"]:
                    await ctx.send("Giveaway Cancelled!")
                    return
                elif confirmation not in ["yes", "confirm", "go", "create"]:
                    await ctx.send(f"The input {confirmation} is not valid!")
                else:
                    # Force giveaway time (s) to formatted UTC datetime
                    datetime_end = datetime.utcnow() + seconds_end
                    datetime_end_str = datetime_end.strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]
                    # Send giveaway message
                    embed = discord.Embed(title=f"{prize}", color=0x8368ff).set_footer(
                        text=f"{number_winners} Winner(s), Ends at {datetime_end_str} UTC/GMT")
                    embed.add_field(name="[-] Information:", value=f"Sponsored by: {sponsors} \nDuration: {duration}",
                                    inline=False)
                    embed.add_field(name="[-] Requirements:",
                                    value=f"{role_requirement_type_message} \nYou must have at least {required_gexp} weekly gexp.",
                                    inline=False)
                    giveaway_msg = await destination_channel.send(
                        f"{self.bot.giveaways_events.mention} React with :tada: to enter!\n", embed=embed)
                    await giveaway_msg.add_reaction("\U0001F389")
                    await destination_channel.send(f"This giveaway was generously sponsored by {sponsors}.\nIf you win this giveaway, make a ticket to claim it!")

                    if required_roles != "":  # Convert list to str for db
                        required_roles = ""
                        required_roles = ' '.join([str(elem) for elem in r_requirements])

                    # Enter data into db
                    await self.bot.db.execute("INSERT INTO Giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                              (giveaway_msg.id, destination_channel.id, prize, number_winners,
                                               datetime_end_str, role_requirement_type, required_roles,
                                               raw_required_gexp, sponsors, "active"))
                    await self.bot.db.commit()

                    await ctx.send(f"Ok! The giveaway has been set up in <#{destination_channel.id}>.")
                    break

        elif action.lower() in ["end", "finish"]:  # End existing giveaway
            if message_ID == None:
                await ctx.send("You must provide the message ID of a giveaway to end!")
            else:
                cursor = await self.bot.db.execute("SELECT status FROM Giveaways WHERE message_id = (?)", (message_ID,))
                row = await cursor.fetchone()
                await cursor.close()

                if row == None:
                    await ctx.send(
                        "The specified giveaway doesn't seem to exist!\n`Either this giveaway never existed, or the data for the giveaway was deleted after 10 days of disuse.`")
                else:
                    status = "".join(row)
                    if status == "active":
                        await self.roll_giveaway(message_ID)
                    else:
                        await ctx.send(
                            "The giveaway specified has already ended!\n`To re-roll that giveaway, use the command ,giveaway reroll`")
                        return



        elif action.lower() == "reroll":  # Reroll existent giveaway
            if message_ID == None:
                await ctx.send("You must provide the message ID of a giveaway to reroll!")
            else:
                cursor = await self.bot.db.execute(
                    "SELECT number_winners, status FROM Giveaways WHERE message_id = (?)", (message_ID,))
                row = await cursor.fetchone()
                await cursor.close()

                if row == None:
                    await ctx.send(
                        "The specified giveaway doesn't seem to exist!\n`Either this giveaway never existed, or the data for the giveaway was deleted after 10 days of disuse.`")
                else:
                    status, number_winners = ",".join([str(value) for value in row]).split(",")
                    if status == "active":
                        await ctx.send(
                            "You cannot reroll an on-going giveaway! \n`To end this giveaway, use ',giveaway end'`.")
                    if reroll_number == None:  # Reroll whole giveaway
                        await self.roll_giveaway(message_ID)
                    elif reroll_number.isnumeric() == False:
                        await ctx.send("The number of winners to reroll for must be numeric!")
                    else:
                        reroll_number = math.floor(int(reroll_number))
                        if reroll_number <= int(
                                number_winners):  # Reroll giveaway with only a certain number of new winners
                            await self.roll_giveaway(message_ID, reroll_number)
                        else:
                            await ctx.send(
                                "You cannot reroll a giveaway for more winners than was originally intended!")


        elif action.lower() == "list":  # List all current giveaways
            cursor = await self.bot.db.execute(
                "SELECT prize, channel_id, message_id, number_winners, time_of_finish, status FROM Giveaways")
            rows = cursor.fetchall()
            await cursor.close()

            if rows == None:
                embed = discord.Embed(title="There have been no giveaways in the last 10 days!",
                                      description="To make a new giveaway, use the command `,giveaway create`",
                                      color=0xFF0000)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Giveaways:",
                                      description="Listed below are all giveaways from the last 10 days.",
                                      color=0x8368ff)
                for row in rows:
                    prize, channel_id, message_id, number_winners, datetime_end_str, status = ",".join(
                        [str(value) for value in row]).split(",")

                    embed.add_field(name=f"{prize}",
                                    value=f"Channel: <#{channel_id}> \nMessage ID: {message_id} \nNumber Of Winners: {number_winners} \nEnds At: {datetime_end_str} \nStatus: {status}")
                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="Invalid Command!", description="Use `,help giveaway` for more info on",
                                  color=0xFF0000)
            await ctx.send(embed=embed)

async def roll_giveaway(self, message_ID, reroll_number=None):
    cursor = await self.bot.db.execute(
        "SELECT message_id, channel_id, prize, number_winners, role_requirement_type, required_roles, required_gexp FROM Giveaways WHERE message_id = (?)",
        (message_ID,))
    row = await cursor.fetchone()
    await cursor.close()
    message_id, channel_id, prize, number_winners, role_requirement_type, required_roles, required_gexp = ",".join(
        [str(value) for value in row]).split(",")
    required_roles = required_roles.split(" ")

    message = await self.bot.get_channel(int(channel_id)).fetch_message(int(message_id))
    message_channel = self.bot.get_channel(int(channel_id))

    reactions = message.reactions
    entrants = []
    winners = []

    for reaction in reactions:
        if (reaction.emoji.encode("unicode-escape") == b'\\U0001f389'):  # If reaction is :tada:
            has_reaction = True
            entrants = await reaction.users().flatten()
            del entrants[0]  # Remove bot's own reaction
            break

    if has_reaction != True:  # Giveaway message does not have the :tada: reaction
        await message_channel.send(f"Yikes! The giveaway for {prize} doesn't seem to have the :tada: reaction :(")
        await self.bot.db.execute("UPDATE Giveaways SET status = 'inactive' WHERE message_id = (?)", (message_id,))
        await self.bot.db.commit()
        return

    if reroll_number == None:
        number_winners = int(number_winners)
    else:
        number_winners = reroll_number

    while len(winners) < number_winners:  # Pick a random winner
        while True:  # Protection from infinite picking of winner
            if len(entrants) == 0 and len(winners) == 0:  # No eligible winners
                await message_channel.send(
                    f"There were no eligible winners for `{prize}`, the giveaway has been ended - message ID `{message_id}`.")
                await self.bot.db.execute("UPDATE Giveaways SET status = 'inactive' WHERE message_id = (?)",
                                            (message_id,))
                await self.bot.db.commit()
                return

            elif len(entrants) == 0:  # Less eligible winners that number_winners
                announcement = ""
                for winner in winners:
                    category = discord.utils.get(self.bot.guild.categories, name="🎫 Ticket Section")
                    winner_ticket = await self.bot.guild.create_text_channel(f"giveaway-winner-{winner.nick}",
                                                                                category=category)
                    await winner_ticket.set_permissions(self.botguild.get_role(self.bot.guild.id),
                                                        send_messages=False,
                                                        read_messages=False)
                    await winner_ticket.set_permissions(self.bot.staff, send_messages=True, read_messages=True,
                                                        add_reactions=True, embed_links=True,
                                                        attach_files=True,
                                                        read_message_history=True, external_emojis=True)
                    await winner_ticket.set_permissions(self.bot.t_officer, send_messages=True,
                                                        read_messages=True,
                                                        add_reactions=True, embed_links=True,
                                                        attach_files=True,
                                                        read_message_history=True, external_emojis=True)
                    await winner_ticket.set_permissions(winner, send_messages=True, read_messages=True,
                                                        add_reactions=True, embed_links=True,
                                                        attach_files=True,
                                                        read_message_history=True, external_emojis=True)
                    await winner_ticket.set_permissions(self.bot.new_member_role, send_messages=False,
                                                        read_messages=False,
                                                        add_reactions=True, embed_links=True,
                                                        attach_files=True,
                                                        read_message_history=True, external_emojis=True)
                    await winner_ticket.send(f"{winner.mention}")

                    announcement = announcement + f"{winner.mention},"

                await message_channel.send(
                    f":tada: Congratulations {announcement} you won the giveaway for {prize}\nMake a ticket to claim!\n`There were less eligible winners for this giveaway than the expected number.`")
                await self.bot.db.execute("UPDATE Giveaways SET status = 'inactive' WHERE message_id = (?)",
                                            (message_id,))
                await self.bot.db.commit()
                return

            else:
                winner = random.choice(entrants)
                break
        name = await utils.name_grabber(winner)

        # ROLE REQUIREMENTS
        if len(required_roles) and role_requirement_type != "none":
            if role_requirement_type == "optional":  # Needs ONE of the required roles
                if not any(role.id in required_roles for role in winner.roles):
                    entrants.remove(winner)
                    continue

            elif role_requirement_type == "required":  # Needs ALL of the required roles
                for req in required_roles:
                    if discord.utils.get(self.bot.misc_guild.roles, id=req) not in winner.roles:
                        for_broken = True
                if for_broken:
                    entrants.remove(winner)
                    continue

        # GEXP REQUIREMENTS
        required_gexp = int(required_gexp)
        if required_gexp != 0:  # There is a gexp requirement
            async with aiohttp.ClientSession() as session:  # Get winner profile info
                async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                    request = await resp.json(content_type=None)
                    await session.close()
            if resp.status != 200:
                entrants.remove(winner)

            else:
                name = request['name']
                uuid = request['id']
                api = utils.get_api()
                async with aiohttp.ClientSession() as session:  # Get winner's weekly GEXP
                    async with session.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}') as resp:
                        req = await resp.json(content_type=None)
                        await session.close()
                if resp.status != 200:
                    entrants.remove(winner)

                else:
                    if "guild" not in req or req['guild'] is None:  # Winner is guildless
                        entrants.remove(winner)

                    else:
                        for member in req["guild"]["members"]:
                            if uuid == member["uuid"]:
                                if sum(member[
                                            "expHistory"].values()) >= required_gexp:  # Winner meets the gexp requirement
                                    entrants.remove(winner)
                                    winners.append(winner)
                                    break

                                else:
                                    entrants.remove(winner)
                                    break

        else:  # There is no gexp requirement
            entrants.remove(winner)
            winners.append(winner)

    await self.bot.db.execute("UPDATE Giveaways SET status = 'inactive' WHERE message_id = (?)", (message_id,))
    await self.bot.db.commit()

    announcement = ""
    for winner in winners:
        category = discord.utils.get(self.bot.misc_guild.categories, name="🎫 Ticket Section")
        winner_ticket = await self.bot.misc_guild.create_text_channel(f"giveaway-winner-{winner.nick}",
                                                                        category=category)
        await winner_ticket.set_permissions(self.bot.misc_guild.get_role(self.bot.misc_guild.id),
                                            send_messages=False,
                                            read_messages=False)
        await winner_ticket.set_permissions(self.bot.staff, send_messages=True, read_messages=True,
                                            add_reactions=True, embed_links=True,
                                            attach_files=True,
                                            read_message_history=True, external_emojis=True)
        await winner_ticket.set_permissions(self.bot.t_officer, send_messages=True,
                                            read_messages=True,
                                            add_reactions=True, embed_links=True,
                                            attach_files=True,
                                            read_message_history=True, external_emojis=True)
        await winner_ticket.set_permissions(winner, send_messages=True, read_messages=True,
                                            add_reactions=True, embed_links=True,
                                            attach_files=True,
                                            read_message_history=True, external_emojis=True)
        await winner_ticket.set_permissions(self.bot.new_member_role, send_messages=False,
                                            read_messages=False,
                                            add_reactions=True, embed_links=True,
                                            attach_files=True,
                                            read_message_history=True, external_emojis=True)
        await winner_ticket.send(f"{winner.mention}")
        announcement += f"{winner.mention},"
    await message_channel.send(
        f":tada: Congratulations {announcement} you won the giveaway for {prize}!\nMake a ticket to claim!")

    @tasks.loop(minutes=1)
    async def check_giveaways(self):
        cursor = await self.bot.db.execute("SELECT message_id, status, time_of_finish FROM Giveaways")
        rows = await cursor.fetchall()
        await cursor.close()

        for row in rows:
            message_id, status, datetime_end_str = ",".join([str(value) for value in row]).split(",")
            datetime_end = datetime.strptime(datetime_end_str, "%Y-%m-%d %H:%M:%S")

            if status == "active" and datetime_end < datetime.utcnow():  # Giveaway needs to be ended
                await self.roll_giveaway(message_id)
            elif status == "inactive" and datetime.utcnow() > datetime_end + timedelta(days=10):  # If giveaway ended more than 10 days ago, delete it
                await self.bot.db.execute("DELETE FROM Giveaways WHERE message_id = (?)", (message_id,))
                await self.bot.db.commit()

    @check_giveaways.before_loop
    async def before_giveaway_check(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(miscellaneous(bot))
