# The following file contains: weeklylb, dnkllist, rolecheck, staffreview, delete, accept, transcript, new, partner, deny, inactive, giveawaycreate, giveawaylist

import asyncio
import re
import aiohttp
from datetime import datetime, timedelta

import discord
from __main__ import bot
from func.utils.consts import (accepted_staff_application_embed, active_req,
                               allies, error_color, guild_handle,
                               invalid_guild_embed, log_channel_id, member_req,
                               neg_color, neutral_color, new_member_req,
                               pos_color, registration_channel_id,
                               registration_embed, staff_application_questions,
                               ticket_categories)
from func.utils.db_utils import insert_new_giveaway, select_all
from func.utils.discord_utils import (create_ticket, create_transcript,
                                      log_event, name_grabber)
from func.utils.minecraft_utils import get_hypixel_player_rank
from func.utils.request_utils import (get_guild_by_name, get_guild_uuids,
                                      get_hypixel_player, get_jpg_file,
                                      get_mojang_profile, get_name_by_uuid,
                                      get_player_guild)


class Func:
    async def weeklylb(ctx):
        async with ctx.channel.typing():
            # Get guild data
            guild_data = await get_guild_by_name(guild_handle)

            if guild_data == None:
                return invalid_guild_embed

            member_gexp = {}

            # Loop through all guild members' gexp, adding it to dict
            for member in guild_data["members"]:
                member_gexp[member["uuid"]] = sum(
                    member["expHistory"].values())

            # Sort member gexp
            member_gexp = sorted(member_gexp.items(),
                                 key=lambda item: item[1], reverse=True)

            # Create url
            url = "&f&lWeekly Top&r%5Cn"
            for i in range(10):
                user_data = member_gexp[i]
                name = await get_name_by_uuid(user_data[0])
                rank, _ = await get_hypixel_player_rank(await get_hypixel_player(name))

                # Add new entry to image content
                url += f"&6{i + 1}. {rank} {name} &2{format(user_data[1], ',d')} Guild Experience"
                # Add new line
                if i < 9:
                    url += "%5Cn"

            # Replace characters for URL
            url = url.replace("+", "%2B")
            url = url.replace("&", "%26")
            url = url.replace(" ", "%20")
            url = url.replace(",", "%2C")

            # Return image
            return await get_jpg_file(f"https://chat.miscguild.xyz/render.png?m=custom&d={url}&t=1")

    async def dnkllist():
        # Fetch all rows
        rows = await select_all("SELECT * FROM dnkl")

        if not rows:
            return discord.Embed(title="No entries!", description="There are no users on the do-not-kick-list!", color=neg_color)

        # Create embed
        content = ""
        for _set in rows:
            _, _, username = _set
            content += f"{username}\n"

        return discord.Embed(title="The people on the do-not-kick-list are as follows:", description=content, color=neutral_color).set_footer(text=f"Total: {len(content.split())}")

    async def rolecheck(ctx, send_ping: bool):
        # Define a message for sending progress updates
        progress_message = await ctx.send("Processing prerequisites...")

        # Define arrays for guild and ally uuids and names
        guild_uuids = await get_guild_uuids(guild_handle)
        guild_names, ally_names, ally_uuids, ally_divisions = [], [], [], []

        # Appending UUIDs of members of all ally guilds into one array
        for ally in allies:
            await progress_message.edit(content=f"Fetching ally UUIDs - {ally}")
            ally_uuids.extend(await get_guild_uuids(ally))
            req = await get_player_guild(ally_uuids[-1])
            gtag = " " if not req["tag"] or not req else req["tag"]
            ally_divisions.append([len(ally_uuids), gtag])  # Ally divisions marks the separation point of one guild from another in the ally_uuids array along with the guild's gtag

        # Limiting the maximum concurrency
        async def gather_with_concurrency(n, *tasks):
            semaphore = asyncio.Semaphore(n)

            async def sem_task(task):
                async with semaphore:
                    return await task

            return await asyncio.gather(*(sem_task(task) for task in tasks))

        # Get guild and ally names from their respective UUIDs
        await progress_message.edit(content="Retrieving names...")
        for _set in [[guild_uuids, guild_names], [ally_uuids, ally_names]]:
            draw, dump = _set
            async with aiohttp.ClientSession():
                tasks = await gather_with_concurrency(5,
                                                      *[
                                                          get_name_by_uuid(uuid) for uuid in draw
                                                      ])    # Gathering with a max concurrency of 5
            dump.extend(tasks)
        print(ally_names)
        # Loop through discord members
        await ctx.send("If you see the bot is stuck on a member along with an error message, forcesync member the bot is stuck on.")
        bot.admin_ids = [member.id for member in bot.admin.members]
        for member in bot.guild.members:
            # Do not check admins and bots
            if member.id in bot.admin_ids or member.bot:
                continue

            name = await name_grabber(member)
            await progress_message.edit(content=f"Checking {name} - {member}")

            # Get player data
            name, uuid = await get_mojang_profile(name)
            # Player does not exist
            if name is None:
                # Edit roles and continue loop
                await member.remove_roles(bot.member_role, bot.ally)
                await member.add_roles(bot.new_member_role)
                continue

            # Member of guild
            if name in guild_names:
                # Edit roles
                await member.add_roles(bot.member_role)
                await member.remove_roles(bot.new_member_role, bot.guest, bot.ally)


            # Member of allied guild
            elif name in ally_names:
                # Get player gtag
                position = ally_uuids.index(uuid)
                last_value = 0
                for guild_division in ally_divisions:
                    if last_value > 0:
                        if last_value < position < guild_division[0]:
                            gtag = guild_division[1]
                    elif position < guild_division[0]:
                        gtag = guild_division[1]
                    last_value = guild_division[0]

                # Set nick
                if not member.nick or gtag not in member.nick:
                    await member.edit(nick=name + f' [{gtag}]')

                # Edit roles
                await member.add_roles(bot.guest, bot.ally)
                await member.remove_roles(bot.new_member_role, bot.member_role, bot.active_role)

        # Send ping to new member role in registration channel
        if send_ping:
            await bot.get_channel(registration_channel_id).send(bot.new_member_role.mention, embed=registration_embed)

        await progress_message.edit(content="Rolecheck complete!")

    async def staffreview(ctx):
        # Define embed to edit
        embed = discord.Embed(title="Staff checkup", color=neutral_color)

        progress_message = await ctx.send("Waiting...")
        # Indefinite loop for collecting info
        while True:
            # Ask for name
            await progress_message.edit(content="What is the name of the staff member? (say 'cancel' to void this command)")

            # Wait for reply and delete message
            staff_name = await bot.wait_for("message", check=lambda
                                            x: x.author == ctx.message.author and x.channel == ctx.channel)
            await staff_name.delete()
            staff_name = staff_name.content

            # Check for cancellation
            if staff_name.lower() == "cancel":
                await progress_message.edit(content="Cancelled")
                return

            # Ask for feedback
            await progress_message.edit(content=f"What are your comments about {staff_name}?")
            # Wait for reply and delete message
            staff_comm = await bot.wait_for("message", check=lambda
                                            x: x.author == ctx.message.author and x.channel == ctx.channel)
            await staff_comm.delete()
            staff_comm = staff_comm.content

            embed.add_field(name=staff_name, value=staff_comm, inline=False)

            # Ask for another staff member
            await progress_message.edit(content="Do you want to add another staff member? (y/n)")
            # Wait for reply and delete message
            more = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel)
            await more.delete()
            more = more.content.lower()

            if more in ("y", "yes", "ye"):
                continue
            return embed

    async def delete(ctx):
        if not ctx.channel.category or ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        # Send deletion warning and gather transcript
        await ctx.send(embed=discord.Embed(title="This ticket will be deleted in 10 seconds!", color=neg_color))
        transcript = await create_transcript(ctx.channel)

        # Sleep and delete channel
        await asyncio.sleep(10)
        await discord.TextChannel.delete(ctx.channel)

        if transcript != None:
            # Log outcome
            await log_event(f"{ctx.channel.name} was deleted by {ctx.author}")
            await bot.get_channel(log_channel_id).send(file=transcript)

    async def accept(ctx):
        if ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        return accepted_staff_application_embed

    async def transcript(ctx):
        if ctx.channel.category.name not in ticket_categories.values():
            return "This command can only be used in tickets!"

        # Create transcript
        transcript = await create_transcript(ctx.channel)
        if not transcript:
            return discord.Embed(text="Transcript creation failed!", color=error_color)

        # Transcript is valid
        return transcript

    async def new(ctx):
        # Create ticket
        ticket = await create_ticket(ctx.author, f"ticket-{await name_grabber(ctx.author)}")

        # Return message with link to ticket
        return f"Click the following link to go to your ticket! <#{ticket.id}>"

    async def partner(ctx, organization_name: str):
        await ctx.send("In one message, please provide a brief description of the guild/organization being patnered.")

        # Wait for description
        description = await bot.wait_for("message", check=lambda x: x.author == ctx.message.author)
        description = description.content

        return discord.Embed(title=organization_name, description=description, color=neutral_color)

    async def deny(ctx, channel: discord.TextChannel):
        # Copy real question list and append 0th element for general critiquing
        application_questions = staff_application_questions.copy()
        application_questions[0] = "General critiquing"

        # Send the list of questions and their associated numbers
        all_questions = ""
        for key, value in application_questions.items():
            all_questions += f"**{key})** {value}\n\n"
        await ctx.send(embed=discord.Embed(title="Questions", description=all_questions, color=neutral_color))

        # Define the embed to be sent to the applicant
        denial_embed = discord.Embed(title="Your staff application has been denied!",
                                     description="The reasons have been listed below", color=error_color)

        # Loop for getting question feedback
        while True:
            while True:
                await ctx.send("What is the question number of the reply that you would like to critique?\nIf you would like to critique something in general, reply with `0`")
                question = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)

                # Try-except for checking if the given number is valid
                try:
                    question = application_questions[int(question.content)]
                    break
                # Catch KeyError if number is invalid
                except KeyError:
                    await ctx.send("Please respond with a valid question number.")

            await ctx.send(f"`{question}`\n**What was the issue that you found with their reply?**")
            critique = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)

            # Update embed and send preview
            denial_embed.add_field(
                name=question, value=critique.content, inline=False)
            await ctx.send(embed=denial_embed)

            # Ask user if they want to critique more questions and wait for reply
            await ctx.send("Would you like to critique more questions? (y/n)")
            while True:
                more = await bot.wait_for("message",
                                          check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                more = more.content.lower()

                # User does not want to critique more questions
                if more in ["n", "no"]:
                    transcript = await create_transcript(channel)

                    # Notify the user that the transcript failed
                    if not transcript:
                        return denial_embed.set_footer(text="Transcript creation failed!"), None

                    return denial_embed.set_footer(text="You may reapply in 2 weeks.\nFollowing is the transcript so that you can refer to it while reapplying."), transcript

                # Break inner loop and let user answer more questions
                break

    async def inactive(ctx):
        with ctx.channel.typing():
            # Fetch guid data
            guild_data = await get_guild_by_name(guild_handle)
            if guild_data == None:
                return invalid_guild_embed

            # Retrieve DNKL users so they can be filtered out
            dnkl_uuids = await select_all("SELECT uuid FROM dnkl")
            for tuple in dnkl_uuids:
                dnkl_uuids[dnkl_uuids.index(tuple)] = tuple[0]

            # Define dicts for each category of users
            to_promote, to_demote, inactive, residents = {}, {}, {}, {}

            # Loop through all guild members with a session to fetch names
            for member in guild_data["members"]:
                uuid = member["uuid"]

                # Gather data
                guild_rank = member["rank"]
                if uuid in dnkl_uuids:
                    guild_rank = "DNKL"
                weekly_exp = sum(member["expHistory"].values())
                name = await get_name_by_uuid(uuid)
                name += f" [{guild_rank}]\n" + \
                        str(datetime.fromtimestamp(
                            int(str(member["joined"])[:-3])))[0:10]
                guild_rank = member["rank"]
                # Remove dnkl users from list




                # Members who need to be promoted
                if guild_rank == "Member" and weekly_exp >= active_req:
                    to_promote[name] = weekly_exp
                # Active members who need to be demoted
                elif guild_rank == "Active" and weekly_exp < active_req:
                    to_demote[name] = weekly_exp
                # Members who do not meet the requirements
                elif weekly_exp < member_req:
                    if guild_rank == "Member":
                        # Filter new members who meet their requirements
                        days_since_join = (
                            datetime.now() - datetime.fromtimestamp(member["joined"] / 1000.0)).days
                        if days_since_join <= 7 and weekly_exp > new_member_req * days_since_join:
                            continue
                        inactive[name] = weekly_exp
                    elif guild_rank == "Resident":
                        residents[name] = weekly_exp

            # Define embeds array to be returned
            embeds = []

            # Loop through dicts, descriptions and colors
            for _dict, title, color in [[to_promote, "Promote the following users:", pos_color],
                                        [to_demote, "Demote the following users:",
                                            neg_color],
                                        [residents, "Following are the inactive residents:", 0xe5ba6c],
                                        [inactive, "Following are the users to be kicked:", neg_color]]:
                # Filter categories with no users
                if _dict:
                    # Sort values from lowest-highest
                    _dict = sorted(
                        _dict.items(), key=lambda item: item[1], reverse=True)
                    length = len(_dict)

                    # Create embed, append fields with data
                    embed = discord.Embed(
                        title=title, description=f"Total: {length}", color=color)
                    for user in _dict:
                        embed.add_field(
                            name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)

                        # If the embed is getting too large, append it and create a new one
                        if len(embed.fields) >= 25 and length != 25:
                            embeds.append(embed)
                            embed = discord.Embed(color=color)

                    # Append embed to array
                    embeds.append(embed)

            return embeds

    async def giveawaycreate(ctx):
        # Define progress message for asking questions
        progress_message = await ctx.send("Which channel should the giveaway be hosted in?\n\n`Please respond with a channel shortcut or ID`\n\n**At any time, you can cancel the giveaway by replying with `cancel` to one of the upcoming prompts.**")

        while True:
            # Wait for answer and check for cancellation
            destination = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            destination = destination.content.lower()
            if destination == "cancel":
                return "Giveaway cancelled!"

            # Parse channel ID
            if destination[0] == "<":
                # Try to get channel ID, returns None if doesn't exist
                destination = bot.get_channel(
                    int(re.sub(r"[\W_]+", "", destination)))
            elif destination.isnumeric():
                # Returns None if doesn't exist
                destination = bot.get_channel(int(destination))

            # If destination is invalid, ask again
            else:
                await ctx.send("Invalid channel! Please respond with a channel shortcut or ID", delete_after=3)
                continue

            # Continue with questioning
            break

        # Ask for prize
        await progress_message.edit(content=f"Sweet! The giveaway will be held in <#{destination.id}>. What is the prize going to be?\n\n`Please respond with a small description of the prize.`")

        # Wait for answer and check for cancellation
        prize = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
        prize = prize.content
        if prize == "cancel":
            return "Giveaway cancelled!"

        # Ask for no. winners
        await progress_message.edit(content=f"Ok great! The prize is set to be {prize}. How many winners should the giveaway have?\n\n`Please respond with a number from 1-20.`")

        while True:
            # Wait for answer and check for cancellation
            number_winners = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            number_winners = number_winners.content
            if number_winners == "cancel":
                return "Giveaway cancelled!"

            # Ensure no. winners is a number
            if not number_winners.isnumeric():
                await ctx.send("Invalid number of winners! Please respond with a number from 1-20", delete_after=3)
                continue

            # Ensure no. winners is within bounds
            number_winners = round(int(number_winners))
            if number_winners > 20 or number_winners < 1:
                await ctx.send("Invalid number of winners! Please respond with a number from 1-20", delete_after=3)
                continue

            break

        # Ask for duration
        await progress_message.edit(content=f"Neat! There will be {number_winners} winner(s). How long should the giveaway last?\n\n`Please enter a duration. Use an 'm' for minutes, 'd' for days, etc.`")

        while True:
            # Wait for answer and check for cancellation
            duration = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            duration = duration.content.lower()
            if duration == "cancel":
                return "Giveaway cancelled!"

            # Convert letters to seconds
            seconds_per_unit = {"m": 60, "h": 3600, "d": 86400, "w": 604800}
            try:
                end_date = datetime.utcnow() + \
                    timedelta(int(duration[:-1]) *
                              seconds_per_unit[duration[-1]])
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]
            except Exception:
                await ctx.send("Invalid duration! Please try again.", delete_after=3)
                continue

            break

        # Ask for gexp requirements
        await progress_message.edit(content=f"Awesome! The giveaway will last for {duration}. Should there be a weekly gexp requirement?\n\n`If you don't want a gexp requirement, reply with 0.`\n`Otherwise, enter a required amount of weekly gexp. Use 'k' for thousands, or 'm' for millions.`")

        while True:
            # Wait for answer and check for cancellation
            required_gexp = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            required_gexp = required_gexp.content.lower()
            if required_gexp == "cancel":
                return "Giveaway cancelled!"

            # Check user wants gexp req
            if required_gexp != 0:
                # No multiplier attached
                if required_gexp.isnumeric():
                    required_gexp = int(required_gexp)

                else:
                    unit_multiplier = {"k": 1000, "m": 1000000}
                    try:
                        required_gexp = int(
                            required_gexp[:-1]) * unit_multiplier[required_gexp[-1]]
                    except Exception:
                        await ctx.send("Invalid gexp requirement! Please try again.", delete_after=3)
                        continue

            break

        # Ask for role requirements
        await progress_message.edit(content=f"Ok, there will be a gexp requirement of {format(required_gexp, ',d')}. Should there be any role requirements for the giveaway?\n\n`Please enter role names or role IDs.`\n`If you don't want any role requirements, reply with 'none'`.\n`If entrants only need ONE of the required roles, use ',' between roles.`\n`If entrants must have ALL required roles, use '&'.`")

        while True:
            # Wait for answer and check for cancellation
            required_roles = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            required_roles = re.sub(r"\s+", "", required_roles.content)
            if required_roles.lower() == "cancel":
                return "Giveaway cancelled!"

            # Check if user wants role reqs
            if required_roles.lower() == "none":
                required_roles = []
                break

            # Convert string to list of all required roles, set requirement type
            all_roles_required = False
            if "," in required_roles:
                required_roles = required_roles.split(",")
            elif "&" in required_roles:
                all_roles_required = True
                required_roles = required_roles.split("&")
            else:
                required_roles = [required_roles]

            # Function for checking all roles are valid
            async def check_roles():
                role_ids = []
                for name in required_roles:
                    role = discord.utils.get(ctx.guild.roles, name=name)
                    if role == None:
                        await ctx.send(f"Invalid role: {name}. Please try again.", delete_after=5)
                        return False
                    role_ids.append(role.id)

                return role_ids

            # If not all roles are valid, redo
            res = await check_roles()
            if not res:
                continue

            # Set required_roles to res for simplicity
            required_roles = res
            break

        # Ask for sponsor(s)
        await progress_message.edit(content=f"Excellent! There will be {len(required_roles)} required role(s). Finally, who has sponsored this giveaway?\n\n`Please ping the sponsor(s) of this giveaway.`")
        # Wait for answer and check for cancellation
        sponsors = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
        sponsors = sponsors.content
        if sponsors == "cancel":
            return "Giveaway cancelled!"

        # Finish gexp requirement text fore embed
        gexp_requirement_text = "There is no gexp requirement." if required_gexp == 0 else f"You must have at least {format(required_gexp, ',d')} weekly gexp."

        # Finish role requirement text for embed
        if not required_roles:
            role_requirement_text = "There are no required roles."
        else:
            role_requirement_text = "You must have all of the following roles:" if all_roles_required else "You must have at least one of the following roles:"
            for id in required_roles:
                role_requirement_text += f"\n- <@&{id}>"

        # Create embed
        embed = discord.Embed(title=f"{prize}", color=0x8368ff)
        embed.set_footer(
            text=f"{number_winners} Winner(s), Ends at {end_date} UTC/GMT")
        embed.add_field(
            name="[-] Information:", value=f"Sponsored by: {sponsors} \nDuration: {duration}", inline=False)
        embed.add_field(
            name="[-] Requirements:", value=f"{role_requirement_text} \n{gexp_requirement_text}", inline=False)

        # Ask for confirmation
        await progress_message.edit(content="This is your last chance to confirm the giveaway, are you sure you want to continue? (y/n)", embed=embed)

        # Wait for answer and check confirmation
        confirmation = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
        confirmation = confirmation.content.lower()
        if confirmation not in ["y", "yes"]:
            return "Giveaway cancelled!"

        # Send the giveaway in destination channel and add 🎉 reaction
        msg = await destination.send(f"{bot.giveaways_events.mention} React with 🎉 to enter! If you win this giveaway, make a ticket to claim it!", embed=embed)
        await msg.add_reaction("\U0001F389")

        # Enter data into db (Make required roles a str for db)
        required_roles = " ".join([str(role) for role in required_roles])
        await insert_new_giveaway(msg.id, destination.id, prize, number_winners, end_date, required_gexp, all_roles_required, required_roles, sponsors)

        # Return confirmation
        return f"Ok! The giveaway has been set up in <#{destination.id}>!"

    async def giveawaylist():
        all_giveaways = await select_all("SELECT prize, channel_id, message_id, number_winners, time_of_finish FROM giveaways")

        # There have been no recent giveaways
        if not all_giveaways:
            return discord.Embed(title="There have been no giveaways in the last 10 days!",
                                 description="To make a new giveaway, use the command `,giveawaycreate`",
                                 color=neg_color)
        else:
            # Define embed
            embed = discord.Embed(title="Giveaways:",
                                  description="Listed below are all giveaways from the last 10 days.",
                                  color=neutral_color)

            # Add info to embed
            for giveaway in all_giveaways:
                prize, channel_id, message_id, number_winners, finish = giveaway
                embed.add_field(name=f"{prize}",
                                value=f"Channel: <#{channel_id}> \nMessage ID: {message_id} \nNumber Of Winners: {number_winners} \nEnds At: {finish}")

            return embed
