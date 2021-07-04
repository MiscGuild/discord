import discord
from discord.ext import commands
from cogs.utils import hypixel
import math
import aiohttp
from datetime import datetime
import json
from quickchart import QuickChart
from io import BytesIO

class Hypixel(commands.Cog, name="Hypixel"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx, name):
        """Used to update your discord nick upon changing your minecraft name/leaving Miscellaneous!
        """
        author = ctx.author
        ign = await hypixel.get_dispname(name)

        if ign is None:
            await ctx.send('Please enter a valid ign!')
        else:
            guild_name = await hypixel.get_guild(name)
            guest = discord.utils.get(ctx.guild.roles, name="Guest")
            member = discord.utils.get(ctx.guild.roles, name="Member")
            awaiting_app = discord.utils.get(ctx.guild.roles, name="Awaiting Approval")
            xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")


            await author.edit(nick=ign)
            if guild_name == "Miscellaneous":
                await ctx.author.remove_roles(guest,awaiting_app)
                await ctx.author.add_roles(member)
                embed = discord.Embed(title="Your nick and role was successfully changed!",
                                    description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                    color=0x8368ff)
                embed.set_footer(text="Member of Miscellaneous\n• Nick Changed\n• Guest & Awaiting Approval were removed\n• Member was given")
                await ctx.send(embed=embed)

            elif guild_name == "XL":
                await ctx.author.remove_roles(member, awaiting_app)
                await ctx.author.add_roles(guest, xl_ally)

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
                    await ctx.send("You aren't in Miscellaneous in-game. Kindly await staff assistance!")
                else:
                    await ctx.author.remove_roles(member)
                    await ctx.author.remove_roles(awaiting_app)
                    await ctx.author.add_roles(guest)
                    if guild_name is None:
                        guild_name = "no guild (Guildless)"
                    embed = discord.Embed(title="Your nick and role was successfully changed!",
                                        description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                        color=0x8368ff)
                    embed.set_footer(text=f"Member of {guild_name}\n• Nick Changed\n• Member & Awaiting Approval were removed\n• Guest was given")
                    await ctx.send(embed=embed)


    @commands.command(aliases=["i"])
    async def info(self, ctx, name=None):
        """Gives the hypixel stats of the requested player
        """
        async with ctx.channel.typing():
            if name is None:
                author = ctx.author
                name = author.nick
                if name is None:
                    x = author.name
                    name = x
            req = await hypixel.get_data(name)
            if req["player"] is None:
                embed = discord.Embed(title="Your discord nick doesn't match your minecraft name",
                                    description=',sync `Your minecraft name`', color=0xff0000)
                await ctx.channel.purge(limit=1)
                await ctx.send(embed=embed)
            else:
                ign = req["player"]["displayname"]
                uuid = req["player"]['uuid']
                api = hypixel.get_api()
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}') as resp:
                        req2 = await resp.json()

                'NETWORK LEVEL'
                exp = int(req["player"]["networkExp"])
                exp = (math.sqrt((2 * exp) + 30625) / 50) - 2.5
                level = round(exp, 2)

                'KARMA'
                karma = int(req["player"]["karma"])
                karma = f"{karma:,d}"

                'RANK'
                if "prefix" in req["player"]:
                    player_prefix = (req["player"]["prefix"])
                    if player_prefix == "§d[PIG§b+++§d]":
                        print('Rank acquired- PIG')
                        rank = f"[PIG+++]"
                    elif player_prefix == "§c[SLOTH]":
                        print('Rank acquired- Sloth')
                        rank = "[SLOTH]"
                    elif player_prefix == "§c[OWNER]":
                        print('Rank acquired- Owner')
                        rank = "[OWNER]"
                else:
                    if "newPackageRank" in req["player"]:
                        if "rank" in req["player"]:
                            rank = (req["player"]["rank"])
                            if rank == 'YOUTUBER':
                                rank = '[YOUTUBE]'
                            if rank == 'ADMIN':
                                print('Rank acquired- Admin')
                                rank = '[ADMIN]'
                            if rank == 'MODERATOR':
                                print('Rank acquired- Moderator')
                                rank = '[MOD]'
                            if rank == 'HELPER':
                                print('Rank acquired- Helper')
                                rank = '[HELPER]'
                        else:
                            rank = (req["player"]["newPackageRank"])
                            if rank == 'MVP_PLUS':
                                if "monthlyPackageRank" in req["player"]:
                                    mvp_plus_plus = (req["player"]["monthlyPackageRank"])
                                    if mvp_plus_plus == "NONE":
                                        print('Rank acquired- MVP+')
                                        rank = '[MVP+]'
                                    else:
                                        print('Rank acquired- MVP+')
                                        rank = "[MVP++]"
                                else:
                                    print('Rank acquired- MVP+')
                                    rank = "[MVP+]"
                            elif rank == 'MVP':
                                print('Rank acquired- MVP')
                                rank = '[MVP]'
                            elif rank == 'VIP_PLUS':
                                print('Rank acquired- VIP+')
                                rank = '[VIP+]'
                            elif rank == 'VIP':
                                print('Rank acquired- VIP')
                                rank = '[VIP]'
                    else:
                        print('Rank acquired- Non')
                        rank = " "

                'ACHIEVEMENT POINTS'
                if "achievementPoints" in req["player"]:
                    ap = int(req["player"]["achievementPoints"])
                    ap = f"{ap:,d}"
                else:
                    ap = "-"

                'GUILD TAG'
                if len(req2) < 5:
                    gtag = " "
                else:
                    if req2["tag"] is None:
                        gtag = " "
                    else:
                        gtag = req2["guild"]["tag"]
                        gtag = f"[{gtag}]"

                'COMPLETED CHALLENGES'
                if "general_challenger" in req["player"]["achievements"]:
                    cp = int(req["player"]["achievements"]['general_challenger'])
                    cp = f"{cp:,d}"
                else:
                    cp = "0"

                'COMPLETED QUESTS'
                if "quests" in req["player"]:
                    cq = len(req["player"]["quests"])
                    cq = f"{cq:,d}"
                else:
                    cq = "-"

                'FIRST LOGIN'
                first_login = req["player"]["firstLogin"]
                time = datetime.fromtimestamp(int(str(first_login)[:-3]))
                fl = time

                'LAST LOGIN'
                if "lastLogin" in req["player"]:
                    last_login = req["player"]["lastLogin"]
                    time = datetime.fromtimestamp(int(str(last_login)[:-3]))
                    ll = time
                else:
                    ll = 'Unknown'


                embed = discord.Embed(title=f"{rank} {ign} {gtag}", url=f'https://plancke.io/hypixel/player/stats/{name}',
                                    color=0x8368ff)
                embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                embed.add_field(name="Network Level:", value=f"`{level}`", inline=True)
                embed.add_field(name="Karma:", value=f"`{karma}`", inline=True)
                embed.add_field(name="Achievement Points:", value=f"`{ap}`", inline=False)
                embed.add_field(name="Challenges Finished:", value=f"`{cp}`", inline=True)
                embed.add_field(name="Quests Completed:", value=f"`{cq}`", inline=True)
                embed.add_field(name="First • Last login", value=f"`{fl} • {ll}`", inline=False)
                embed.set_image(url=f"https://gen.plancke.io/exp/{name}.png")
                await ctx.send(embed=embed)

    # Do-Not-Kick-List
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def dnkladd(self, ctx, name = None, x = None, y = None, *, z = None):
        """Adds the user to the do-not-kick-list!
        """
        if name is not None:
            ign = await hypixel.get_dispname(name)
            rank = await hypixel.get_rank(name)
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{ign}') as resp:
                    request = await resp.json(content_type=None)
            
            if resp.status != 200:
                await ctx.send('Unknown IGN!')
            else:
                uuid = request['id']
                with open('dnkl.json') as f:
                    data = json.load(f)

                a, b, c = x.split('/')
                p, q, r = y.split('/')

                if int(b) > 12:
                    embed = discord.Embed(title='Please enter a valid date!', description="`DD/MM/YYYY`", color=0xff0000)
                    await ctx.send(embed=embed)
                if int(q) > 12:
                    embed = discord.Embed(title='Please enter a valid date!', description="`DD/MM/YYYY`", color=0xff0000)
                    await ctx.send(embed=embed)
                if int(b) & int(q) <= 12:
                    dates = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
                            6: "June", 7: "July", 8: "August", 9: "September",
                            10: "October", 11: "November", 12: "December"}
                    start_month = dates.get(int(b))
                    end_month = dates.get(int(q))

                    embed = discord.Embed(title=f"{rank} {ign}", url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                        color=0x0ffff)
                    embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}?size=512&default=MHF_Steve&overlay')
                    embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                    embed.add_field(name="Start:", value=f"{a} {start_month} {c}", inline=False)
                    embed.add_field(name="End:", value=f"{p} {end_month} {r}", inline=False)
                    embed.add_field(name="Reason", value=f"{z}", inline=False)
                    embed.set_author(name="Do not kick list")
                    await ctx.channel.purge(limit=1)
                    message = await ctx.send(embed=embed)

                    dnkl_dict = {ign: message.id}

                    data.update(dnkl_dict)
                    with open('dnkl.json', 'w') as f:
                        json.dump(data, f)
            await session.close()

        else:
            await ctx.send("**What is the name of the user you wish to add to the do not kick list?**")

            name = await self.bot.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            name = name.content
            ign = await hypixel.get_dispname(name)
            rank = await hypixel.get_rank(name)
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{ign}') as resp:
                    request = await resp.json(content_type=None)
            
            if resp.status != 200:
                await ctx.send('Unknown IGN!')  
            else:
                uuid = request['id']
                with open('dnkl.json') as f:
                    data = json.load(f)
            
                await ctx.send("**What is the start date?** (DD/MM/YYYY)")
                start_date = await self.bot.wait_for('message',
                                            check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                start_date = start_date.content
                await ctx.send("**What is the end date?** (DD/MM/YYYY)")
                end_date = await self.bot.wait_for('message',
                                                check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                end_date = end_date.content

                await ctx.send("**What is the reason behind their inactivity?**")

                reason = await self.bot.wait_for('message',
                                                check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                reason = reason.content
                a, b, c = start_date.split('/')
                p, q, r = end_date.split('/')

                if int(b) > 12:
                    embed = discord.Embed(title='Please enter a valid date!', description="`DD/MM/YYYY`",
                                        color=0xff0000)
                    await ctx.send(embed=embed)
                if int(q) > 12:
                    embed = discord.Embed(title='Please enter a valid date!', description="`DD/MM/YYYY`",
                                        color=0xff0000)
                    await ctx.send(embed=embed)
                if int(b) & int(q) <= 12:
                    dates = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
                            6: "June", 7: "July", 8: "August", 9: "September",
                            10: "October", 11: "November", 12: "December"}
                    start_month = dates.get(int(b))
                    end_month = dates.get(int(q))

                    embed = discord.Embed(title=f"{rank} {ign}", url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                        color=0x0ffff)
                    embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}?size=512&default=MHF_Steve&overlay')
                    embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                    embed.add_field(name="Start:", value=f"{a} {start_month} {c}", inline=False)
                    embed.add_field(name="End:", value=f"{p} {end_month} {r}", inline=False)
                    embed.add_field(name="Reason", value=f"{reason}", inline=False)
                    embed.set_author(name="Do not kick list")
                    
                    message = await self.bot.dnkl_channel.send(embed=embed)

                    dnkl_dict = {ign: message.id}

                    data.update(dnkl_dict)
                    with open('dnkl.json', 'w') as f:
                        json.dump(data, f)
            await session.close()

    @commands.command(aliases=['dnklrmv'])
    @commands.has_permissions(manage_messages=True)
    async def dnklremove(self, ctx, name):
        """Removes a user from the do not kick list!
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                request = await resp.json(content_type=None)
        if resp.status != 200:
            await ctx.send('Unknown IGN!')
        else:
            ign = request['name']
            with open("dnkl.json", 'r') as f:
                data = json.load(f)

            if ign not in data.keys():
                await ctx.send('This player is not on the Do-not-kick-list!')

            msgid = f"{data[ign]}"

            data.pop(ign)
            with open('dnkl.json', 'w') as f:
                json.dump(data, f)

            msg = await self.bot.dnkl_channel.fetch_message(msgid)
            await msg.delete()

            await ctx.send(f'{ign} has been removed from the do-not-kick-list!')
        await session.close()


    @commands.command()
    async def dnkllist(self, ctx, raw=None):
        name = ""
        with open('dnkl.json') as f:
            data = json.load(f)
        if raw is not None:
            await ctx.author.send(data)
        else:
            keys = data.keys()
            for x in keys:
                name = name + f"{x}\n"

            embed = discord.Embed(title='The people on the do not kick list are as follows',
                                description=name,
                                color=0x8368ff)
            embed.set_footer(text=f'Total: {len(keys)}')
            await ctx.send(embed=embed)


    @commands.command(aliases=["gi"])
    async def ginfo(self, ctx, *, name):
        """Gives basic information about the requested guild.
        """
        async with ctx.channel.typing():
            req = await hypixel.get_guild_data(name)

            'GUILD NAME'
            if len(req) > 2:
                gname = req["name"]
                print(f'Guild name acquired - {gname}')
                guild = f"{gname}"
            else:
                print("The user is not in any guild!")
                await ctx.send('The user is not in any guild')
            'GUILD TAG'
            gtag = req["tag"]
            print("Gtag acquired")
            gtag = f"[{gtag}]"

            'GUILD LEVEL'
            glvl = req['level']

            'GUILD DESCRIPTION'
            gdesc = req['description']
            if gdesc is None:
                gdesc = 'No guild description.'

            'GUILD LEGACY RANK'
            if "legacy_ranking" in req:
                glg = req["legacy_ranking"]

                glg = f"{glg}"
            else:
                print('Not a legacy guild!')
                glg = '-'

            'JOINABILITY'
            if req["joinable"] is True:
                joinable = "Yes"
            else:
                joinable = "No"

            'PUBLICLY LISTED'
            if req["public"] is True:
                publiclisting = "Yes"
            else:
                publiclisting = "No"

            'ONLINE RECORD'
            onlinerecord = await hypixel.get_guild_onlinerecord(name)

            'TOTAL MEMBERS'
            gmembers = len(req["members"])

            # EMBED
            embed = discord.Embed(title=f"{guild} {gtag}", url=f"https://plancke.io/hypixel/guild/name/{name}",
                                description=f"{gdesc}", color=0x9900ff)
            embed.add_field(name="Level:", value=f"`{glvl}`", inline=True)
            embed.add_field(name="Members:", value=f"`{gmembers}/125`", inline=True)
            embed.add_field(name="Legacy Rank:", value=f"`{glg}`", inline=True)
            embed.add_field(name="Joinable:", value=f"`{joinable}`", inline=True)
            embed.add_field(name="Publicly Listed:", value=f"`{publiclisting}`", inline=True)
            embed.add_field(name="Online players record:", value=f"`{onlinerecord}`", inline=True)
            embed.set_author(name="Guild Stats")
            await ctx.send(embed=embed)

    @commands.command(aliases=['ge'])
    async def gexp(self, ctx, gname):
        """Lists the guild experience of the requested guild!
        """
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = hypixel.get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.hypixel.net/guild?key={api}&name={gname}') as req:
                req = await req.json()
                await session.close()
        array = {}
        exp = 0
        async with ctx.channel.typing():
            for i in range(len(req['guild']['members'])):
                uuid = req['guild']['members'][i]['uuid']
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as names:
                        names = await names.json()

                name = names['name'] + f" [{req['guild']['members'][i]['rank']}]"
                expHistory = sum(req['guild']['members'][i]['expHistory'].values())
                exp += expHistory
                array[name] = exp
                exp = 0


            await msg.edit(content="**Please wait!**\n `SENDING!`")
            sortedList = sorted(array.items(), key=lambda x: x[1], reverse=True)

            x = 0
            embed = discord.Embed(title=f"Here's the guild experience of all users!",
                                description=f"Total: {len(sortedList)}",
                                color=0x8368ff)
            if len(sortedList) <= 25:
                for user in sortedList:
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)
                await ctx.send(embed=embed)
            else:
                for user in sortedList:
                    x = x + 1
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)

                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0x8368ff)
                    elif x == len(sortedList):
                        await ctx.send(embed=embed)
            await msg.delete()

    @commands.command()
    async def gactive(self, ctx):
        """Lists all the users in the guild who are eligible for active rank.
        """
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        gname = 'Rowdies'
        link = f'https://api.slothpixel.me/api/guilds/{gname}'
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                g = await resp.json()
        array = {}
        exp = 0
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 5 seconds`")
        async with ctx.channel.typing():
            for i in range(len(g['members'])):
                expHistory = sum(g['members'][i]['exp_history'].values())
                if expHistory >= self.bot.active:
                    uuid = g['members'][i]['uuid']
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                            a = await resp.json()
                    name = a['name'] + f"[{g['members'][i]['rank']}]"
                    exp += expHistory
                    array[name] = exp
                    exp = 0
                else:
                    pass
            sortedList = sorted(array.items(), key=lambda x: x[1], reverse=True)
            await msg.edit(content="**Please wait!**\n `SENDING!`")
            embed = discord.Embed(title=f"Here's the guild experience of all active users!",
                                description=f"Total: {len(sortedList)}", color=0x8368ff)
            if len(sortedList) <= 25:
                for user in sortedList:
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)
                await ctx.send(embed=embed)
            else:
                for user in sortedList:
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)

                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0x9900ff)
                    elif len(embed.fields) == len(sortedList):
                        await ctx.send(embed=embed)
            await msg.delete()

    @commands.command()
    async def ginactive(self, ctx):
        """Lists all the users in the guild who don't meet the guild requirements.
        """
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        gname = 'Rowdies'
        link = f'https://api.slothpixel.me/api/guilds/{gname}'
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                g = await resp.json()
        array = {}
        exp = 0
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 10 seconds!`")
        async with ctx.channel.typing():
            for i in range(len(g['members'])):
                expHistory = sum(g['members'][i]['exp_history'].values())
                if expHistory < self.bot.inactive:
                    uuid = g['members'][i]['uuid']
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                            a = await resp.json()
                    name = a['name']
                    rank = g['members'][i]['rank']
                    name = name + f'[{rank}]'
                    exp += expHistory
                    array[name] = exp
                    exp = 0
                else:
                    pass
            sortedList = sorted(array.items(), key=lambda x: x[1], reverse=True)
            await msg.edit(content="**Please wait!**\n `SENDING!`")
            x = 0
            embed = discord.Embed(title=f"Here's a list of all inactive members along with their weekly guild experience!",
                                description=f"Total: {len(sortedList)}", color=0x8368ff)
            if len(sortedList) <= 25:
                for user in sortedList:
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)
                await ctx.send(embed=embed)
            else:
                for user in sortedList:
                    x = x + 1
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)

                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0x8368ff)
                    elif x == len(sortedList):
                        await ctx.send(embed=embed)
            await msg.delete()

    @commands.command(aliases=['gr'])
    async def grank(self, ctx, reqrank):
        """Lists the guild experience of users with the specified rank.
        """
        reqrank = reqrank.capitalize()
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        gname = 'Rowdies'
        link = f'https://api.slothpixel.me/api/guilds/{gname}'
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                g = await resp.json()
                await session.close()
        array = {}
        exp = 0
        if reqrank == "Member":
            time = "15 Seconds"
        elif reqrank == "Veteran":
            time = "10 Seconds"
        elif reqrank == "Active":
            time = "5 Seconds"
        elif reqrank == "Admin":
            time = "5 Seconds"
        elif reqrank == "Officer":
            time = "5 Seconds"
        else:
            time = "10 Seconds"
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: {time}`")
        async with ctx.channel.typing():

            for i in range(len(g['members'])):
                rank = g['members'][i]['rank']
                if rank == reqrank:
                    uuid = g['members'][i]['uuid']
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}') as resp:
                            a = await resp.json()
                            await session.close()
                    name = a['name']
                    expHistory = sum(g['members'][i]['exp_history'].values())
                    exp += expHistory
                    array[name] = exp
                    exp = 0
                else:
                    pass
            await msg.edit(content="**Please wait!**\n `SENDING!`")
            sortedList = sorted(array.items(), key=lambda x: x[1], reverse=True)
            x = 0
            embed = discord.Embed(title=f"Here's the guild experience of all users with the {reqrank} rank!",
                                description=f"Total: {len(sortedList)}", color=0x8368ff)
            if len(sortedList) <= 25:
                for user in sortedList:
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)
                await ctx.send(embed=embed)
            else:
                for user in sortedList:
                    x = x + 1
                    embed.add_field(name=f"{user[0]}", value=(format(user[1], ',d')), inline=True)
                    if len(embed.fields) >= 25:
                        await ctx.send(embed=embed)
                        embed.clear_fields()
                        embed = discord.Embed(title="", color=0x8368ff)
                    elif x == len(sortedList):
                        await ctx.send(embed=embed)
            await msg.delete()

    @commands.command(aliases=['gm', 'g'])
    async def gmember(self, ctx, name=None):
        """Gives the guild experience earned by the user over the course of a week.
        """
        if name is None:
            name = ctx.author.nick
            if name is None:
                name = ctx.author.name
        results = []
        dates = []
        weeklyexp = []
        if name in ('top', 'Top'):
            embed = discord.Embed(title="Incorrect syntax!",
                                description="The command you're trying to use is `,gtop`", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                    request = await resp.json(content_type=None)
            if resp.status != 200:
                await ctx.send('Unknown IGN!')
            else:
                name = request['name']
                uuid = request['id']
                api = hypixel.get_api()
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}') as resp:
                        req = await resp.json()
                        await session.close()

                if "guild" not in req or req['guild'] is None:
                    embed = discord.Embed(title=f"{name}", url=f'https://plancke.io/hypixel/player/stats/{name}',
                                        color=0xf04747)
                    embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                    embed.add_field(name="Guildless!",
                                    value="You must be in a guild for the command to work!")
                    await ctx.send(embed=embed)
                else:
                    gname = req['guild']['name']
                    for member in req['guild']["members"]:
                        if uuid == member["uuid"]:
                            joined = member['joined']
                            dt = str(datetime.fromtimestamp(int(str(joined)[:-3])))
                            dt = (dt[0:10])
                            rank = member['rank']
                            if "questParticipation" in member:
                                cq = member['questParticipation']
                            else:
                                cq = 0
                            expHistory = member['expHistory']

                            totalexp = member['expHistory']
                            totalexp = sum(totalexp.values())

                            if rank == "Resident":
                                if totalexp > self.bot.resident_req:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("res_met")
                                else:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("res_not_met")
                            else:
                                if totalexp > self.bot.active:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("active")
                                elif totalexp > self.bot.inactive:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("member")
                                else:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("inactive")

                            totalexp = (format(totalexp, ',d'))
                            for key, value in expHistory.items():
                                results.append([key,value])
                                dates.append(key)
                                weeklyexp.append(int(value))


                            dictionary = {
                                0: 'Today:',
                                1: 'Yesterday:',
                                2: 'Two days ago:',
                                3: 'Three days ago:',
                                4: 'Four days ago:',
                                5: 'Five days ago:',
                                6: 'Six days ago:'
                            }
                            z = 0
                            gexphistory = ""
                            for x in results:
                                if z < 7:
                                    date = dictionary.get(z, "None")
                                    gexphistory = gexphistory + f"➤ {date} **{format(weeklyexp[z],',d')}**\n"
                                    z = z + 1

                                else:
                                    break
                            if "commands" not in ctx.channel.name:
                                name = name.replace("_",        "\_")
                                await ctx.send(f"__**{name}**__\n**Guild Experience -** `{totalexp}`")
                            else:
                                embed = discord.Embed(title=f"{name}",
                                                    url=f'https://plancke.io/hypixel/player/stats/{name}',
                                                    color=colour)
                                embed.set_author(name=gname, url=f'https://plancke.io/hypixel/guild/player/{name}')
                                embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                embed.add_field(name="Rank:", value=rank, inline=True)
                                embed.add_field(name="Joined:", value=dt, inline=True)
                                embed.add_field(name="Quests Completed:", value=cq, inline=True)
                                embed.add_field(name="Overall Exp:", value=f"`{totalexp}`", inline=False)
                                embed.add_field(name="GEXP History", value=gexphistory, inline=False)


                                weeklyexp.reverse()
                                dates.reverse()
                                chart = QuickChart()
                                chart.width = 1000
                                chart.height = 500
                                chart.background_color = "transparent"
                                chart.config = {
                                    "type": "line",
                                    "data": {
                                        "labels": dates,
                                        "datasets": [{
                                            "label": "Experience",
                                            "data": weeklyexp,
                                            "lineTension": 0.4,
                                            "backgroundColor": GraphColor,
                                            "borderColor": GraphBorder
                                        }]
                                    }
                                }
                                chart_url = chart.get_url()
                                embed.set_image(url=chart_url)
                                await ctx.send(embed=embed)
            await session.close()

    @commands.command(aliases=['dnklchk'])
    async def dnklcheck(self, ctx, name=None):
        """A command to check whether or not you can apply for the do-not-kick-list.
        """
        if name is None:
            author = ctx.author
            name = author.nick
            if name is None:
                x = author.name
                name = x
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                request = await resp.json(content_type=None)  

        if resp.status != 200:
            await ctx.send('Unknown IGN!')
        else:      
            name = request['name']
            uuid = request['id']
            api = hypixel.get_api()
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}') as resp:
                    data = await resp.json()
                    if data['guild'] == None:
                        await ctx.send('You are not in a guild!')
                        return
                    await session.close()
            gname = data['guild']['name']
            if gname != 'Miscellaneous':
                await ctx.send('The user is not in Miscellaneous')
            if len(data) < 2:
                print("The user is not in any guild!")
                await ctx.send('The user is not in any guild')
            else:
                for member in data["guild"]["members"]:
                    if uuid == member["uuid"]:
                        member = member
                        totalexp = member['expHistory']
                        totalexp = int(sum(totalexp.values()))
                        if totalexp >= self.bot.dnkl:
                            eligiblity = True
                        else:
                            eligiblity = False
                        totalexp = (format(totalexp, ',d'))
                        if eligiblity is False:
                            embed = discord.Embed(title=name,
                                                url=f'https://visage.surgeplay.com/full/832/{uuid}',
                                                color=0xff3333)
                            embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                            embed.set_author(name="Do-not-kick-list: Eligibility Check")
                            embed.add_field(name="You are not eligible to apply for the do not kick list.",
                                            value=f"You need a minimum of {format(self.bot.dnkl,',d')} weekly guild experience.\n You have {totalexp} weekly guild experience.",
                                            inline=True)
                        else:
                            embed = discord.Embed(title=name,
                                                url=f'https://visage.surgeplay.com/full/832/{uuid}',
                                                color=0x333cff)
                            embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                            embed.set_author(name='Do-not-kick-list: Eligibility Check')
                            embed.add_field(name="You are eligible to apply for the do not kick list.",
                                            value=f"You meet the minimum of {format(self.bot.dnkl,',d')} weekly guild experience.\n You have {totalexp} weekly guild experience.",
                                            inline=True)
                        await ctx.send(embed=embed)
        await session.close()

    @commands.command(aliases=["gt"])
    async def gtop(self, ctx):
        """Gives the weekly guild experience leaderboard!
        """
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = hypixel.get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.hypixel.net/guild?key={api}&name=Miscellaneous') as resp:
                req = await resp.json()
                await session.close()
        array = {}
        exp = 0
        async with ctx.channel.typing():
            for i in range(len(req['guild']['members'])):
                uuid = req['guild']['members'][i]['uuid']
                expHistory = sum(req['guild']['members'][i]['expHistory'].values())
                exp += expHistory
                array[uuid] = exp
                exp = 0

            sortedList = sorted(array.items(), key=lambda x: x[1], reverse=True)
            iteration_number = 1
            weeklygexp = f'&f&lWeekly Top&r%5Cn'

            color = {'RED': '&c',
                    'GOLD': '&6',
                    'GREEN': '&a',
                    'YELLOW': '&e',
                    'LIGHT_PURPLE': '&d',
                    'WHITE': '&f',
                    'BLUE': '&9',
                    'DARK_GREEN': '&2',
                    'DARK_RED': '&4',
                    'DARK_AQUA': '&3',
                    'DARK_PURPLE': '&5',
                    'DARK_GRAY': '&8',
                    'BLACK': '&0',
                    'DARK_BLUE': '&1'}
            await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 10 seconds`")



            for user in sortedList:
                if iteration_number < 11:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{user[0]}') as resp:
                            mojang = await resp.json()
                            await session.close()
                    name = mojang['name']

                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://api.hypixel.net/player?key={api}&name={name}") as resp:
                            data = await resp.json()
                            await session.close()

                    if data["player"] is None:
                        return None
                    if "prefix" in data["player"]:
                        player_prefix = (data["player"]["prefix"])
                        if player_prefix == "§d[PIG§b+++§d]":  # Pig+++
                            print('Rank acquired- PIG')
                            playerrank = f"&d[PIG&b+++&d]"
                        elif player_prefix == "§c[SLOTH]":  # Sloth
                            print('Rank acquired- Sloth')
                            playerrank = "&c[SLOTH]"
                        elif player_prefix == "§c[OWNER]":  # Owner
                            print('Rank acquired- Owner')
                            playerrank = "&c[OWNER]"

                    if "newPackageRank" in data["player"]:
                        if "rank" in data["player"]:
                            rank = data["player"]["rank"]
                            if rank == 'YOUTUBER':  # Youtuber
                                playerrank = '&c[&fYOUTUBE&c]'
                            if rank == 'ADMIN':  # Admin
                                print('Rank acquired- Admin')
                                playerrank = '&c[ADMIN]'
                            if rank == 'MODERATOR':  # Moderator
                                print('Rank acquired- Moderator')
                                playerrank = '&2[MOD]'
                            if rank == 'HELPER':  # Helper
                                print('Rank acquired- Helper')
                                playerrank = '&9[HELPER]'

                        else:

                            rank = (data["player"]["newPackageRank"])

                            if rank == 'MVP_PLUS':
                                if "monthlyPackageRank" in data["player"]:

                                    if (data["player"]["monthlyPackageRank"]) == "NONE":  # Had MVP++ but now is an MVP+
                                        if 'rankPlusColor' in data['player']:
                                            pluscolor = color.get(data['player']['rankPlusColor'])
                                            print('Rank acquired- MVP+ (MVP++ sub category)')
                                            playerrank = f'&b[MVP{pluscolor}+&b]'
                                        else:
                                            playerrank = f'&b[MVP&c+&b]'

                                    else:
                                        if 'monthlyRankColor' in data['player']:
                                            if data['player']['monthlyRankColor'] == 'GOLD':  # Gold MVP++
                                                if 'rankPlusColor' in data['player']:  # Gold MVP++ w/custom + colors
                                                    pluscolor = color.get(data['player']['rankPlusColor'])
                                                    print('Rank acquired- MVP++ (Gold + rankPlusColor)')
                                                    playerrank = f'&6[MVP{pluscolor}++&6]'
                                                else:  # Gold MVP++ w/o custom + colors
                                                    playerrank = f'&6[MVP&c++&6]'
                                                    print('Rank acquired- MVP++ (Gold + No rankPlusColor)')

                                            elif data['player']['monthlyRankColor'] == 'AQUA':  # Aqua MVP++ w/custom + colors
                                                if 'rankPlusColor' in data['player']:
                                                    pluscolor = color.get(data['player']['rankPlusColor'])
                                                    print('Rank acquired- MVP++ (Aqua + rankPlusColor)')
                                                    playerrank = f'&b[MVP{pluscolor}++&b]'
                                                else:  # Aqua MVP++ w/o custom + colors
                                                    playerrank = f'&b[MVP&c++&b]'
                                                    print('Rank acquired- MVP++ (Aqua + No rankPlusColor)')
                                        else:
                                            if 'rankPlusColor' in data['player']:
                                                pluscolor = color.get(data['player']['rankPlusColor'])
                                                print('Rank acquired- MVP+ (MVP++ sub category)')
                                                playerrank = f'&b[MVP{pluscolor}+&b]'
                                            else:
                                                playerrank = f'&b[MVP&c+&b]'

                                else:  # MVP+ (No MVP++ subcategory found)
                                    if 'rankPlusColor' in data['player']:
                                        pluscolor = color.get(data['player']['rankPlusColor'])
                                        print('Rank acquired- MVP+ (MVP+ category)')
                                        playerrank = f'&b[MVP{pluscolor}+&b]'
                                    else:
                                        playerrank = f'&b[MVP&c+&b]'
                            elif rank == 'MVP':
                                print('Rank acquired- MVP')
                                playerrank = '&b[MVP]'
                            elif rank == 'VIP_PLUS':
                                print('Rank acquired- VIP+')
                                playerrank = '&a[VIP&6+&a]'
                            elif rank == 'VIP':
                                print('Rank acquired- VIP')
                                playerrank = '&a[VIP]'
                    else:
                        print('Rank acquired- Non')
                        playerrank = '&7'

                    if iteration_number != 10:
                        weeklygexp = weeklygexp + f"&6{iteration_number}. {playerrank} {name} &2{format(user[1], ',d')} Guild Experience%5Cn"
                    else:
                        weeklygexp = weeklygexp + f"&6{iteration_number}. {playerrank} {name} &2{format(user[1], ',d')} Guild Experience"
                    iteration_number = iteration_number + 1
            await msg.delete()
            weeklygexp = weeklygexp.replace('+', '%2B')
            weeklygexp = weeklygexp.replace('&', '%26')
            weeklygexp = weeklygexp.replace(' ', '%20')
            weeklygexp = weeklygexp.replace(',', '%2C')

            url = f"https://chat.miscguild.xyz/render.png?m=custom&d={weeklygexp}&t=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    image_data = BytesIO(await resp.read())
                    await session.close()

            await ctx.send(file=discord.File(image_data, 'gtop.jpg'))

    @commands.command()
    async def dailylb(self, ctx, x=1):
        """Prints the daily guild leaderboard. The value defaults to the day prior.
        """
        await ctx.channel.purge(limit=1)
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = hypixel.get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.hypixel.net/guild?key={api}&name=Miscellaneous') as resp:
                req = await resp.json()
                await session.close()
        array = {}
        async with ctx.channel.typing():
            for i in range(len(req['guild']['members'])):
                uuid = req['guild']['members'][i]['uuid']
                expHistory = list(req['guild']['members'][i]['expHistory'].values())
                date = list(req['guild']['members'][i]['expHistory'].keys())
                date = date[x]
                exp = expHistory[x]
                array[uuid] = exp

            sortedList = sorted(array.items(), key=lambda x: x[1], reverse=True)
            z = 1
            dailygexp = f'&f&lDaily Top - {date}&r%5Cn'

            color = {'RED': '&c',
                    'GOLD': '&6',
                    'GREEN': '&a',
                    'YELLOW': '&e',
                    'LIGHT_PURPLE': '&d',
                    'WHITE': '&f',
                    'BLUE': '&9',
                    'DARK_GREEN': '&2',
                    'DARK_RED': '&4',
                    'DARK_AQUA': '&3',
                    'DARK_PURPLE': '&5',
                    'DARK_GRAY': '&8',
                    'BLACK': '&0',
                    'DARK_BLUE': '&1'}
            await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 10 seconds`")
            for user in sortedList:
                if z < 11:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{user[0]}') as resp:
                            mojang = await resp.json()
                            name = mojang['name']
                            await session.close()

                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://api.hypixel.net/player?key={api}&name={name}") as resp:
                            data = await resp.json()
                            await session.close()

                    print(name)
                    if data["player"] is None:
                        return None
                    if "prefix" in data["player"]:
                        player_prefix = (data["player"]["prefix"])
                        if player_prefix == "§d[PIG§b+++§d]":  #Pig+++
                            print('Rank acquired- PIG')
                            playerrank = f"&d[PIG&b+++&d]"
                        elif player_prefix == "§c[SLOTH]":  #Sloth
                            print('Rank acquired- Sloth')
                            playerrank = "&c[SLOTH]"
                        elif player_prefix == "§c[OWNER]":  #Owner
                            print('Rank acquired- Owner')
                            playerrank = "&c[OWNER]"


                    if "newPackageRank" in data["player"]:
                        if "rank" in data["player"]:
                            rank = (data["player"]["rank"])
                            if rank == 'YOUTUBER':  #Youtuber
                                playerrank = '&c[&fYOUTUBE&c]'
                            if rank == 'ADMIN':  #Admin
                                print('Rank acquired- Admin')
                                playerrank = '&c[ADMIN]'
                            if rank == 'MODERATOR':  #Moderator
                                print('Rank acquired- Moderator')
                                playerrank = '&2[MOD]'
                            if rank == 'HELPER':  #Helper
                                print('Rank acquired- Helper')
                                playerrank = '&9[HELPER]'



                        else:

                            rank = (data["player"]["newPackageRank"])

                            if rank == 'MVP_PLUS':
                                if "monthlyPackageRank" in data["player"]:

                                    if (data["player"]["monthlyPackageRank"]) == "NONE": #Had MVP++ but now is an MVP+
                                        if 'rankPlusColor' in data['player']:
                                            pluscolor = color.get(data['player']['rankPlusColor'])
                                            print('Rank acquired- MVP+ (MVP++ sub category)')
                                            playerrank = f'&b[MVP{pluscolor}+&b]'
                                        else:
                                            playerrank = f'&b[MVP&c+&b]'

                                    else:


                                        if 'monthlyRankColor' not in data['player'] or data['player']['monthlyRankColor'] == 'GOLD': #Gold MVP++
                                            if 'rankPlusColor' in data['player']: #Gold MVP++ w/custom + colors
                                                pluscolor = color.get(data['player']['rankPlusColor'])
                                                print('Rank acquired- MVP++ (Gold + rankPlusColor)')
                                                playerrank = f'&6[MVP{pluscolor}++&6]'
                                            else: #Gold MVP++ w/o custom + colors
                                                playerrank = f'&6[MVP&c++&6]'
                                                print('Rank acquired- MVP++ (Gold + No rankPlusColor)')


                                        elif data['player']['monthlyRankColor'] == 'AQUA': #Aqua MVP++ w/custom + colors
                                            if 'rankPlusColor' in data['player']:
                                                pluscolor = color.get(data['player']['rankPlusColor'])
                                                print('Rank acquired- MVP++ (Aqua + rankPlusColor)')
                                                playerrank = f'&b[MVP{pluscolor}++&b]'
                                            else: #Aqua MVP++ w/o custom + colors
                                                playerrank = f'&b[MVP&c++&b]'
                                                print('Rank acquired- MVP++ (Aqua + No rankPlusColor)')



                                else: #MVP+ (No MVP++ subcategory found)
                                    if 'rankPlusColor' in data['player']:
                                        pluscolor = color.get(data['player']['rankPlusColor'])
                                        print('Rank acquired- MVP+ (MVP+ category)')
                                        playerrank = f'&b[MVP{pluscolor}+&b]'
                                    else:
                                        playerrank = f'&b[MVP&c+&b]'
                            elif rank == 'MVP':
                                print('Rank acquired- MVP')
                                playerrank = '&b[MVP]'
                            elif rank == 'VIP_PLUS':
                                print('Rank acquired- VIP+')
                                playerrank = '&a[VIP&6+&a]'
                            elif rank == 'VIP':
                                print('Rank acquired- VIP')
                                playerrank = '&a[VIP]'
                    else:
                        print('Rank acquired- Non')
                        playerrank = '&7'





                    if z != 10:
                        dailygexp = dailygexp + f"&6{z}. {playerrank} {name} &2{format(user[1],',d')} Guild Experience%5Cn"
                    if z == 10:
                        dailygexp = dailygexp + f"&6{z}. {playerrank} {name} &2{format(user[1], ',d')} Guild Experience"
                    z = z + 1
            await msg.delete()
            dailygexp = dailygexp.replace('+','%2B')
            dailygexp = dailygexp.replace('&','%26')
            dailygexp = dailygexp.replace(' ','%20')
            dailygexp = dailygexp.replace(',','%2C')

            url = f"https://chat.miscguild.xyz/render.png?m=custom&d={dailygexp}&t=1"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    image_data = BytesIO(await resp.read())
                    await session.close()

                    
            await ctx.send(file=discord.File(image_data, 'dailylb.jpg'))

def setup(bot):
    bot.add_cog(Hypixel(bot))
