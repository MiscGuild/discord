import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import aiohttp
import discord
import requests
from discord.ext import commands

from cogs.utils import utilities as utils


class staff(commands.Cog, name="Staff"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['req', 'requirement'])
    async def requirements(self, ctx):
        """Lists the requirements
        """
        embed = discord.Embed(title="Miscellaneous Guild Requirements",
                              description="These requirements are subject to change!",
                              color=0x8368ff)
        embed.add_field(name="Active", value=f"•  {format(self.bot.active, ',d')} Weekly Guild Experience",
                        inline=False)
        embed.add_field(name="Do Not Kick List Eligibility",
                        value=f"•  {format(self.bot.dnkl, ',d')} Weekly Guild Experience", inline=False)
        embed.add_field(name="Resident", value=f"•  {format(self.bot.resident_req, ',d')} Weekly Guild Experience",
                        inline=False)
        embed.add_field(name="Member", value=f"•  {format(self.bot.inactive, ',d')} Weekly Guild Experience",
                        inline=False)
        embed.add_field(name="New Member", value=f"•  {format(self.bot.new_member, ',d')} Daily Guild Experience",
                        inline=False)
        embed.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                              "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['res'])
    async def resident(self, ctx):
        """Lists the methods to get the resident rank
        """
        embed = discord.Embed(title='How to get Resident?',
                              description='To be eligible for Resident, you must be one of the following',
                              color=0x8368ff)
        embed.add_field(name="Youtuber",
                        value="If you're a youtuber with more than 5,000 subscribers, you aren't subject to any guild requirements.",
                        inline=False)
        embed.add_field(name="Rich Kid", value="Spend Money on the guild by doing giveaways, sponsoring events!",
                        inline=False)
        embed.add_field(name="Server Booster", value="Boost the guild discord!",
                        inline=False)
        embed.add_field(name="GvG Team", value="Be an exceptional GvG player.",
                        inline=False)
        embed.set_footer(
            text=f"Everyone who has the resident rank must get {format(self.bot.resident_req, ',d')} weekly guild experience! (Except YouTubers)")
        await ctx.send(embed=embed)

    @commands.command(aliases=['ticket'])
    async def tickets(self, ctx):
        """Explains the entire ticket system
        """
        embed = discord.Embed(title="How to create a ticket?",
                              color=0x8368ff)
        embed.add_field(name="Go to #🎟-tickets-🎟",
                        value="#🎟-tickets-🎟 is located in the noticeboard category",
                        inline=False)
        embed.add_field(name="Tickets can be created for the following reasons",
                        value="> Discord Nick/Role & Tag Change/\n"
                              "> Do not kick list\n"
                              "> Problems/Queries/Complaint/Suggestion\n"
                              "> Reporting a player\n"
                              "> Milestone\n"
                              "> Staff Application\n"
                              "> Event\n"
                              "> Other",
                        inline=False)
        embed.add_field(name="Click the button under the message sent by @Miscellaneous",
                        value="The following image shows you what you need to click.",
                        inline=False)
        embed.set_image(
            url=f"https://media.discordapp.net/attachments/813075018820222976/870799273892147230/unknown.png?width=1316&height=671")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("Staff")
    async def inactive(self, ctx):
        """Prints a list of users who need to be promoted, demoted, warned and kicked!
        """
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = utils.get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.hypixel.net/guild?key={api}&name=Miscellaneous') as resp:
                g = await resp.json(content_type=None)
                await session.close()

        cursor = await self.bot.db.execute("SELECT username FROM DNKL")
        rows = await cursor.fetchall()
        await cursor.close()

        dnkl_names = []
        for tuple in rows:
            username = tuple[0]
            dnkl_names.append(username)

        activearray = {}
        activedemotearray = {}
        inactivearray = {}
        veteranarray = {}
        exp = 0
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 15 seconds`")
        async with ctx.channel.typing():
            for i in range(len(g['guild']['members'])):
                expHistory = sum(g['guild']['members'][i]['expHistory'].values())
                rank = g['guild']['members'][i]['rank']
                joined = g['guild']['members'][i]['joined']
                if expHistory >= self.bot.active and rank == "Member":
                    uuid = g['guild']['members'][i]['uuid']
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                                f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                            a = await resp.json(content_type=None)
                            await session.close()
                    name = a['name']
                    time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                    dt = (time[0:10])
                    if name in dnkl_names:
                        name = name + f'[DNKL]\n{dt}'
                    else:
                        name = name + f'[{rank}]\n{dt}'
                    exp += expHistory
                    activearray[name] = exp
                    exp = 0
                elif expHistory < self.bot.active and rank == "Active":
                    uuid = g['guild']['members'][i]['uuid']
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                                f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                            a = await resp.json(content_type=None)
                            await session.close()
                    name = a['name']
                    time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                    dt = (time[0:10])
                    if name in dnkl_names:
                        name = name + f'[DNKL]\n{dt}'
                    else:
                        name = name + f'[{rank}]\n{dt}'
                    exp += expHistory
                    activedemotearray[name] = exp
                    exp = 0
                elif expHistory < self.bot.inactive:
                    if rank == "Member":
                        uuid = g['guild']['members'][i]['uuid']
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                    f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                                a = await resp.json(content_type=None)
                        time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                        name = a['name']
                        dt = (time[0:10])
                        if name in dnkl_names:
                            name = name + f'[DNKL]\n{dt}'
                        else:
                            name = name + f'[{rank}]\n{dt}'
                        exp += expHistory
                        inactivearray[name] = exp
                        exp = 0
                    elif rank == "Resident":
                        if expHistory < self.bot.resident_req:
                            uuid = g['guild']['members'][i]['uuid']
                            async with aiohttp.ClientSession() as session:
                                async with session.get(
                                        f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                                    a = await resp.json(content_type=None)
                            time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                            name = a['name']
                            dt = (time[0:10])
                            if name in dnkl_names:
                                name = name + f'[DNKL]\n{dt}'
                            else:
                                name = name + f'[{rank}]\n{dt}'
                            exp += expHistory
                            veteranarray[name] = exp
                            exp = 0
                else:
                    pass
            ActivesortedList = sorted(activearray.items(), key=lambda x: x[1], reverse=True)
            ActiveDemoteSortedList = sorted(activedemotearray.items(), key=lambda x: x[1], reverse=True)
            VeteransortedList = sorted(veteranarray.items(), key=lambda x: x[1], reverse=True)
            InactivesortedList = sorted(inactivearray.items(), key=lambda x: x[1], reverse=True)

            await msg.edit(content="**Please wait!**\n `The embeds are being sent!`")

            '---------------------------------------------------------------ACTIVE PROMOTION------------------------------------------------------------------------------'
            embed = discord.Embed(title=f"Promote the following users:",
                                  description=f"Total: {len(ActivesortedList)}", color=0x43b581)
            y = 0
            if len(ActivesortedList) <= 25:
                for user in ActivesortedList:
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)
                await ctx.send(embed=embed)
            else:
                for user in ActivesortedList:
                    y = y + 1
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)

                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0x43b581)
                    elif y == len(ActivesortedList):
                        await ctx.send(embed=embed)

            '---------------------------------------------------------------ACTIVE DEMOTION-------------------------------------------------------------------------------'
            embed = discord.Embed(title=f"Demote the following users:",
                                  description=f"Total: {len(ActiveDemoteSortedList)}", color=0xf04747)
            z = 0
            if len(ActiveDemoteSortedList) <= 25:
                for user in ActiveDemoteSortedList:
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)
                await ctx.send(embed=embed)
            else:
                for user in ActiveDemoteSortedList:
                    z = z + 1
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)

                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0xf04747)
                    elif z == len(ActiveDemoteSortedList):
                        await ctx.send(embed=embed)

            '---------------------------------------------------------------VETERAN WARNING-------------------------------------------------------------------------------'
            embed = discord.Embed(
                title=f"Following are the residents who don't meet the requirements:",
                description=f"Total: {len(VeteransortedList)}", color=0xe5ba6c)
            w = 0
            if len(VeteransortedList) <= 25:
                for user in VeteransortedList:
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)
                await ctx.send(embed=embed)
            else:
                for user in VeteransortedList:
                    w = w + 1
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)

                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0xe5ba6c)
                    elif w == len(VeteransortedList):
                        await ctx.send(embed=embed)

            '---------------------------------------------------------------INACTIVE MEMBERS------------------------------------------------------------------------------'
            embed = discord.Embed(title=f"The users to be kicked are as follows:",
                                  description=f"Total: {len(InactivesortedList)}", color=0xf04747)
            x = 0
            if len(InactivesortedList) <= 25:
                for user in InactivesortedList:
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)
                await ctx.send(embed=embed)
            else:
                for user in InactivesortedList:
                    x = x + 1
                    embed.add_field(name=f"{user[0]}", value=f"```cs\n{format(user[1], ',d')}```", inline=True)

                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0xf04747)
                    elif x == len(InactivesortedList):
                        await ctx.send(embed=embed)

            await msg.delete()

    @commands.command(aliases=['fs'])
    @commands.has_role("Staff")
    async def forcesync(self, ctx, member: discord.Member, name):
        """Used to forcefully sync a player's IGN
        """
        moderator = discord.utils.get(ctx.guild.roles, name="Moderator")
        admin = discord.utils.get(ctx.guild.roles, name="Admin")
        if moderator or admin in ctx.author.roles:
            ign, uuid = await utils.get_dispnameID(name)
            if ign is None:
                await ctx.send('Please enter a valid ign!')
            else:
                guild_name = await utils.get_guild(name)
                newmember = discord.utils.get(ctx.guild.roles, name="New Member")
                guest = discord.utils.get(ctx.guild.roles, name="Guest")
                member_ = discord.utils.get(ctx.guild.roles, name="Member")
                awaiting_app = discord.utils.get(ctx.guild.roles, name="Awaiting Approval")
                ally = discord.utils.get(ctx.guild.roles, name="Ally")

                await member.edit(nick=ign)

                if guild_name == "Miscellaneous":
                    await member.remove_roles(guest, awaiting_app, newmember)
                    await member.add_roles(member_)
                    embed = discord.Embed(title=f"{member.name}'s nick and role were successfully changed!",
                                          color=0x8368ff)
                    embed.set_footer(
                        text="Member of Miscellaneous\n• Nick Changed\n• Guest & Awaiting Approval were removed\n• Member was given")
                    embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')

                    await ctx.send(embed=embed)


                elif guild_name in self.bot.misc_allies:
                    for guild in self.bot.misc_allies:
                        if guild == guild_name:
                            gtag = await utils.get_gtag(guild)
                            if member.nick is None or str(gtag) not in member.nick:
                                ign = ign + " " + str(gtag)
                                await member.edit(nick=ign)
                            await member.remove_roles(self.bot.new_member_role)

                            await member.add_roles(self.bot.guest, self.bot.ally)

                            embed = discord.Embed(title=f"{member.name}'s nick and role were successfully changed!",
                                                  color=0x8368ff)
                            embed.set_footer(
                                text=f"Member of {guild}\n• Nick & Tag Changed\n• Member & Awaiting Approval were removed\n• Guest and Ally were given")
                            embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')
                            await ctx.send(embed=embed)


                elif guild_name != "Miscellaneous" and guild_name not in self.bot.misc_allies:
                    await member.remove_roles(member_, awaiting_app, newmember, ally)
                    await member.add_roles(guest)

                    embed = discord.Embed(title=f"{member.name}'s nick and role were successfully changed!",
                                          color=0x8368ff)

                    embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')
                    embed.set_footer(text=f"Member of {guild_name}"
                                          "\n• Member & Awaiting Approval were removed"
                                          "\n• Guest was given")

                    await ctx.send(embed=embed)
                elif guild_name is None:
                    await member.remove_roles(member_, awaiting_app, newmember)
                    await member.add_roles(guest)
                    guild_name = "Guildless (No Guild)"
                    embed = discord.Embed(title=f"{member.name}'s nick and role were successfully changed!",
                                          color=0x8368ff)
                    embed.set_footer(
                        text=f"Member of {guild_name}\n• Nick Changed\n• Member & Awaiting Approval were removed\n• Guest was given")
                    embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')

                    await ctx.send(embed=embed)



        else:
            embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                                  description="Your role lacks permissions to force sync a member's nick!",
                                  color=0xff0000)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("Admin")
    async def staffreview(self, ctx):
        channel = self.bot.get_channel(523226672980557824)
        admin = discord.utils.get(ctx.guild.roles, name="Admin")
        if admin in ctx.author.roles:
            embed = discord.Embed(title="Staff checkup", color=0x8368ff)
            while True:
                await ctx.send('**What is the name of the staff member?**')
                staff_name = await self.bot.wait_for('message', check=lambda
                    x: x.author == ctx.message.author and x.channel == ctx.channel)
                staff_name = staff_name.content

                await ctx.send(f"**What are your comments about** *{staff_name}*")
                staff_comm = await self.bot.wait_for('message', check=lambda
                    x: x.author == ctx.message.author and x.channel == ctx.channel)
                staff_comm = staff_comm.content
                embed.add_field(name=staff_name, value=staff_comm, inline=False)

                embed1 = discord.Embed(title="Is that it or are there more staff members?", color=0x8368ff)
                embed1.add_field(name="If yes:", value="Reply with `Yes`")
                embed1.add_field(name="If not:", value="Reply with `No`")
                await ctx.send(embed=embed1)

                more = await self.bot.wait_for('message', check=lambda x: x.channel == ctx.channel)
                more = more.content
                more = more.capitalize()

                if more in ('Yes', 'Yeah', 'Ye', 'Yea'):
                    continue
                else:
                    await channel.send(embed=embed)
                    break
        else:
            embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                                  description="Your role lacks permissions make a post for the staff checkup!",
                                  color=0xff0000)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("Admin")
    async def partner(self, ctx):
        await ctx.send("**What is the name of the guild/organization you wish to partner?**")
        name = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        name = name.content

        await ctx.send("**Kindly provide a brief description of the guild/organization. ONE MESSAGE ONLY!!!**")
        description = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        description = description.content

        embed = discord.Embed(title=name,
                              url=f'https://plancke.io/hypixel/guild/name/{name.replace(" ", "%20")}',
                              description=description,
                              color=0x8368ff)
        partner_channel = self.bot.get_channel(874725728397193436)
        await partner_channel.send(embed=embed)

    @commands.command()
    @commands.has_role("Staff")
    async def rolecheck(self, ctx, send_ping=None):
        """Checks the roles of all the users and changes them on the basis of their guild
        """
        import time
        msg = await ctx.send("**Processing all the prerequisites**")

        misc_uuids = await utils.get_guild_members("Miscellaneous")     #Fetches the uuids of all miscellaneous members
        misc_members, ally_members, ally_uuids = [], [], []
        start_time = time.time()
        discord_member_count = 0
        for x in self.bot.misc_allies:
            ally_uuids = ally_uuids + await utils.get_guild_members(x)      #Fetches the uuids of all ally guild members
            await msg.edit(content=f"**Getting Ally UUIDs** - {x}")

        cursor = await self.bot.db.execute("SELECT username FROM DNKL")
        rows = await cursor.fetchall()
        await cursor.close()

        dnkl_names = []
        for tuple in rows:
            username = tuple[0]
            dnkl_names.append(username)

        # Miscellaneous Member Names
        await msg.edit(content="**Processing** - 1/2")
        with ThreadPoolExecutor(max_workers=10) as executor:
            with requests.Session() as session:
                # Set any session parameters here before calling `fetch`
                loop = asyncio.get_event_loop()
                tasks = [
                    loop.run_in_executor(
                        executor,
                        utils.fetch,
                        *(session, individual_misc_uuid)  # Allows us to pass in multiple arguments to `fetch`
                    )
                    for individual_misc_uuid in misc_uuids
                ]
                for response in await asyncio.gather(*tasks):  # Puts the result into a list
                    misc_members.append(response)

        # Ally Member Names
        await msg.edit(content="**Processing** - 2/2")
        with ThreadPoolExecutor(max_workers=10) as executor:
            with requests.Session() as session:
                # Set any session parameters here before calling `fetch`
                loop = asyncio.get_event_loop()
                tasks = [
                    loop.run_in_executor(
                        executor,
                        utils.fetch,
                        *(session, individual_ally_uuid)  # Allows us to pass in multiple arguments to `fetch`
                    )
                    for individual_ally_uuid in ally_uuids
                ]
                for response in await asyncio.gather(*tasks):  # Puts the result into a list
                    ally_members.append(response)

        for guild in self.bot.guilds:
            if str(guild) == "Miscellaneous [MISC]":  # Check if the Discord is Miscellaneous
                for member in guild.members:  # For loop for all members in the Discord
                    discord_member_count+=1
                    if member.id not in self.bot.admin_ids and member.bot is False:
                        name = await utils.name_grabber(member)
                        has_tag_perms = any(role in ctx.author.roles for role in self.bot.tag_allowed_roles)
                        await msg.edit(content=f"Checking {name} - \\{member}"
                                               f"\n*If you see that the checking is stuck on a member, check <#523743721443950612>, if you see an error forcesync the user the bot got stuck on and then rerun rolecheck!*")

                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as mojang:

                                if mojang.status != 200:  # If the IGN is invalid
                                    await member.remove_roles(self.bot.member_role,
                                                              self.bot.guest,
                                                              reason="Rolecheck")
                                    await member.add_roles(self.bot.new_member_role,
                                                           reason="Rolecheck"),
                                    continue
                                elif self.bot.guild_master not in member.roles:
                                    mojang_json = await mojang.json()
                                    ign = mojang_json["name"]
                                    uuid = mojang_json['id']
                                await session.close()
                            # Miscellaneous
                        if ign in misc_members and ign not in ("Rowdies", "PolarPowah", "LBROz", "Fantastic_Doge", "ElijahRus", "BotTyler", "silviccs"):
                            async with aiohttp.ClientSession() as session:
                                async with session.get(
                                        f"https://api.hypixel.net/guild?key={utils.get_api()}&player={uuid}") as resp:
                                    req = await resp.json()
                                    await session.close()

                            if self.bot.member_role not in member.roles or self.bot.new_member in member.roles or self.bot.ally in member.roles:
                                await member.add_roles(self.bot.member_role,
                                                       reason="Rolecheck - Member of Miscellaneous - Member Role Absent/New Member or Ally Role(s) Present - Given Member")
                                await member.remove_roles(self.bot.new_member_role,
                                                          self.bot.guest,
                                                          self.bot.ally,
                                                          reason="Rolecheck - Member of Miscellaneous - Member role Absent/New Member or Ally Role(s) Present - Removed New Member, Guest &/or Ally")


                            for user in req['guild']["members"]:
                                if uuid == user["uuid"]:
                                    totalexp = user['expHistory']
                                    totalexp = sum(totalexp.values())
                                    usergrank = user['rank']

                                    if totalexp >= self.bot.active:  # If the member meets active requirements
                                        if has_tag_perms is False:
                                            await member.edit(nick=name)
                                        await member.remove_roles(self.bot.inactive_role,
                                                                  reason="Rolecheck - Active Requirements met - Removed Inactive")
                                        await member.add_roles(self.bot.active_role,
                                                               reason="Rolecheck - Active Requirements met - Given Active role")


                                    elif usergrank != 'Resident':     # For non-residents
                                        if totalexp < self.bot.inactive:    # Base requirement check for non-residents
                                            if has_tag_perms is False:
                                                await member.edit(nick=name)
                                            if name not in dnkl_names:  # If the member doesn't meet base guild requirements
                                                await member.add_roles(self.bot.inactive_role,
                                                                       reason="Rolecheck - Guild Requirements not met - Given Active role")
                                            await member.remove_roles(self.bot.active_role,
                                                                      reason="Rolecheck - Guild Requirements not met - Removed Active role")

                                        else:  # If the member meets regular requirements
                                            if has_tag_perms is False:
                                                await member.edit(nick=name)
                                            await member.remove_roles(self.bot.inactive_role,
                                                                      self.bot.active_role,
                                                                      reason="Rolecheck - Regular Requirements met - Removed Inactive &/or Active")


                                    else:       # For residents
                                        if totalexp < self.bot.resident_req:    # Base requirement check for residents
                                            if has_tag_perms is False:
                                                await member.edit(nick=name)
                                            await member.add_roles(self.bot.inactive_role, reason="Rolecheck")
                                            await member.remove_roles(self.bot.active_role, self.bot.ally,
                                                                      reason="Rolecheck")

                                        else:  # If the resident meets base resident requirements
                                            if has_tag_perms is False:
                                                await member.edit(nick=name)
                                            await member.remove_roles(self.bot.inactive_role,
                                                                      self.bot.active_role,
                                                                      reason="Rolecheck - Resident Requirements met - Removed Inactive &/or Active")

                        # Ally
                        elif ign in ally_members:
                            guild_name = await utils.get_guild(name)
                            for ally_guild in self.bot.misc_allies:
                                if ally_guild == guild_name:
                                    gtag = await utils.get_gtag(guild_name)
                                    if (member.nick is None or str(gtag) not in member.nick) and has_tag_perms is False:
                                        ign = ign + " " + str(gtag)
                                        await member.edit(nick=ign)
                                    await member.add_roles(self.bot.guest,
                                                           self.bot.ally,
                                                           reason="Rolecheck - Member of an Ally Guild - Given Guest &/or Ally")
                                    await member.remove_roles(self.bot.member_role,
                                                              self.bot.new_member_role,
                                                              self.bot.active_role,
                                                              self.bot.inactive_role,
                                                              reason="Rolecheck - Member of an Ally Guild - Removed Member, New Member, Active &/or Inactive")

                        else:
                            if member.nick != name and has_tag_perms is False:
                                await member.edit(nick=ign)
                            await member.add_roles(self.bot.guest, reason="Rolecheck - Guest - Given Guest")
                            await member.remove_roles(self.bot.member_role,
                                                      self.bot.new_member_role,
                                                      self.bot.active_role,
                                                      self.bot.inactive_role,
                                                      self.bot.ally,
                                                      reason="Rolecheck - Guest - Removed Member, New Member, Active, Inactive &/or Ally")
                end_time = time.time()
                await msg.edit(content=f"**Completed rolecheck for {discord_member_count} discord members!**\n"
                                       f"Time Taken for execution- {round(end_time-start_time)}")
        if not send_ping:
            inactivity_channel = self.bot.get_channel(848067712156434462)

            embed = discord.Embed(title="You do not meet the guild requirements!",
                                  description=f"Member requirement - **{format(self.bot.inactive, ',d')}** Weekly Guild Experience\nResident requirement - **{format(self.bot.resident_req, ',d')}** Weekly Guild Experience",
                                  color=0xDC143C)
            await inactivity_channel.send(f"<@&848051215287058443>")
            await inactivity_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(staff(bot))
