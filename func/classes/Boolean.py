# The following file contains: rolecheck, dnkllist

from __main__ import bot
from concurrent.futures import ThreadPoolExecutor
import asyncio
import requests

from func.utils.discord_utils import name_grabber
from func.utils.request_utils import get_guild_uuids, get_mojang_profile, get_player_guild, session_get_name_by_uuid
from func.utils.consts import registration_embed


class Boolean:
    def __init__(self, boolean: bool):
        self.boolean = boolean

    async def rolecheck(self, ctx):
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

    # async def dnkllist(self):
    #     return True
