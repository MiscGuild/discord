# The following file contains: weeklylb, dnkllist, rolecheck

from __main__ import bot
import asyncio
from concurrent.futures import ThreadPoolExecutor
import discord
import requests

from func.utils.discord_utils import name_grabber
from func.utils.minecraft_utils import get_hypixel_player_rank
from func.utils.request_utils import get_mojang_profile, get_player_guild, get_guild_by_name, get_name_by_uuid, get_hypixel_player, get_gtop, get_guild_uuids, session_get_name_by_uuid
from func.utils.db_utils import select_all
from func.utils.consts import neg_color, neutral_color, invalid_guild_embed, registration_embed


class Func:
    async def weeklylb(ctx):
        async with ctx.channel.typing():
            # Get guild data
            guild_data = await get_guild_by_name(bot.guild_name)

            if guild_data == None:
                return invalid_guild_embed

            member_gexp = {}

            # Loop through all guild members' gexp, adding it to dict
            for member in guild_data["members"]:
                member_gexp[member["uuid"]] = sum(member["expHistory"].values())

            # Sort member gexp
            member_gexp = sorted(member_gexp.items(), key=lambda item: item[1], reverse=True)

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
                    url +="%5Cn"

            # Replace characters for URL
            url = url.replace("+", "%2B")
            url = url.replace("&", "%26")
            url = url.replace(" ", "%20")
            url = url.replace(",", "%2C")

            # Return image
            return await get_gtop(f"https://chat.miscguild.xyz/render.png?m=custom&d={url}&t=1")

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

    async def rolecheck(self, ctx, send_ping: bool):
        # Define a message for sending progress updates
        progress_message = await ctx.send("Processing prerequisites...")

        # Define arrays for guild and ally uuids and names
        guild_uuids = await get_guild_uuids(bot.guild_name)
        guild_names, ally_names, ally_uuids = [], [], []
        
        for ally in bot.misc_allies:
            await progress_message.edit(content=f"Fetching ally UUIDs - {ally}")
            ally_uuids.extend(await get_guild_uuids(ally))

        # Get guild and ally names
        await progress_message.edit(content="Retrieving names...")
        for _set in [[guild_uuids, guild_names], [ally_uuids, ally_names]]:
            draw, dump = _set
            with ThreadPoolExecutor(max_workers=10) as executor:
                with requests.Session() as session:
                    # Set session params before calling fetch
                    loop = asyncio.get_event_loop()
                    tasks = [
                        # Pass multiple args to fetch
                        loop.run_in_executor(
                            executor,
                            session_get_name_by_uuid,
                            *(session, uuid)
                        )
                        for uuid in draw
                    ]
                    for response in await asyncio.gather(*tasks):
                        dump.append(response)


        # Loop through discord members, send warning message
        await ctx.send("If you see the bot is stuck on a member, forcesync that user in the event of an error.")
        for member in bot.guild.members:
            # Do not check admins and bots
            if member.id in bot.admin_ids or member.bot: continue

            name = await name_grabber(member)
            await progress_message.edit(content=f"Checking {name} - {member}")

            # Get player data
            name, uuid = await get_mojang_profile(name)
            # Player does not exist
            if name == None:
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
                guild = await get_player_guild(uuid)
                gtag = " " if len(guild["guild"]) < 2 or not guild["tag"] else guild["tag"]

                # Set nick
                if not member.nick or gtag not in member.nick:
                    await member.edit(nick=name + gtag)

                # Edit roles
                await member.add_roles(bot.guest, bot.ally)
                await member.remove_roles(bot.new_member_role, bot.member_role, bot.active_role, bot.inactive_role)


        # Send ping to new member role in registration channel
        if self.boolean: await bot.registration_channel.send(bot.new_member_role.mention, embed=registration_embed)

        await progress_message.edit(content="Rolecheck complete!")
