import discord
from discord.ext import commands
from cogs.utils import hypixel
from datetime import datetime
import json
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import asyncio
import requests

class staff(commands.Cog, name="Staff"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['req', 'requirement'])
    async def requirements(self, ctx):
        """Lists the requirements
        """
        try:
            embed = discord.Embed(title="Miscellaneous Guild Requirements",
                                description="These requirements are subject to change!",
                                color=0x8368ff)
            embed.add_field(name="Active", value=f"•  {format(self.bot.active,',d')} Weekly Guild Experience", inline=False)
            embed.add_field(name="Do Not Kick List Eligibility", value=f"•  {format(self.bot.dnkl,',d')} Weekly Guild Experience", inline=False)
            embed.add_field(name="Resident", value=f"•  {format(self.bot.resident_req,',d')} Weekly Guild Experience", inline=False)
            embed.add_field(name="Member", value=f"•  {format(self.bot.inactive,',d')} Weekly Guild Experience", inline=False)
            embed.add_field(name="New Member", value=f"•  {format(self.bot.new_member,',d')} Daily Guild Experience", inline=False)
            embed.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                                "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(aliases=['res'])
    async def resident(self, ctx):
        """Lists the methods to get the resident rank
        """
        try:
            embed = discord.Embed(title='How to get Resident?',
                                description='To be eligible for Resident, you must be one of the following',
                                color=0x8368ff)
            embed.add_field(name="Veteran", value="Be in the guild for more than 1 year",
                            inline=False)
            embed.add_field(name="Server Booster", value="Boost the Discord. You will lose resident once your boost expires.",
                            inline=False)
            embed.add_field(name="Youtuber", value="If you're a youtuber with more than 5,000 subscribers, you aren't subject to any guild requirements.",
                            inline=False)
            embed.add_field(name="Sugar Daddy", value="Spend Money on the guild by doing giveaways, sponsoring events!",
                            inline=False)
            embed.set_footer(text=f"Everyone who has the resident rank must get {format(self.bot.resident_req,',d')} weekly guild experience! (Except YouTubers)")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(aliases=['ticket'])
    async def tickets(self, ctx):
        """Explains the entire ticket system
        """
        try:
            embed = discord.Embed(title="How to create a ticket?",
                                color=0x8368ff)
            embed.add_field(name="Go to #🎟-tickets-🎟",
                            value="#🎟-tickets-🎟 is located in the noticeboard category",
                            inline=False)
            embed.add_field(name="Tickets can be created for the following reasons",
                            value="> Discord Nick/Role Change\n"
                                "> Do not kick list\n"
                                "> Problems/Queries/Complaint/Suggestion\n"
                                "> Reporting a player\n"
                                "> Milestone\n"
                                "> Staff Application\n"
                                "> Event\n"
                                "> Other",
                            inline=False)
            embed.add_field(name="React to the message sent by @TicketTool",
                            value="The following image shows you what you need to react to.",
                            inline=False)
            embed.set_image(url=f"https://media.discordapp.net/attachments/522930919984726016/775953643991990272/unknown.png?width=1069&height=702")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @commands.command(aliases=['participant'])
    async def participants(self, ctx, raw=None):
        try:
            staff = discord.utils.get(ctx.guild.roles, name="Staff")
            if staff in ctx.author.roles:
                div1_name = div2_name = ""
                count = 0
                with open('eventparticipants.json') as f:
                    data = json.load(f)
                if raw is not None:
                    await ctx.author.send(data)
                else:
                    for x in data['div1']:
                        div1_name = div1_name + f"{x}\n"
                        count += 1
                    for x in data['div2']:
                        div2_name = div2_name + f"{x}\n"
                        count += 1
                    embed = discord.Embed(title='The participants of the event are as follows:',
                                        color=0x8368ff)
                    embed.add_field(name="Division 1", value=div1_name, inline=False)
                    embed.add_field(name="Division 2", value=div2_name, inline=False)
                    embed.set_footer(text=f"Total: {count}")
                    await ctx.send(embed=embed)
            else:
                participants = ""
                count = 0
                with open('eventparticipants.json') as f:
                    data = json.load(f)
                if raw is not None:
                    await ctx.author.send(data)
                else:
                    for x in data['div1']:
                        participants = participants + f"{x}\n"
                        count += 1
                    for x in data['div2']:
                        participants = participants + f"{x}\n"
                        count += 1
                    embed = discord.Embed(title='The participants of the event are as follows:', description=participants,
                                        color=0x8368ff)
                    embed.set_footer(text=f"Total: {count}")
                    await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await self.bot.error_channel.send(f"Error in {ctx.channel.name} while running `participants`"
                                    f"\n{e}\n<@!326399363943497728>")

    @commands.command(aliases=['switch','swapper'])
    async def swap(self, ctx, name):
        """Swaps a users division in an event
        """
        try:
            count = 0
            div1_name = div2_name = ""
            ign = await hypixel.get_dispname(name)
            with open('eventparticipants.json') as f:
                data = json.load(f)
                if ign in data['div1']:
                    data['div1'].remove(ign)
                    data['div2'].append(ign)
                else:
                    data['div2'].remove(ign)
                    data['div1'].append(ign)

                for x in data['div1']:
                    div1_name = div1_name + f"{x}\n"
                    count += 1
                for x in data['div2']:
                    div2_name = div2_name + f"{x}\n"
                    count += 1
                embed = discord.Embed(title='The participants of the event are as follows:',
                                    color=0x8368ff)
                embed.add_field(name="Division 1", value=div1_name, inline=False)
                embed.add_field(name="Division 2", value=div2_name, inline=False)
                embed.set_footer(text=f"Total: {count}")
                await ctx.send(embed=embed)
            with open('eventparticipants.json', 'w') as event_participants:
                json.dump(data, event_participants)
        except Exception as e:
            print(e)
            await self.bot.error_channel.send(
                f"Error in {ctx.channel.name} while running dnkllist"
                f"Error in {ctx.channel.name} while running `swap`"
                f"\n{e}\n<@!326399363943497728>")

    @commands.command()
    @commands.has_role(538015368782807040)
    async def staff(self, ctx):
        """Prints a list of users who need to be promoted, demoted, warned and kicked!
        """
        try:
            msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
            api = hypixel.get_api()
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.hypixel.net/guild?key={api}&name=Miscellaneous') as resp:
                    g = await resp.json()
                    await session.close()

            with open('dnkl.json') as f:
                data = json.load(f)

            key = data.keys()

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
                            async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                                a = await resp.json()
                                await session.close()
                        name = a['name']
                        time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                        dt = (time[0:10])
                        if name in key:
                            name = name + f'[DNKL]\n{dt}'
                        else:
                            name = name + f'[{rank}]\n{dt}'
                        exp += expHistory
                        activearray[name] = exp
                        exp = 0
                    elif expHistory < self.bot.active and rank == "Active":
                        uuid = g['guild']['members'][i]['uuid']
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                                a = await resp.json()
                                await session.close()
                        name = a['name']
                        time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                        dt = (time[0:10])
                        if name in key:
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
                                async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                                    a = await resp.json()
                            time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                            name = a['name']
                            dt = (time[0:10])
                            if name in key:
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
                                    async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                                        a = await resp.json()
                                time = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                                name = a['name']
                                dt = (time[0:10])
                                if name in key:
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
                embed = discord.Embed(title=f"The users to be PROMOTED are as follows:",
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
                embed = discord.Embed(title=f"The users to be DEMOTED are as follows:",
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
                    title=f"Kindly PM the following veterans on discord and inform them that they don't meet the requirements!",
                    description=f"Total: {len(VeteransortedList)}", color=0xe5ba6c)
                w = 0
                if len(VeteransortedList) <= 25:
                    for user in VeteransortedList:
                        embed.add_field(name=f"{user[0]}", value=f"```\n{format(user[1], ',d')}```", inline=True)
                    await ctx.send(embed=embed)
                else:
                    for user in VeteransortedList:
                        w = w + 1
                        embed.add_field(name=f"{user[0]}", value=f"```\n{format(user[1], ',d')}```", inline=True)

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
                await ctx.send(
                    "**PLEASE CHECK THE DO NOT KICK LIST BEFORE KICKING ANYONE**\nDon't PM the veterans if they're on the do not kick list!")

        except Exception as e:
            if str(e) == "Expecting value: line 1 column 1 (char 0)":
                embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                    color=0xff0000)
                await ctx.send(embed=embed)
                print(e)
            else:
                print(e)
                await self.bot.error_channel.send(f"Error in {ctx.channel.name} while using `staff`\n{e}\n<@!326399363943497728>")
            
    @commands.command()
    @commands.has_role(538015368782807040)
    async def rolecheck(self, ctx):
        """Checks the roles of all the users and changes them on the basis of their guild
        """
        try:
            guild_master = discord.utils.get(ctx.guild.roles, name="Guild Master")
            staff = discord.utils.get(ctx.guild.roles, name="Staff")
            new_member = discord.utils.get(ctx.guild.roles, name="New Member")
            guest = discord.utils.get(ctx.guild.roles, name="Guest")
            member_role = discord.utils.get(ctx.guild.roles, name="Member")
            active_role = discord.utils.get(ctx.guild.roles, name="Active")
            inactive_role = discord.utils.get(ctx.guild.roles, name="Inactive")
            xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")


            msg = await ctx.send("**Processing all the prerequisites**")

            misc_uuids, xl_uuids, = await hypixel.get_guild_members("Miscellaneous"), await hypixel.get_guild_members("XL")


            misc_members, calm_members, xl_members= [], [], []

            #Miscellaneous Member Names
            await msg.edit(content="**Processing** - 1/2")
            with ThreadPoolExecutor(max_workers=10) as executor:
                with requests.Session() as session:
                    # Set any session parameters here before calling `fetch`
                    loop = asyncio.get_event_loop()
                    tasks = [
                        loop.run_in_executor(
                            executor,
                            hypixel.fetch,
                            *(session, individual_uuid)  # Allows us to pass in multiple arguments to `fetch`
                        )
                        for individual_uuid in misc_uuids
                    ]
                    for response in await asyncio.gather(*tasks): #Puts the result into a list
                        misc_members.append(response)


            #XL Member Names
            await msg.edit(content="**Processing** - 2/2")
            with ThreadPoolExecutor(max_workers=10) as executor:
                with requests.Session() as session:
                    # Set any session parameters here before calling `fetch`
                    loop = asyncio.get_event_loop()
                    tasks = [
                        loop.run_in_executor(
                            executor,
                            hypixel.fetch,
                            *(session, individual_uuid)  # Allows us to pass in multiple arguments to `fetch`
                        )
                        for individual_uuid in xl_uuids
                    ]
                    for response in await asyncio.gather(*tasks):  # Puts the result into a list
                        xl_members.append(response)


            if staff in ctx.author.roles:  # Making sure that the user is Staff
                for guild in self.bot.guilds:
                    if str(guild) == "Miscellaneous [MISC]":  # Check if the Discord is Miscellaneous
                        for member in guild.members:  # For loop for all members in the Discord
                            if member.id != '326399363943497728' and member.bot is False:
                                name = member.nick  # Obtaining their nick
                                if name is None:  # If they don't have a nick, it uses their name.
                                    name = member.name

                                else:
                                    message = await ctx.send(f"Checking {name}")

                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                                            mojang = resp
                                    
                                    if mojang.status != 200:  # If the IGN is invalid
                                        await member.remove_roles(member_role, guest)
                                        await member.add_roles(new_member)
                                        await message.edit(content=
                                                        f"{name} ||{member}|| Player doesn't exist. **++New Member | --Member | -- Guest**")
                                    elif guild_master not in member.roles:
                                        mojang_json = await mojang.json()
                                        ign = mojang_json["name"]
                                        uuid = mojang_json['id']
                                        await member.edit(nick=ign)


                                        #Miscellaneous
                                        if ign in misc_members and ign != "Rowdies":
                                            async with aiohttp.ClientSession() as session:
                                                async with session.get(f"https://api.hypixel.net/guild?key={await hypixel.get_api()}&player={uuid}") as resp:
                                                    req = await resp.json()


                                            if member_role not in member.roles:
                                                await member.add_roles(member)
                                                await member.remove_roles(new_member, guest)

                                            for user in req['guild']["members"]:
                                                if uuid == user["uuid"]:
                                                    totalexp = user['expHistory']
                                                    totalexp = sum(totalexp.values())
                                                    usergrank = user['rank']

                                                if usergrank != 'Resident':
                                                    if totalexp < self.bot.inactive:
                                                        await member.add_roles(inactive_role)
                                                        await member.remove_roles(active_role)
                                                        await message.edit(
                                                            content=f"{name} ||{member}|| **++Member \| ++Inactive \| --Active**")

                                                    elif totalexp >= self.bot.active:  # If the member is active
                                                        await member.remove_roles(inactive_role, new_member)
                                                        await member.add_roles(active_role)
                                                        await message.edit(
                                                            content=f"{name} ||{member}|| **++Member \| ++Active \| --Inactive**")

                                                    elif totalexp > self.bot.inactive:
                                                        await member.remove_roles(inactive_role, active_role)
                                                        await message.edit(
                                                            content=f"{name} ||{member}|| **++Member \| --Inactive\| --Active**")
                                                else:
                                                    if totalexp < 50000:
                                                        await member.add_roles(inactive_role)
                                                        await member.remove_roles(active_role)
                                                        await message.edit(
                                                            content=f"{name} ||{member}|| **++Member \| ++Inactive \| --Active**")

                                                    elif totalexp >= self.bot.active:  # If the member is active
                                                        await member.remove_roles(inactive_role, new_member)
                                                        await member.add_roles(active_role)
                                                        await message.edit(
                                                            content=f"{name} ||{member}|| **++Member \| ++Active \| --Inactive**")

                                                    elif totalexp > 50000:
                                                        await member.remove_roles(inactive_role, active_role)
                                                        await message.edit(
                                                            content=f"{name} ||{member}|| **++Member \| --Inactive\| --Active**")

                                                


                                        elif ign in xl_members:
                                            await member.add_roles(guest, xl_ally)
                                            await member.remove_roles(member_role, new_member, active_role)
                                            await message.edit(content=f"{name} ||{member}|| Member of XL **++XL - Ally \| ++Guest | --Member | --Active**")

                                        else:
                                            await member.add_roles(guest)
                                            await member.remove_roles(member_role, new_member, active_role)
                                            await message.edit(content=f"{name} ||{member}|| Member of an unallied guild **++Guest | --Member | --Active**")

            inactivity_channel = self.bot.get_channel(848067712156434462)

            embed = discord.Embed(title="You do not meet the guild requirements!",
                                description=f"Member requirement - **{format(self.bot.inactive,',d')}** Weekly Guild Experience\nResident requirement - **{format(self.bot.resident_req,',d')}** Weekly Guild Experience",
                                color = 0xDC143C)
            await inactivity_channel.send(f"<@&848051215287058443>")
            await inactivity_channel.send(embed=embed)

        except Exception as e:
            if str(e) == "Expecting value: line 1 column 1 (char 0)":
                embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                    color=0xff0000)
                await ctx.send(embed=embed)
                print(e)
            elif str(e) == "404 Not Found (error code: 10011): Unknown Role":
                print(e)
                await self.bot.error_channel.send(f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n{ctx.author.mention} please `forcesync` the last user on the list.")

            else:
                print(e)
                await self.bot.error_channel.send(
                    f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n<@!326399363943497728>")

    @commands.command(aliases=['fs'])
    @commands.has_role(538015368782807040)
    async def forcesync(self, ctx, member: discord.Member, name):
        """Used to forcefully sync a player's IGN
        """
        try:
            officer = discord.utils.get(ctx.guild.roles, name="Officer")
            admin = discord.utils.get(ctx.guild.roles, name="Admin")
            if officer or admin in ctx.author.roles:
                ign = await hypixel.get_dispname(name)
                if ign is None:
                    await ctx.send('Please enter a valid ign!')
                else:
                    guild_name = await hypixel.get_guild(name)
                    newmember = discord.utils.get(ctx.guild.roles, name="New Member")
                    guest = discord.utils.get(ctx.guild.roles, name="Guest")
                    member_ = discord.utils.get(ctx.guild.roles, name="Member")
                    awaiting_app = discord.utils.get(ctx.guild.roles, name="Awaiting Approval")
                    xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")


                    await member.edit(nick=ign)

                    if guild_name == "Miscellaneous":
                        await member.remove_roles(guest,awaiting_app,newmember)
                        await member.add_roles(member_)
                        embed = discord.Embed(title=f"{member.name}'s nick and role were successfully changed!",
                                            description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                            color=0x8368ff)
                        embed.set_footer(text="Member of Miscellaneous\n• Nick Changed\n• Guest & Awaiting Approval were removed\n• Member was given")
                        await ctx.send(embed=embed)


                    elif guild_name == "XL":
                        await member.remove_roles(member_,awaiting_app)
                        await member.add_roles(guest, xl_ally)

                        embed = discord.Embed(title="Your nick and role was successfully changed!",
                                            description="If this wasn't the change you anticipated, "
                                                        "kindly create a ticket or get in contact with staff!",
                                            color=0x8368ff)

                        embed.set_footer(text="Member of XL"
                                            "\n• Member & Awaiting Approval were removed"
                                            "\n• Guest & XL - Ally were given")
                        await ctx.send(embed=embed)


                    elif guild_name not in ("Miscellaneous", "XL"):
                        if str(ctx.channel.category.name) == "RTickets":
                            await ctx.send("You aren't in Miscellaneous in-game. Kindly await staff assistance")
                        elif str(ctx.channel.category.name) == "REGISTRATION":
                            await ctx.send("The person isn't an ally/a member of Miscellaneous. Let them register!")
                        else:
                            await member.remove_roles(member_,awaiting_app)
                            await member.add_roles(guest)
                            if guild_name is None:
                                guild_name = "no guild (Guildless)"
                            embed = discord.Embed(title=f"{member.name}'s nick and role were successfully changed!",
                                                description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                                color=0x8368ff)
                            embed.set_footer(text=f"Member of {guild_name}\n• Nick Changed\n• Member & Awaiting Approval were removed\n• Guest was given")
                            await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                                    description="Your role lacks permissions to force sync a member's nick!", color=0xff0000)
                await ctx.channel.purge(limit=1)
                await ctx.send(embed=embed)

        except Exception as e:
            if str(e) == "Expecting value: line 1 column 1 (char 0)":
                embed = discord.Embed(title="The Hypixel API is down!",
                                    description="Please try again in a while!",
                                    color=0xff0000)
                await ctx.send(embed=embed)
                print(e)
            else:
                print(e)
                await self.bot.error_channel.send(f"Error in {ctx.channel.name} while trying to use `forcesync`\n{e}\n<@!326399363943497728>")

    @commands.command()
    @commands.has_role(522588118251995147)
    async def staffreview(self, ctx):
        try:
            channel = self.bot.get_channel(523226672980557824)
            admin = discord.utils.get(ctx.guild.roles, name="Admin")
            if admin in ctx.author.roles:
                embed = discord.Embed(title="Staff checkup", color=0x8368ff)
                while True:
                    await ctx.send('**What is the name of the staff member?**')
                    staff_name = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author and x.channel == ctx.channel)
                    staff_name = staff_name.content

                    await ctx.send(f"**What are your comments about** *{staff_name}*")
                    staff_comm = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author and x.channel == ctx.channel)
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
                                    description="Your role lacks permissions make a post for the staff checkup!", color=0xff0000)
                await ctx.channel.purge(limit=1)
                await ctx.send(embed=embed)

        except Exception as e:
            print(e)
            await self.bot.error_channel.send(f"Error in {ctx.channel.name} while using `staffreview`\n{e}\n<@!326399363943497728>")

    @commands.command()
    @commands.has_role(538015368782807040)
    async def newrolecheck(self, ctx):
        try:
            guild_master = discord.utils.get(ctx.guild.roles, name="Guild Master")
            staff = discord.utils.get(ctx.guild.roles, name="Staff")
            new_member = discord.utils.get(ctx.guild.roles, name="New Member")
            guest = discord.utils.get(ctx.guild.roles, name="Guest")
            member_role = discord.utils.get(ctx.guild.roles, name="Member")
            active_role = discord.utils.get(ctx.guild.roles, name="Active")
            inactive_role = discord.utils.get(ctx.guild.roles, name="Inactive")
            xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")

            misc_info, xl_members, discord_members,\
            invalid_members, active_members, regular_members,inactive_members,\
            xl_discord_members, guest_list = [], [], [], [], [], [], [], [], []

            guild = self.bot.get_guild(522586672148381726)
            memberList = guild.members

            msg = await ctx.send("**Processing all the prerequisites**")

            misc_details, xl_uuids, = await hypixel.get_misc_members(
                "Miscellaneous"), await hypixel.get_guild_members("XL")

            count = 0
            # Miscellaneous Member Names + gexp
            await msg.edit(content="**Processing** - 1/2")
            with ThreadPoolExecutor(max_workers=10) as executor:
                with requests.Session() as session:
                    # Set any session parameters here before calling `fetch`
                    loop = asyncio.get_event_loop()
                    tasks = [
                        loop.run_in_executor(
                            executor,
                            hypixel.fetch,
                            *(session, individual_uuid[0])  # Allows us to pass in multiple arguments to `fetch`
                        )
                        for individual_uuid in misc_details
                    ]
                    for response in await asyncio.gather(*tasks):  # Puts the result into a list
                        misc_details[count][0] = response
                        count = count + 1

            # XL Member Names
            await msg.edit(content="**Processing** - 2/2")
            with ThreadPoolExecutor(max_workers=10) as executor:
                with requests.Session() as session:
                    # Set any session parameters here before calling `fetch`
                    loop = asyncio.get_event_loop()
                    tasks = [
                        loop.run_in_executor(
                            executor,
                            hypixel.fetch,
                            *(session, individual_uuid)  # Allows us to pass in multiple arguments to `fetch`
                        )
                        for individual_uuid in xl_uuids
                    ]
                    for response in await asyncio.gather(*tasks):  # Puts the result into a list
                        xl_members.append(response)


            if staff in ctx.author.roles:  # Making sure that the user is Staff
                for guild in self.bot.guilds:
                    if str(guild) == "Miscellaneous [MISC]":  # Check if the Discord is Miscellaneous
                        for member in guild.members:  # For loop for all members in the Discord
                            if not member.bot:
                                discord_members.append(member)

                invalid_names = active_names = inactive_names = member_names = xl_names = ""
                for member in discord_members:
                    name = member.nick  # Obtaining their nick
                    if name is None:  # If they don't have a nick, it uses their name.
                        name = member.name

                    name = '_' + name

                    if name.isidentifier() is False:
                        await member.remove_roles(member_role, guest)
                        await member.add_roles(new_member)

                        invalid_names = invalid_names + str(member) + "\n"
                        discord_members.pop(discord_members.index(member))

                    name = member.nick  # Obtaining their nick
                    if name is None:  # If they don't have a nick, it uses their name.
                        name = member.name

                    for element in misc_details:
                        if name in element[0]:
                            if element[1] > self.bot.active:
                                active_members.append(member)
                                active_names = active_names + str(member) + "\n"
                            elif element[1] > self.bot.inactive:
                                if member_role not in member.roles:
                                    regular_members.append(member)
                                    member_names = member_names + str(member) + "\n"
                            elif element[1] < self.bot.inactive:
                                inactive_members.append(member)
                                inactive_names = inactive_names + str(member) + "\n"

                    if name in xl_members:
                        if xl_ally not in member.roles:
                            xl_discord_members.append(member)
                            xl_names = xl_names + str(member) + "\n"
                    else:
                        guest_list.append(member)
                invalid_embed = discord.Embed(title="Invalid: Given @New Member", description=invalid_names, color=0x620B06)
                active_embed = discord.Embed(title="Active: Given @Active", description=active_names, color=0x0073BF)
                member_embed = discord.Embed(title="Member: Given @Member", description=member_names, color=0x4DFF00)
                inactive_embed = discord.Embed(title="Inactive: Given @inactive", description=inactive_names, color=0xFF4C6E)
                xl_embed = discord.Embed(title="XL: Given @xl_ally", description=xl_names, color=0xA05E75)
                await ctx.send(embed=invalid_embed)
                await ctx.send(embed=active_embed)
                await ctx.send(embed=member_embed)
                await ctx.send(embed=inactive_embed)
                await ctx.send(embed=xl_embed)



        except Exception as e:
            if str(e) == "Expecting value: line 1 column 1 (char 0)":
                embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                    color=0xff0000)
                await ctx.send(embed=embed)
                print(e)
            elif str(e) == "404 Not Found (error code: 10011): Unknown Role":
                print(e)
                await self.bot.error_channel.send(f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n{ctx.author.mention} please `forcesync` the last user on the list.")

            else:
                print(e)
                await self.bot.error_channel.send(
                    f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n<@!326399363943497728>")

    @commands.command()
    @commands.has_role(538015368782807040)
    async def challenge(self, ctx, x):
        channel = self.bot.get_channel(753103243659444286)
        if x == "e":
            msg = await ctx.send(content="**What would you like the first challenge under the easy category to be (name)?**")
            challenge1 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1 = challenge1.content

            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge1_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1_prize = challenge1_prize.content

            await msg.edit(
                content="**What would you like the second challenge under the easy category to be?"
                        "\nIf you don't want one, type None**")
            challenge2 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2 = challenge2.content
            if challenge2 == "None":
                embed = discord.Embed(title="Easy", color=0x90ee90)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            else:
                await msg.edit(content="What is the prize for completing this challenge?")
                challenge2_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
                challenge2_prize = challenge2_prize.content

                embed = discord.Embed(title="Easy", color=0x90ee90)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
                embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
            await channel.send(f'*Complete the following challenges to get prizes*\nTo view the store, use `!shop`')
            await channel.send(embed=embed)

        if x == "m":
            msg = await ctx.send("**What would you like the first challenge under the medium category to be (name)?**")
            challenge1 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1 = challenge1.content

            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge1_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1_prize = challenge1_prize.content

            await msg.edit(
                content="**What would you like the second challenge under the medium category to be?"
                        "\nIf you don't want one, type None**")
            challenge2 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2 = challenge2.content
            if challenge2 == "None":
                embed = discord.Embed(title="Medium", color=0xffa500)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            else:
                await msg.edit(content="**What is the prize for completing this challenge?**")
                challenge2_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
                challenge2_prize = challenge2_prize.content

                embed = discord.Embed(title="Medium", color=0xffa500)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
                embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
            await channel.send(embed=embed)

        if x == "h":
            msg = await ctx.send("**What would you like the challenge under the hard category to be (name)?**")
            challenge1 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1 = challenge1.content

            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge1_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1_prize = challenge1_prize.content

            await msg.edit(
                content="**What would you like the second challenge under the hard category to be?"
                        "\nIf you don't want one, type None**")
            challenge2 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2 = challenge2.content
            if challenge2 == "None":
                embed = discord.Embed(title="Hard", color=0xcd5c5c)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            else:
                await msg.edit(content="**What is the prize for completing this challenge?**")
                challenge2_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
                challenge2_prize = challenge2_prize.content

                embed = discord.Embed(title="Hard", color=0xcd5c5c)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
                embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
                embed.set_footer(text="You can only do one challenge once.")
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(staff(bot))