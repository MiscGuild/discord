# The following file contains: weeklylb, dnkllist, rolecheck, staffreview, delete, accept, transcript, new, partner, deny, inactive, giveawaycreate, giveawaylist

import asyncio
import re
from __main__ import bot
from datetime import datetime, timedelta

import aiohttp
import discord
import discord.ui

from src.func.Union import Union
from src.utils.consts import (accepted_staff_application_embed, active_req,
                              allies, error_color, guild_handle,
                              invalid_guild_embed, log_channel_id, member_req,
                              milestone_emojis, milestones_channel, neg_color,
                              neutral_color, pos_color, ticket_deleted_embed,
                              registration_channel_id, registration_embed,
                              staff_application_questions, ticket_categories)
from src.utils.db_utils import insert_new_giveaway, select_all
from src.utils.discord_utils import (create_ticket, create_transcript,
                                     get_ticket_creator, log_event,
                                     name_grabber)
from src.utils.minecraft_utils import get_hypixel_player_rank
from src.utils.request_utils import (get_guild_by_name, get_guild_uuids,
                                     get_hypixel_player, get_jpg_file,
                                     get_mojang_profile, get_name_by_uuid,
                                     get_player_guild)


class General:
    async def weeklylb(ctx):
        async with ctx.channel.typing():
            # Get guild data
            guild_data = await get_guild_by_name(guild_handle)

            if not guild_data:
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
            text = "&f&lWeekly Top&r%5Cn"
            count = 0
            for i in member_gexp[:10]:
                count += 1
                user_data = i
                name = await get_name_by_uuid(user_data[0])
                rank, _ = await get_hypixel_player_rank(await get_hypixel_player(uuid=user_data[0]))

                # Add new entry to image content
                text += f"&6{count}. {rank} {name} &2{format(user_data[1], ',d')} Guild Experience"
                # Add new line
                if count < 10:
                    text += "%5Cn"

            # Replace characters for URL
            text = text.replace("+", "%2B")
            text = text.replace("&", "%26")
            text = text.replace(" ", "%20")
            text = text.replace(",", "%2C")

            # Return image
            return await get_jpg_file(f"https://fake-chat.matdoes.dev/render.png?m=custom&d={text}&t=1")

    async def dnkllist(ctx):
        # Fetch all rows
        rows = await select_all("SELECT * FROM dnkl")

        if not rows:
            return discord.Embed(title="No entries!", description="There are no users on the do-not-kick-list!",
                                 color=neg_color)

        # Create embed
        content = ""
        for _set in rows:
            _, _, username = _set
            content += f"{username}\n"

        return discord.Embed(title="The people on the do-not-kick-list are as follows:", description=content,
                             color=neutral_color).set_footer(text=f"Total: {len(content.split())}")

    async def rolecheck(ctx, send_ping: bool):
        # Define a message for sending progress updates
        progress_message = await ctx.send("Processing prerequisites...")

        # Define arrays for guild and ally uuids and names
        guild_members = (await get_guild_by_name(guild_handle))['members']
        guild_uuids = await get_guild_uuids(guild_handle)
        guild_names, ally_names, ally_uuids, ally_divisions = [], [], [], []

        # Appending UUIDs of members of all ally guilds into one array
        for ally in allies:
            await progress_message.edit(content=f"Fetching ally UUIDs - {ally}")
            ally_uuids.extend(await get_guild_uuids(ally))
            req = await get_player_guild(ally_uuids[-1])
            gtag = " " if not req["tag"] or not req else req["tag"]
            ally_divisions.append([len(ally_uuids),
                                   gtag])  # Ally divisions marks the separation point of one guild from another in the ally_uuids array along with the guild's gtag

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
                tasks = await gather_with_concurrency(2,
                                                      *[
                                                          get_name_by_uuid(uuid) for uuid in draw
                                                      ])  # Gathering with a max concurrency of 5
            dump.extend(tasks)
        # Loop through discord members
        await ctx.send("If you see the bot is stuck on a member along with an error message, "
                       "forcesync member the bot is stuck on.")
        bot.admin_ids = [member.id for member in bot.admin.members]
        for member in bot.guild.members:
            # Do not check admins and bots
            if member.id in bot.admin_ids or member.bot:
                continue

            name = await name_grabber(member)
            await progress_message.edit(content=f"Checking {name} - {member}")
            # Member of guild
            if name in guild_names:
                # Checks if the member meets the requirements for the active rank
                for guild_member in guild_members:
                    if guild_uuids[guild_names.index(name)] == guild_member['uuid']:  # Finds the users uuid from their name using the list and finds their corresponding hypixel data
                        weekly_exp = sum(guild_member["expHistory"].values())
                        if weekly_exp >= active_req:  # If the member meets the active requirements
                            await member.add_roles(bot.active_role)
                        elif weekly_exp < active_req and bot.active_role in member.roles:  # If the member doesn't meet active requirements but has the active role
                            await member.remove_roles(bot.active_role)

                # Edit roles
                await member.add_roles(bot.member_role)
                await member.remove_roles(bot.new_member_role, bot.guest, bot.ally)
                continue

            # Get player data
            name, uuid = await get_mojang_profile(name)
            if not name:
                # Edit roles and continue loop
                await member.remove_roles(bot.member_role, bot.ally, bot.guest)
                await member.add_roles(bot.new_member_role)
                continue

            # Member of an ally guild
            if name in ally_names:
                # Get player gtag
                position = ally_uuids.index(uuid)
                last_value = 1
                for guild_division in ally_divisions:
                    if last_value > 1:
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
                continue

            # Guests
            else:
                await member.add_roles(bot.guest)
                await member.remove_roles(bot.new_member_role, bot.member_role, bot.active_role, bot.ally)
                continue

        # Send ping to new member role in registration channel
        if send_ping:
            await bot.get_channel(registration_channel_id).send(bot.new_member_role.mention, embed=registration_embed)

        await progress_message.edit(content="Rolecheck complete!")


    async def delete(ctx):
        embed = discord.Embed(title="This ticket will be deleted in 10 seconds!", color=neg_color)
        if ("MILESTONES" == ctx.channel.category.name) or not ctx.channel.category or ctx.channel.category.name not in ticket_categories.values():
            return "This command cannot be used here"
        if ctx.channel.category.name == ticket_categories["registrees"]:
            member = await get_ticket_creator(ctx.channel)
            if member:
                ign, uuid = await get_mojang_profile(await name_grabber(member))
                await Union(user=member).sync(ctx, ign, None, True)
                embed.set_footer(text=f"{ign}'s roles have been updated automatically!")

        # Send deletion warning and gather transcript
        await ctx.respond(embed=embed)
        transcript = await create_transcript(ctx.channel)

        # Sleep and delete channel
        await asyncio.sleep(10)
        await discord.TextChannel.delete(ctx.channel)

        if transcript:
            # Log outcome
            await log_event(f"{ctx.channel.name} was deleted by {ctx.author}")
            try:
                await (await bot.fetch_user(ctx.channel.topic.split("|")[0])).send(embed=ticket_deleted_embed.set_footer(text=ctx.channel.name), file=transcript)
            except:
                pass
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
            return discord.Embed(title="Transcript creation failed!", color=error_color)

        # Transcript is valid
        return transcript

    async def new(ctx):
        # Create ticket
        ticket = await create_ticket(ctx.author, f"ticket-{await name_grabber(ctx.author)}")

        # Return message with link to ticket
        return f"Click the following link to go to your ticket! <#{ticket.id}>"

    async def partner(ctx, organization_name: str):
        await ctx.send("In one message, please provide a brief description of the guild/organization being partnered.")
        # Wait for description
        description = (await bot.wait_for("message", check=lambda x: x.author == ctx.message.author)).content

        await ctx.send("Please provide the logo of the organization/guild. (Please provide the URL. If they don't have a logo, type `None`)")
        # Wait for Logo
        logo = (await bot.wait_for("message", check=lambda x: x.author == ctx.message.author)).content if (await bot.wait_for("message", check=lambda x: x.author == ctx.message.author)).content.lower() != "none" else None
        if logo:
            return discord.Embed(title=organization_name, description=description, color=neutral_color).set_thumbnail(url=logo)
        return discord.Embed(title=organization_name, description=description, color=neutral_color)


    async def deny(ctx, channel: discord.TextChannel):
        # Copy real question list and append 0th element for general critiquing
        application_questions = staff_application_questions.copy()
        application_questions[0] = "General critiquing"
        message = await channel.fetch_message(int(channel.topic.split("|")[1]))
        member = await get_ticket_creator(channel)
        await ctx.send(embed=message.embeds[0].set_footer(text=""))

        # Define the embed to be sent to the applicant
        denial_embed = discord.Embed(title="Your staff application has been denied!",
                                     description="The reasons have been listed below", color=error_color)

        # Loop for getting question feedback
        while True:
            while True:
                await ctx.send(
                    "What is the question number of the reply that you would like to critique?\nIf you would like to critique something in general, reply with `0`")
                question = await bot.wait_for("message",
                                              check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                # Try-except for checking if the given number is valid
                try:
                    question = application_questions[int(question.content)]
                    break
                # Catch KeyError if number is invalid
                except:
                    await ctx.send("Please respond with a valid question number.")

            await ctx.send(f"`{question}`\n**What was the issue that you found with {member.nick}'s reply?**")
            critique = await bot.wait_for("message",
                                          check=lambda x: x.channel == ctx.channel and x.author == ctx.author)

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

                    return denial_embed.set_footer(
                        text="You may reapply in 2 weeks.\nFollowing is the transcript so that you can refer to it while reapplying."), transcript

                # Break inner loop and let user answer more questions
                break

    async def inactive(ctx):
        with ctx.channel.typing():
            # Fetch guid data
            guild_data = await get_guild_by_name(guild_handle)
            if not guild_data:
                return invalid_guild_embed

            # Retrieve DNKL users so they can be filtered out
            dnkl_uuids = await select_all("SELECT uuid FROM dnkl")
            for tuple in dnkl_uuids:
                dnkl_uuids[dnkl_uuids.index(tuple)] = tuple[0]

            # Define dicts for each category of users
            to_promote, to_demote, inactive, residents, skipped_users = {}, {}, {}, {}, []

            # Loop through all guild members with a session to fetch names
            for member in guild_data["members"]:
                uuid = member["uuid"]

                # Gather data
                guild_rank = member["rank"]
                if uuid in dnkl_uuids:
                    guild_rank = "DNKL"
                weekly_exp = sum(member["expHistory"].values())
                name = await get_name_by_uuid(uuid)
                if not name:
                    skipped_users.append(uuid)
                    continue
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
                        if days_since_join <= 7 and weekly_exp > member_req / 7 * days_since_join:
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
                            if skipped_users:
                                embed.set_footer(
                                    text=f"Omitted {len(skipped_users)} user(s) to avoid an error!\nUUID(s):\n{str(*skipped_users)}")
                    # Append embed to array
                    embeds.append(embed)

            return embeds

    async def giveawaycreate(ctx):
        # Define progress message for asking questions
        progress_message = await ctx.send(
            "**Which channel should the giveaway be hosted in?**\n\n`Please respond with a channel shortcut or ID`\n\n**At any time, you can cancel the giveaway by replying with `cancel` to one of the upcoming prompts.**")

        while True:
            # Wait for answer and check for cancellation
            destination = await bot.wait_for("message",
                                             check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            destination = destination.content.lower()
            if destination == "cancel":
                return "Giveaway cancelled!"

            # Parse channel ID
            if destination[0] == "<":
                # Try to get channel ID, returns None if it doesn't exist
                destination = bot.get_channel(
                    int(re.sub(r"[\W_]+", "", destination)))
            elif destination.isnumeric():
                # Returns None if it doesn't exist
                destination = bot.get_channel(int(destination))

            # If destination is invalid, ask again
            else:
                await ctx.send("Invalid channel! Please respond with a channel shortcut or ID", delete_after=3)
                continue

            # Continue with questioning
            break

        # Ask for prize
        await progress_message.edit(
            content=f"Sweet! The giveaway will be held in <#{destination.id}>.\n\n**What is the prize going to be?**\n\n`Please respond with a small description of the prize.`")

        # Wait for answer and check for cancellation
        prize = await bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
        prize = prize.content
        if prize == "cancel":
            return "Giveaway cancelled!"

        # Ask for no. winners
        await progress_message.edit(
            content=f"Ok great! The prize is set to be {prize}.\n\n**How many winners should the giveaway have?**\n\n`Please respond with a number from 1-20.`")

        while True:
            # Wait for answer and check for cancellation
            number_winners = await bot.wait_for("message",
                                                check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
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
        await progress_message.edit(
            content=f"Neat! There will be {number_winners} winner(s).\n\n**How long should the giveaway last?**\n\n`Please enter a duration. Use a 's' for seconds, 'm' for minutes and 'd' for days`")

        while True:
            # Wait for answer and check for cancellation
            duration = await bot.wait_for("message",
                                          check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            duration_visual = duration = duration.content.lower()
            # Convert the duration to seconds
            if duration[:-2:-1] == "s":
                duration = int(duration[:-1])
            elif duration[:-2:-1] == "m":
                duration = int(duration[:-1])*60
            elif duration[:-2:-1] == "d":
                duration = int(duration[:-1])*86400
            if duration == "cancel":
                return "Giveaway cancelled!"
            try:
                end_date = datetime.utcnow() + timedelta(seconds=duration)
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-7]
            except Exception:
                await ctx.send("Invalid duration! Please try again.", delete_after=3)
                continue
            break

        # Ask for gexp requirements
        await progress_message.edit(
            content=f"Awesome! The giveaway will last for {duration_visual}.\n\n**Should there be a weekly gexp requirement?**\n\n`If you don't want a gexp requirement, reply with 0.`\n`Otherwise, enter a required amount of weekly gexp. Use 'k' for thousands, or 'm' for millions.`")

        while True:
            # Wait for answer and check for cancellation
            required_gexp = await bot.wait_for("message",
                                               check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
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
        await progress_message.edit(
            content=f"Ok, there will be a gexp requirement of {format(required_gexp, ',d')}.\n\n**Should there be any role requirements for the giveaway?**\n\n`Please enter role names or role IDs.`\n`If you don't want any role requirements, reply with 'None'`.\n`If entrants only need ONE of the required roles, use ',' between roles.`\n`If entrants must have ALL required roles, use '&'.`")

        while True:
            # Wait for answer and check for cancellation
            required_roles = await bot.wait_for("message",
                                                check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            required_roles = re.sub(r"\s+", "", required_roles.content)
            if required_roles.lower() == "cancel":
                return "Giveaway cancelled!"

            # Check if user wants role reqs
            if required_roles.lower() == "none":
                required_roles = []
                all_roles_required = False
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
                    if not role:
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
        await progress_message.edit(
            content=f"Excellent! There will be {len(required_roles)} required role(s).\n\n**Finally, who has sponsored this giveaway?**\n\n`Please ping the sponsor(s) of this giveaway.`")
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
            name="[-] Information:", value=f"Sponsored by: {sponsors} \nDuration: {duration_visual}", inline=False)
        embed.add_field(
            name="[-] Requirements:", value=f"{role_requirement_text} \n{gexp_requirement_text}", inline=False)

        # Ask for confirmation
        await progress_message.edit(
            content="This is your last chance to confirm the giveaway, are you sure you want to continue? (y/n)",
            embed=embed)

        # Wait for answer and check confirmation
        confirmation = await bot.wait_for("message",
                                          check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
        confirmation = confirmation.content.lower()
        if confirmation not in ["y", "yes"]:
            return "Giveaway cancelled!"

        # Send the giveaway in destination channel and add 🎉 reaction
        msg = await destination.send(
            f"{bot.giveaways_events.mention} React with 🎉 to enter! If you win this giveaway, make a ticket to claim it!",
            embed=embed)
        await msg.add_reaction("\U0001F389")

        # Enter data into db (Make required roles a str for db)
        required_roles = " ".join([str(role) for role in required_roles])
        await insert_new_giveaway(msg.id, destination.id, prize, number_winners, end_date, required_gexp,
                                  all_roles_required, required_roles, sponsors)

        # Return confirmation
        return f"Ok! The giveaway has been set up in <#{destination.id}>!"

    async def giveawaylist(ctx):
        all_giveaways = await select_all(
            "SELECT prize, channel_id, message_id, number_winners, time_of_finish FROM giveaways")

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

    async def add_milestone(ctx, gamemode, milestone):
        member = await get_ticket_creator(ctx.channel)
        name = await name_grabber(member)
        channel = ctx.channel

        class MilestoneTypeSelect(discord.ui.Select):
            def __init__(self):
                super().__init__()
                for key, value in milestone_emojis.items():
                    self.add_option(label=key.replace("_", " ").title(), emoji=f"{value}")

            # Override default callback
            async def callback(self, interaction: discord.Interaction):
                # Set option var and delete Select, so it cannot be used twice
                option = list(interaction.data.values())[0][0]
                option_emoji = milestone_emojis.get(option)

                await interaction.response.send_message(f"**Milestone Category:** {option}"
                                                        f"\n**What is {name}'s milestone?**\n"
                                                        f"{emoji}{name}.... (Complete the sentence)")
                milestone = await bot.wait_for("message",
                                               check=lambda
                                                   x: x.channel == channel and x.author == interaction.user)
                await milestone_ticket_update(ctx, channel, option_emoji, milestone.content)

        async def milestone_ticket_update(ctx, channel, emoji, milestone):
            milestone_string = f"{emoji} {member.mention} {milestone}|"
            channel_description = channel.topic + milestone_string
            await ctx.send(
                "Please give the bot up to 10 minutes to add the milestone. Once it has done it, you'll receive a completion message.")
            await channel.edit(topic=str(channel_description))
            embed = discord.Embed(title="Milestone Registered!",
                                  description=milestone_string[:-1], color=neutral_color)

            await ctx.send(embed=embed)


        if gamemode and milestone:
            if gamemode.upper() in [x for x in milestone_emojis.keys()]:
                emoji = milestone_emojis.get(gamemode.upper())
                await milestone_ticket_update(ctx, channel, emoji, milestone)
            else:
                embed= discord.Embed(title="Invalid gamemode inserted!",
                                    description=f"All the possible gamemodes are as follows:",
                                     color= neg_color).set_footer(
                    text=f"{f'{chr(10)}'.join([x.title() for x in milestone_emojis.keys()])}")  #   chr(10) is a new line character
                await ctx.respond(embed=embed)
            return
        # Create view and embed, send to ticket
        view = discord.ui.View()
        view.add_item(MilestoneTypeSelect())
        embed = discord.Embed(title=f"Under what category does {name}'s milestone fall?",
                              description="Please select your reason from the dropdown given below!",
                              color=neutral_color)
        return embed, view

    async def update_milestone(ctx):
        member = await get_ticket_creator(ctx.channel)
        name = await name_grabber(member)

        channel_description_list = ctx.channel.topic.split(
            "|")  # Has a list in the format ["MEMBER ID","MILESTONE 1", "MILESTONE 2"....}
        all_milestones = ctx.channel.topic.split('|')[
                         1:-1]  # Omits the Member ID from channel_description_list and also an empty string from the end

        class MilestoneTypeSelect(discord.ui.Select):
            def __init__(self):
                super().__init__()
                index = 1
                for milestone in all_milestones:
                    category = [k for k, v in milestone_emojis.items() if v == milestone.split(" ")[0]][0]
                    self.add_option(label=f"{name} {milestone.split(' ', 2)[2]}",
                                    value=f"{index} {category} {milestone.split(' ', 2)[2]}",
                                    emoji=milestone.split(" ")[0])
                    index += 1

            # Override default callback
            async def callback(self, interaction: discord.Interaction):
                # Set option var
                option = list(interaction.data.values())[0][0].split(' ', 2)
                index = int(option[0])
                category = option[1]
                old_milestone = option[2]
                emoji = milestone_emojis[category]

                await interaction.response.send_message(
                    f"**Milestone Category:** {category}\n"
                    f"**Old Milestone:** {old_milestone}"
                    f"\n**What is {name}'s milestone?**\n"
                    f"{emoji}{name}.... (Complete the sentence)")
                milestone = await bot.wait_for("message",
                                               check=lambda
                                                   x: x.channel == ctx.channel and x.author == interaction.user)
                new_milestone_message = f"{emoji} {member.mention} {milestone.content}"
                channel_description_list[index] = new_milestone_message

                await ctx.channel.edit(topic="|".join(channel_description_list))
                embed = discord.Embed(title="Milestone Registered!",
                                      description=new_milestone_message, color=neutral_color)

                await ctx.send(embed=embed)

        # Create view and embed, send to ticket
        view = discord.ui.View()
        view.add_item(MilestoneTypeSelect())
        embed = discord.Embed(title=f"Which of the following milestones would you like to update?",
                              description="Please select your reason from the dropdown given below!",
                              color=neutral_color)
        return embed, view

    async def compile_milestones(ctx):
        day_number = 86 + round((datetime.utcnow() - datetime.strptime("2022/05/15", "%Y/%m/%d")).days / 7)

        milestone_message = f"**Weekly Milestones**\nThis is week __{day_number}__ of weekly milestones\n\n"
        count = 0
        for channel in bot.guild.text_channels:
            if channel.category.name == ticket_categories["milestone"]:
                player_milestones = channel.topic.split("|")[1:-1]
                for milestone in player_milestones:
                    count += 1
                    milestone_message = milestone_message + milestone + "!\n"
                    if count >= 15:
                        await bot.get_channel(milestones_channel).send(milestone_message)
                        milestone_message = ""
                        count = 0
                await discord.TextChannel.delete(channel)
        milestone_message = milestone_message + "\n**Congrats to everyone this week. If you wish to submit a milestone, look over at <#650248396480970782>!**"
        await bot.get_channel(milestones_channel).send(milestone_message)
        return f"{count} milestones have been compiled and sent in {bot.get_channel(milestones_channel)}"

