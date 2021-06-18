import discord, json, random, math, requests
import hypixel
import time
import aiohttp
import asyncio
from quickchart import QuickChart
from discord.ext import commands
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

with open('config.json') as config_file:
    configFile = json.load(config_file)


intents = discord.Intents.default()
intents.reactions = True
intents.members = True
client = commands.Bot(command_prefix=[',', '@Miscellaneous#4333'], intents=intents)

client.remove_command('help')


resident_req = int(50000)
active = int(275000)
inactive = int(100000)
dnkl = int(200000)
new_member = int(25000)


"-------------------[[------------------------------------------------------------------------------General--------------------------------------------------------------------------------------------------------------------"

@client.event
async def on_ready():
    try:
        statuses = ['with Miscellaneous members!', 'with cool kids of Miscellaneous!']
        print('The Bot is up and running!')
        for status in statuses:
            await client.change_presence(status=discord.Status.idle, activity=discord.Game(status))
            await asyncio.sleep(600)

        with open('dnkl.json', 'r') as f:
            data = str(f.read()).replace("'", '"')
        with open('dnkl.json', 'w') as f:
            f.write(data)
    except Exception as e:
        print(e)
client.loop.create_task(on_ready())

# Error Message
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Invalid Command!",
                              description=f"Use `help` for a list of all commands!",
                              color=0xff0000)
        await ctx.send(embed=embed)

@client.event
async def on_member_join(member):
    try:
        channel = client.get_channel(714882620001091585)
        role = discord.utils.get(member.guild.roles, name="New Member")
        await member.add_roles(role)

        embed = discord.Embed(title=f"Welcome to the Miscellaneous Discord, {member.name}", color=0x8368ff)
        embed.add_field(name="Register using the following command:", value="**,register** `Your Minecraft Name`", inline=False)
        embed.set_footer(text="Example:\n,register John")

        await channel.send(embed=embed)

    except Exception as e:
        print(e)




@client.command(aliases=['req', 'requirement', 'Req', 'Requirement', 'Requirements'])
async def requirements(ctx):
    try:
        embed = discord.Embed(title="Miscellaneous Guild Requirements",
                              description="These requirements are subject to change!",
                              color=0x8368ff)
        embed.add_field(name="Active", value=f"•  {format(active,',d')} Weekly Guild Experience", inline=False)
        embed.add_field(name="Do Not Kick List Eligibility", value=f"•  {format(dnkl,',d')} Weekly Guild Experience", inline=False)
        embed.add_field(name="Resident", value=f"•  {format(resident_req,',d')} Weekly Guild Experience", inline=False)
        embed.add_field(name="Member", value=f"•  {format(inactive,',d')} Weekly Guild Experience", inline=False)
        embed.add_field(name="New Member", value=f"•  {format(new_member,',d')} Daily Guild Experience", inline=False)
        embed.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                              "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)


@client.command(aliases=['Ticket', 'Tickets', 'ticket'])
async def tickets(ctx):
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
                              "> Staff  Application\n"
                              "> Other",
                        inline=False)
        embed.add_field(name="React to the message sent by @TicketTool",
                        value="The following image shows you what you need to react to.",
                        inline=False)
        embed.set_image(url=f"https://media.discordapp.net/attachments/522930919984726016/775953643991990272/unknown.png?width=1069&height=702")
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)


@client.command(aliases=['res', 'Res', 'Resident'])
async def resident(ctx):
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
        embed.set_footer(text=f"Everyone who has the resident rank must get {format(resident_req,',d')} weekly guild experience! (Except YouTubers)")
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)




"------------------------------------------------------------------------------------------------------------------Tickets------------------------------------------------------------------------------------------------------"


# Ticket Handling
@client.event
async def on_guild_channel_create(channel):
    try:
        while True:
            if channel.category.name == "RTickets":
                embed = discord.Embed(title="Do you wish to join Miscellaneous in-game?", color=0x8368ff)
                embed.add_field(name="If you do", value="Type `Yes`")
                embed.add_field(name="If you don't", value="Type `No`")
                await channel.send(embed=embed)
                reply = await client.wait_for('message', check=lambda x: x.channel == channel)
                reply = reply.content
                reply = reply.capitalize()
                try:
                    if reply in ('Yes', 'Yeah', 'Ye', 'Yea'):
                        await channel.send(
                            'Alright. Kindly wait until staff get in contact with you.'
                            '\n`You are recommended to leave your present guild (if any) so that staff can invite you to Miscellaneous ASAP`'
                            '\nIf you get in the guild and want the member role in the discord, use ,sync `Your Minecraft Name` ! ')
                        time.sleep(3)
                        embed1 = discord.Embed(title="Miscellaneous Guild Requirements",
                                               description="These requirements are subject to change!",
                                               color=0x8368ff)
                        embed1.set_author(name="While you wait, kindly take a look a the guild requirements!")
                        embed1.add_field(name="Active",
                                         value=f"•  {format(active,',d')} Weekly Guild Experience",
                                         inline=False)
                        embed1.add_field(name="Do Not Kick List Eligibility",
                                         value=f"•  {format(dnkl,',d')} Weekly Guild Experience",
                                         inline=False)
                        embed1.add_field(name="Resident", value=f"•  {format(resident_req,',d')} Weekly Guild Experience",
                                         inline=False)
                        embed1.add_field(name="Member",
                                         value=f"•  {format(inactive,',d')} Weekly Guild Experience",
                                         inline=False)
                        embed1.add_field(name="New Member",
                                         value=f"•  {format(new_member,',d')} Daily Guild Experience",
                                         inline=False)
                        embed1.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                                               "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
                        await channel.send(embed=embed1)
                        break
                    elif reply in ('No', 'Nah', 'Nope'):
                        embed = discord.Embed(title="Did you join the discord to organize a GvG with Miscellaneous?",
                                              color=0x8368ff)
                        embed.add_field(name="If yes", value="Type `Yes`")
                        embed.add_field(name="If not", value="Type `No`")
                        await channel.send(embed=embed)
                        noreply = await client.wait_for('message', check=lambda x: x.channel == channel)
                        noreply = noreply.content
                        noreply = noreply.capitalize()
                        if noreply in ('Yes', 'Yeah', 'Ye', 'Yea'):
                            embed = discord.Embed(title="In order to organize a GvG with miscellaneous, "
                                                        "kindly list the following and await staff assistance!",
                                                  description="• Your guild's plancke"
                                                              "\n• Your preferred gamemode"
                                                              "\n• Your preferred timezone"
                                                              "\n• Number of players",
                                                  color=0x8368ff)
                            embed.set_footer(text="Upon completion of all of the above, kindly await staff assistance!")
                            await channel.send(embed=embed)
                            break
                        elif noreply == "No":
                            await channel.send(
                                "**Okay, kindly specify your reason behind joining the Miscellaneous discord and then await staff help!**")
                            break
                        else:
                            embed = discord.Embed(title="My massive computer brain thinks you made a mistake.",
                                                  color=0xff0000)
                            embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
                            embed.add_field(name="If this is false", value="Type `No`", inline=False)
                            await channel.send(embed=embed)
                            errorreply = await client.wait_for('message', check=lambda x: x.channel == channel)
                            errorreply = errorreply.content
                            errorreply = errorreply.capitalize()
                            if errorreply in ('Yes', 'Yeah', 'Ye', 'Yea'):
                                embed = discord.Embed(title="Great! Let's start over!",
                                                      color=0x8368ff)
                                await channel.send(embed=embed)
                            else:
                                embed = discord.Embed(title="Alright! Kindly specify why you joined the discord and await staff assistance!",
                                                      color=0x8368ff)
                                await channel.send(embed=embed)
                                break
                    else:
                        embed = discord.Embed(title="My massive computer brain thinks you made a mistake.",
                                              color=0xff0000)
                        embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
                        embed.add_field(name="If this is false", value="Type `No`", inline=False)
                        await channel.send(embed=embed)
                        errorreply = await client.wait_for('message', check=lambda x: x.channel == channel)
                        errorreply = errorreply.content
                        errorreply = errorreply.capitalize()
                        if errorreply in ('Yes', 'Yeah', 'Ye', 'Yea'):
                            embed = discord.Embed(title="Great! Let's start over!",
                                                  color=0x8368ff)
                            await channel.send(embed=embed)
                        else:
                            embed = discord.Embed(title="Alright! Kindly specify why you joined the discord and await staff assistance!",
                                                  color=0x8368ff)
                            await channel.send(embed=embed)
                            break
                except Exception as e:
                    embed = discord.Embed(title="Alright! Kindly specify why you joined the discord and await staff assistance!",
                                          color=0x8368ff)
                    await channel.send(embed=embed)
                    error_channel = client.get_channel(523743721443950612)
                    print(e)
                    await error_channel.send(
                        f"Error in {channel.name} while dealing with registration tickets\n{e}\n<@!326399363943497728>")

                    break
            elif channel.category.name == '🎫 Ticket Section':
                time.sleep(3)
                embed = discord.Embed(title="What's your reason behind creating this ticket?",
                                      description="Please reply with your reason from the list given below!",
                                      color=0x8368ff)
                embed.add_field(name="Do-Not-Kick-List", value="Reply with `DNKL`", inline=False)
                embed.add_field(name="Role/Username Change", value="Reply with `Role`", inline=False)
                embed.add_field(name="Report", value="Reply with `Report`", inline=False)
                embed.add_field(name="Problem/Query/Complaint/Suggestion", value="Reply with `General`", inline=False)
                embed.add_field(name="Milestone", value="Reply with `Milestone`", inline=False)
                embed.add_field(name="Staff Application", value="Reply with `Staff`", inline=False)
                embed.add_field(name="GvG Application", value="Reply with `GvG`", inline=False)
                embed.add_field(name="Other", value="Reply with `Other`", inline=False)
                await channel.send(embed=embed)
                reply = await client.wait_for('message', check=lambda x: x.channel == channel)
                author = reply.author
                name = author.nick
                if name is None:
                    name = author.name
                reply = reply.content
                reply = reply.capitalize()

                if reply in ("Dnkl", "Do not kick list", "Do-Not-Kick-List"):

                    if name is None:
                        x = author.name
                        name = x
                    await channel.edit(name=f"DNKL-{name}", category=discord.utils.get(channel.guild.categories, name="DNKL"))
                    request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
                    if request.status_code != 200:
                        await channel.send('Unknown IGN!')
                    else:
                        name = request.json()['name']
                        uuid = request.json()['id']
                        api = hypixel.get_api()
                        data = requests.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}').json()
                        gname = data['guild']['name']
                        if gname != 'Miscellaneous':
                            await channel.send('You are not in Miscellaneous')
                        if len(data) < 2:
                            print("The user is not in any guild!")
                            await channel.send('You are not in any guild')
                        else:
                            for member in data["guild"]["members"]:
                                if uuid == member["uuid"]:
                                    member = member
                                    totalexp = member['expHistory']
                                    totalexp = int(sum(totalexp.values()))
                                    if totalexp >= 200000:
                                        eligiblity = True
                                    else:
                                        eligiblity = False
                                    totalexp = (format(totalexp, ',d'))
                                    if eligiblity is False:
                                        embed = discord.Embed(title=name,
                                                              url=f'https://visage.surgeplay.com/full/832/{uuid}',
                                                              color=0xff3333)
                                        embed.set_thumbnail(
                                            url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                        embed.set_author(name="Do-not-kick-list: Eligibility Check")
                                        embed.set_footer(text="Miscellaneous Bot | Coded by Rowdies")
                                        embed.add_field(name="You are not eligible to apply for the do not kick list.",
                                                        value=f"You need a minimum of {format(dnkl,',d')} weekly guild experience."
                                                              f"\n You have {totalexp} weekly guild experience.",
                                                        inline=True)
                                        await channel.send(embed=embed)
                                        await channel.send(
                                            "Even though you do not meet the requirements, "
                                            "you might still be accepted so we shall proceed with the application process!")

                                        await channel.send("**When will your inactivity begin? (Start date) (DD/MM/YYYY)**")
                                        start = await client.wait_for('message', check=lambda x: x.author == author and x.channel == channel)
                                        start = start.content
                                        await channel.send('**When will your inactivity end? (End date) (DD/MM/YYYY)**')
                                        end = await client.wait_for('message', check=lambda x: x.author == author and x.channel == channel)
                                        end = end.content
                                        await channel.send("**What's the reason behind your inactivity?**")
                                        reason = await client.wait_for('message', check=lambda x: x.author == author and x.channel == channel)
                                        reason = reason.content

                                        await channel.send(
                                            f"Alright! Kindly await staff assistance!"
                                            f"\n**Start:** {start}"
                                            f"\n**End:** {end}"
                                            f"\n**Reason:** {reason}"
                                            f"\n*If you made an error, kindly notify staff by typing after this message*"
                                            f"\n\n||,dnkl {name} {author.mention} {start} {end} {reason}||")

                                    else:
                                        embed = discord.Embed(title=name,
                                                              url=f'https://visage.surgeplay.com/full/832/{uuid}',
                                                              color=0x333cff)
                                        embed.set_thumbnail(
                                            url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                        embed.set_author(name='Do-not-kick-list: Eligibility Check')
                                        embed.set_footer(text="Miscellaneous Bot | Coded by Rowdies")
                                        embed.add_field(name="You are eligible to apply for the do not kick list.",
                                                        value=f"You meet the minimum of {format(dnkl,',d')} weekly guild experience."
                                                              f"\n You have {totalexp} weekly guild experience.",
                                                        inline=True)
                                        await channel.send(embed=embed)

                                        await channel.send("**When will your inactivity begin? (Start date) (DD/MM/YYYY)**")
                                        start = await client.wait_for('message', check=lambda x: x.author == author and x.channel == channel)
                                        start = start.content
                                        await channel.send('**When will your inactivity end? (End date) (DD/MM/YYYY)**')
                                        end = await client.wait_for('message', check=lambda x: x.author == author and x.channel == channel)
                                        end = end.content
                                        await channel.send("**What's the reason behind your inactivity?**")
                                        reason = await client.wait_for('message', check=lambda x: x.author == author and x.channel == channel)
                                        reason = reason.content

                                        await channel.send(
                                            f"Alright! Kindly await staff assistance!"
                                            f"\n**Start:** {start}"
                                            f"\n**End:** {end}"
                                            f"\n**Reason:** {reason}"
                                            f"\n*If you made an error, kindly notify staff by typing after this message*"
                                            f"\n\n||,dnkladd {name} {author.mention} {start} {end} {reason}||"
                                            )

                                        await channel.send("**Staff, what do you wish to do with this dnkl request?**"
                                                            f"\nReply with `Approve` to approve the do-not-kick-list request"
                                                            f"\nReply with `Deny` to deny the do-not-kick-list request"
                                                            f"\nReply with `Error` if the user made an error while applying for the do not kick list")

                                        while True:
                                            action = await client.wait_for('message', check=lambda
                                                x: staff in x.author.roles)
                                            action = (action.content).capitalize()
                                            if action in ('Approve','Deny','Error'):
                                                if action == "Approve":
                                                    a, b, c = start.split('/')
                                                    p, q, r = end.split('/')
                                                    ign = hypixel.get_dispname(name)
                                                    rank = hypixel.get_rank(name)
                                                    dates = {1: "January", 2: "February", 3: "March", 4: "April",
                                                             5: "May",
                                                             6: "June", 7: "July", 8: "August", 9: "September",
                                                             10: "October", 11: "November", 12: "December"}
                                                    start_month = dates.get(int(b))
                                                    end_month = dates.get(int(q))

                                                    embed = discord.Embed(title=f"{rank} {ign}",
                                                                          url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                                                          color=0x0ffff)
                                                    embed.set_thumbnail(
                                                        url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                                    embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                                                    embed.add_field(name="Start:", value=f"{a} {start_month} {c}",
                                                                    inline=False)
                                                    embed.add_field(name="End:", value=f"{p} {end_month} {r}",
                                                                    inline=False)
                                                    embed.add_field(name="Reason", value=f"{reason}", inline=False)
                                                    embed.set_author(name="Do not kick list")
                                                    await channel.channel.purge(limit=1)
                                                    dnkl_channel = client.get_channel(629564802812870657)
                                                    message = await dnkl_channel.send(embed=embed)

                                                    with open('dnkl.json') as f:
                                                        data = json.load(f)
                                                    dnkl_dict = {ign: message.id}

                                                    data.update(dnkl_dict)
                                                    with open('dnkl.json', 'w') as f:
                                                        json.dump(data, f)
                                                    break

                                                elif action == "Deny":
                                                    await channel.send("**This do not kick list request has been denied!")

                                                elif action == "Error":
                                                    await channel.send(
                                                        "**What is the name of the user you wish to add to the do not kick list?**")

                                                    name = await client.wait_for('message', check=lambda
                                                        x: x.channel == channel.channel)
                                                    name = name.content
                                                    ign = hypixel.get_dispname(name)
                                                    rank = hypixel.get_rank(name)
                                                    request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{ign}')
                                                    uuid = request.json()['id']
                                                    with open('dnkl.json') as f:
                                                        data = json.load(f)
                                                    if request.status_code != 200:
                                                        await channel.send('Unknown IGN!')
                                                    else:
                                                        await channel.send("**What is the start date?** (DD/MM/YYYY)")
                                                        start_date = await client.wait_for('message',
                                                                                           check=lambda
                                                                                               x: x.channel == channel.channel)
                                                        start_date = start_date.content
                                                        await channel.send("**What is the end date?** (DD/MM/YYYY)")
                                                        end_date = await client.wait_for('message',
                                                                                         check=lambda
                                                                                             x: x.channel == channel.channel)
                                                        end_date = end_date.content
                                                        a, b, c = start_date.split('/')
                                                        p, q, r = end_date.split('/')

                                                        await channel.send("**What's the reason for inactivity?**")
                                                        reason = await client.wait_for('message',
                                                                                         check=lambda
                                                                                             x: x.channel == channel.channel)
                                                        reason = reason.content

                                                        if int(b) > 12:
                                                            embed = discord.Embed(title='Please enter a valid date!',
                                                                                  description="`DD/MM/YYYY`",
                                                                                  color=0xff0000)
                                                            await channel.send(embed=embed)
                                                        if int(q) > 12:
                                                            embed = discord.Embed(title='Please enter a valid date!',
                                                                                  description="`DD/MM/YYYY`",
                                                                                  color=0xff0000)
                                                            await channel.send(embed=embed)
                                                        if int(b) & int(q) <= 12:
                                                            dates = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
                                                                     6: "June", 7: "July", 8: "August", 9: "September",
                                                                     10: "October", 11: "November", 12: "December"}
                                                            start_month = dates.get(int(b))
                                                            end_month = dates.get(int(q))

                                                            embed = discord.Embed(title=f"{rank} {ign}",
                                                                                  url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                                                                  color=0x0ffff)
                                                            embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                                            embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                                                            embed.add_field(name="Start:", value=f"{a} {start_month} {c}",
                                                                            inline=False)
                                                            embed.add_field(name="End:", value=f"{p} {end_month} {r}", inline=False)
                                                            embed.add_field(name="Reason", value=f"{reason}", inline=False)
                                                            embed.set_author(name="Do not kick list")
                                                            await channel.channel.purge(limit=1)
                                                            dnkl_channel = client.get_channel(629564802812870657)
                                                            message = await dnkl_channel.send(embed=embed)


                                                            dnkl_dict = {ign: message.id}

                                                            data.update(dnkl_dict)
                                                            with open('dnkl.json', 'w') as f:
                                                                json.dump(data, f)
                                            else:
                                                continue


                    break

                elif reply in ("Role", "Username", "Name"):
                    await channel.edit(name=f"Role/NameChange-{name}",category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    await channel.send('What is your minecraft username?')
                    role_reply = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    name = role_reply.content
                    ign = hypixel.get_dispname(name)
                    if ign is None:
                        await channel.send('Please enter a valid ign!')
                        await channel.send("I'll restart the process. If you think I made an error, select 'Other' upon restart")
                    else:
                        guild_name = hypixel.get_guild(ign)
                        guest = discord.utils.get(channel.guild.roles, name="Guest")
                        member = discord.utils.get(channel.guild.roles, name="Member")
                        awaiting_app = discord.utils.get(channel.guild.roles, name="Awaiting Approval")
                        xl_ally = discord.utils.get(channel.guild.roles, name="XL - Ally")
#
#
                        await author.edit(nick=ign)
                        if guild_name == "Miscellaneous":
                            await author.remove_roles(guest, awaiting_app)
                            await author.add_roles(member)
                            embed = discord.Embed(title="Your nick and role was succesfully changed!",
                                                  description="await staff assistance.",
                                                  color=0x8368ff)
                            embed.set_footer(text="Member of Miscellaneous"
                                                  "\n• Guest & Awaiting Approval were removed"
                                                  "\n• Member was given")
                            await channel.send(embed=embed)

                        elif guild_name == "XL":
                            await author.remove_roles(member, awaiting_app)
                            await author.add_roles(guest, xl_ally)
                            embed = discord.Embed(title="Your nick and role was succesfully changed!",
                                                  description="If this wasn't the change you anticipated, "
                                                              "await staff assistance.",
                                                  color=0x8368ff)
                            embed.set_footer(text="Member of XL"
                                                  "\n• Member & Awaiting Approval were removed"
                                                  "\n• Guest & XL - Ally were given")
                            await channel.send(embed=embed)

                        elif guild_name not in ("Miscellaneous","XL"):
                            if str(channel.channel.category.name) == "RTickets":
                                await channel.send("You aren't in Miscellaneous in-game. Kindly await staff assistance!")
                            else:
                                await author.remove_roles(member,awaiting_app)
                                await author.add_roles(guest)
                                embed = discord.Embed(title="Your nick and role was succesfully changed!",
                                                      description="If this wasn't the change you anticipated, "
                                                                  "await staff assistance.",
                                                      color=0x8368ff)
                                embed.set_footer(text=f"Member of {guild_name}"
                                                      f"\n• Member & Awaiting Approval were removed"
                                                      f"\n• Guest was given")
                                await channel.send(embed=embed)

                elif reply in "Report":
                    await channel.edit(name=f"Report-{name}", category=discord.utils.get(channel.guild.categories, name="REPORTS"))
                    await channel.send(
                        "Alright. Please provide adequate details about the user and await staff assistance!")
                    break
                elif reply in ("General", "Problem", "Query", "Complaint", "Suggestion"):
                    await channel.edit(name=f"General-{name}", category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    await channel.send(
                        "Alright. Kindly specify the reason you created this ticket and wait for staff assistance!")
                    break
                elif reply == "Milestone":
                    await channel.edit(name=f"Milestone-{name}", category=discord.utils.get(channel.guild.categories, name="MILESTONES"))
                    await channel.send(
                        "Kindly provide a screenshot followed by a message specifying your milestone and then await staff assistance!")
                    break
                elif reply in ('Staff', 'Staff Application', 'Staff App'):
                    embed = discord.Embed(title="To be eligible to apply for staff,"
                                                " you must meet the following requirements.",
                                          description="• You must be older than 13 years."
                                                      "\n• You must have enough knowledge about the bots in this Discord."
                                                      "\n• You must be active both on Hypixel and in the guild Discord."
                                                      "\n• You must have a good reputation amongst guild members.",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    await channel.send("**Do you meet these requirements? (Yes/No)**")

                    reqs = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    reqs = reqs.content
                    reqs = reqs.capitalize()

                    if reqs in ('Yes', 'Ye', 'Yup', 'Y', 'Yeah', 'Yus'):
                        embed = discord.Embed(title="Does your discord nick match your Minecraft Username?",
                                              description="Kindly reply with a Yes or No",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        nickmatching = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                        nickmatching = nickmatching.content
                        nickmatching = nickmatching.capitalize()
                        if nickmatching in ('Yes', 'Ye', 'Yup', 'Y', 'Yeah', 'Yus'):
                            if name is None:
                                x = author.name
                                name = x
                            request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
                            uuid = request.json()['id']
                            await channel.edit(name=f"Staff-Application-{name}", category=discord.utils.get(channel.guild.categories, name="OTHER"))
                            '''AGE'''
                            embed = discord.Embed(title="What is your age?",
                                                  description="Kindly reply with a number",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            age = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            age = age.content

                            '''VETERENCY'''
                            embed = discord.Embed(title="For how long have you been in Miscellaneous?",
                                                  description="You can check this through \"/g menu\" ingame",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            veterency = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            veterency = veterency.content

                            '''PAST INFRACTIONS'''
                            embed = discord.Embed(title="Have you had any past infractions on Hypixel?",
                                                  description="Kindly reply with a Yes or No",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            infractions = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            infractions = infractions.content
                            infractions = infractions.capitalize()

                            embed = discord.Embed(title="Kindly make sure that your answers are as detailed as possible."
                                                        "\nGiving short answers will hinder your chances at getting staff.",
                                                  description="When answering, answer in the form of one message. One question, one message!",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            time.sleep(3)

                            '''------------------------------------------------------Questions------------------------------------------------'''

                            '''WHY STAFF'''
                            embed = discord.Embed(title="Why have you decided to apply for staff?",
                                                  description="Please make sure that you respond in one message",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            whystaff = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            whystaff = whystaff.content

                            '''WHY MISC'''
                            embed = discord.Embed(title="What brought you to Miscellaneous, and what has kept you here?",
                                                  description="Please make sure that you respond in one message",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            whymisc = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            whymisc = whymisc.content

                            '''Suggest'''
                            embed = discord.Embed(title="What is something that you could suggest that could improve the guild?",
                                                  description="Please make sure that you respond in one message",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            suggestion = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            suggestion = suggestion.content

                            '''SCENARIO 1'''
                            embed = discord.Embed(title="You have just started as a trial officer and an officer starts arguing with another member. "
                                                        "This argument starts to get serious quite quickly. What do you do? ",
                                                  description="Make your answer as detailed as possible!",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            scen1 = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            scen1 = scen1.content

                            '''SCENARIO 2'''
                            embed = discord.Embed(title="Suppose it's your first week of being a trial officer and you guild-mute a well-known player. "
                                                        "Your guildmates start spamming you calling you a bad officer and telling you to unmute them. "
                                                        "What would you do?",
                                                  description="Make your answer as detailed as possible!",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            scen2 = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            scen2 = scen2.content

                            '''SCENARIO 3'''
                            embed = discord.Embed(title="Upon joining a game and you discover that a guild member is in your game and is hacking. "
                                                        "What do you do?",
                                                  description="Please make sure that you respond in one message",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            scen3 = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            scen3 = scen3.content

                            '''STAFF'''
                            embed = discord.Embed(title="Have you been staff in any other guild or on any server? "
                                                        "If yes, which one?",
                                                  description="Please make sure that you respond in one message",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            staff = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            staff = staff.content

                            '''TIME'''
                            embed = discord.Embed(title="How much time do you have to contribute to the role? (Per day)",
                                                  description="Please make sure that you respond in one message",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            time_ = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            time_ = time_.content

                            '''GENERAL QUESTION'''
                            embed = discord.Embed(title="Tell us about a time you made a mistake within the last year. "
                                                        "How did you deal with it? What did you learn?",
                                                  escription="Make your answer as detailed as possible!",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            question = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            question = question.content

                            '''ANYTHING ELSE'''
                            embed = discord.Embed(title="Anything else you would like us to know?",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            random = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            random = random.content

                            await channel.send("Great! You're done with the application!"
                                               "\nI'm working on compiling the application and I'll send it once I'm done compiling!")

                            embed = discord.Embed(title=f"{name}'s Staff Application", color=0x4b89e4)
                            embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                            embed.add_field(name="1) What is your age?", value=age, inline=False)
                            embed.add_field(name="2) How long have you been in the guild for?", value=veterency, inline=False)
                            embed.add_field(name="3) Have you had any past infractions on Hypixel?", value=infractions, inline=False)
                            embed.add_field(name="4) Why have you decided to apply for staff?", value=whystaff, inline=False)
                            embed.add_field(name="5) What brought you to Miscellaneous, and what has kept you here?", value=whymisc, inline=False)
                            embed.add_field(name="6) What is something you could suggest that would improve the guild?", value=suggestion, inline=False)
                            embed.add_field(name="7) You have just started as a trial officer and an officer starts arguing with another member. This argument starts to get serious quite quickly. What do you do?", value=scen1, inline=False)
                            embed.add_field(name="8) Suppose it's your first week of being a trial officer and you guild-mute a well-known player. Your guildmates start spamming you calling you a bad officer and telling you to unmute them. What would you do?", value=scen2, inline=False)
                            embed.add_field(name="9) Upon joining a game and you discover that a guild member is in your game and is hacking. What do you do?", value=scen3, inline=False)
                            embed.add_field(name="10) Have you been staff in any other guild or on any server? If yes, which one?", value=staff, inline=False)
                            embed.add_field(name="11) How much time do you have to contribute to the role? (Per day)", value=time_, inline=False)
                            embed.add_field(name="12) Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?", value=question, inline=False)
                            embed.add_field(name="13) Anything else you would us to know?", value=random, inline=False)
                            await channel.send(embed=embed)
                            await channel.send("If you made any error, make a new ticket, rectify your mistake and copy paste your answer.")
                            break

                        else:
                            await channel.send('What is your minecraft username?')
                            role_reply = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                            name = role_reply.content
                            ign = hypixel.get_dispname(name)
                            if ign is None:
                                await channel.send('Please enter a valid ign!')
                                await channel.send(
                                    "I'll restart the process. "
                                    "If you think I made an error, select 'Other' upon restart")
                            else:
                                guild_name = hypixel.get_guild(name)

                                guest = discord.utils.get(channel.guild.roles, name="Guest")
                                member = discord.utils.get(channel.guild.roles, name="Member")
                                awaiting_app = discord.utils.get(channel.guild.roles, name="Awaiting Approval")

                                await author.edit(nick=ign)
                                if guild_name == "Miscellaneous":
                                    await author.remove_roles(awaiting_app)
                                    await author.remove_roles(guest)
                                    await author.add_roles(member)
                                    embed = discord.Embed(title="Your nick and role was succesfully changed!",
                                                          description="Now let's proceed to your application!",
                                                          color=0x8368ff)
                                    await channel.send(embed=embed)

                                else:
                                    await author.remove_roles(member)
                                    await author.add_roles(guest)
                                    embed = discord.Embed(title="Your nick and role was succesfully changed!",
                                                          description="Now let's proceed to your application!",
                                                          color=0x8368ff)
                                    await channel.send(embed=embed)

                                request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
                                uuid = request.json()['id']

                                await channel.edit(name=f"Staff-Application-{name}", category=discord.utils.get(channel.guild.categories, name="OTHER"))
                                '''AGE'''
                                embed = discord.Embed(title="What is your age?",
                                                      description="Kindly reply with a number",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                age = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                age = age.content

                                '''VETERENCY'''
                                embed = discord.Embed(title="For how long have you been in Miscellaneous?",
                                                      description="You can check this through \"/g menu\" ingame",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                veterency = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                veterency = veterency.content

                                '''PAST INFRACTIONS'''
                                embed = discord.Embed(title="Have you had any past infractions on Hypixel?",
                                                      description="Kindly reply with a Yes or No",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                infractions = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                infractions = infractions.content
                                infractions = infractions.capitalize()

                                embed = discord.Embed(title="Kindly make sure that your answers are as detailed as possible."
                                                            "\nGiving short answers will hinder your chances at getting staff.",
                                                      description="When answering, answer in the form of one message. "
                                                                  "One question, one message!",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                time.sleep(3)
    #------------------------------------------------------Questions------------------------------------------------

                                #WHY STAFF
                                embed = discord.Embed(title="Why have you decided to apply for staff?",
                                                      description="Please make sure that you respond in one message",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                whystaff = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                whystaff = whystaff.content


                                #WHY MISC
                                embed = discord.Embed(title="What brought you to Miscellaneous, "
                                                            "and what has kept you here?",
                                                      description="Please make sure that you respond in one message",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                whymisc = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                whymisc = whymisc.content


                                #Suggest
                                embed = discord.Embed(title="What is something that you could suggest that could improve the guild?",
                                                      description="Please make sure that you respond in one message",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                suggestion = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                suggestion = suggestion.content


                                #SCENARIO 1
                                embed = discord.Embed(title="You have just started as a trial officer and an officer starts arguing with another member."
                                                            " This argument starts to get serious quite quickly. What do you do? ",
                                                      description="Make your answer as detailed as possible!",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                scen1 = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                scen1 = scen1.content


                                #SCENARIO 2
                                embed = discord.Embed(title="Suppose it's your first week of being a trial officer and you guild-mute a well-known player."
                                                            " Your guildmates start spamming you calling you a bad officer and telling you to unmute them."
                                                            " What would you do?",
                                                      description="Make your answer as detailed as possible!",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                scen2 = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                scen2 = scen2.content


                                #SCENARIO 3
                                embed = discord.Embed(title="Upon joining a game and you discover that a guild member is in your game and is hacking."
                                                            " What do you do?",
                                                      description="Please make sure that you respond in one message",
                                                      color=0x4b89e4)
                                await channel.send(embed=embed)
                                scen3 = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                scen3 = scen3.content


                                #STAFF
                                embed = discord.Embed(title="Have you been staff in any other guild or on any server? If yes, which one?", description="Please make sure that you respond in one message", color=0x4b89e4)
                                await channel.send(embed=embed)
                                staff = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                staff = staff.content


                                #TIME
                                embed = discord.Embed(title="How much time do you have to contribute to the role? (Per day)", description="Please make sure that you respond in one message", color=0x4b89e4)
                                await channel.send(embed=embed)
                                time_ = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                time_ = time_.content


                                #GENERAL QUESTION
                                embed = discord.Embed(title="Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?", description="Make your answer as detailed as possible!", color=0x4b89e4)
                                await channel.send(embed=embed)
                                question = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                question = question.content

                                #ANYTHING ELSE
                                embed = discord.Embed(title="Anything else you would like us to know?", color=0x4b89e4)
                                await channel.send(embed=embed)
                                random = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                                random = random.content


                                msg = await channel.send("Great! You're done with the application!\n I'm working on compiling the application and I'll send it once I'm done compiling!")
                                try:
                                    embed = discord.Embed(title=f"{name}'s Staff Application", color=0x4b89e4)
                                    embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                    embed.add_field(name="1) What is your age?", value=age, inline=False)
                                    embed.add_field(name="2) How long have you been in the guild for?", value=veterency, inline=False)
                                    embed.add_field(name="3) Have you had any past infractions on Hypixel?", value=infractions, inline=False)
                                    embed.add_field(name="4) Why have you decided to apply for staff?", value=whystaff, inline=False)
                                    embed.add_field(name="5) What brought you to Miscellaneous, and what has kept you here?", value=whymisc, inline=False)
                                    embed.add_field(name="6) What is something you could suggest that would improve the guild?", value=suggestion, inline=False)
                                    embed.add_field(name="7) You have just started as a trial officer and an officer starts arguing with another member. This argument starts to get serious quite quickly. What do you do?", value=scen1, inline=False)
                                    embed.add_field(name="8) Suppose it's your first week of being a trial officer and you guild-mute a well-known player. Your guildmates start spamming you calling you a bad officer and telling you to unmute them. What would you do?", value=scen2, inline=False)
                                    embed.add_field(name="9) Upon joining a game and you discover that a guild member is in your game and is hacking. What do you do?", value=scen3, inline=False)
                                    embed.add_field(name="10) Have you been staff in any other guild or on any server? If yes, which one?", value=staff, inline=False)
                                    embed.add_field(name="11) How much time do you have to contribute to the role? (Per day)", value=time_, inline=False)
                                    embed.add_field(name="12) Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?", value=question, inline=False)
                                    embed.add_field(name="13) Anything else you would us to know?", value=random, inline=False)
                                    await channel.send(embed=embed)
                                    await channel.send("If you made any error, make a new ticket, rectify your mistake and copy paste your answer.")
                                except Exception as e:
                                    if e == "400 Bad Request (error code: 50035): Invalid Form Body\nIn embed.fields.9.value: Must be 1024 or fewer in length.":
                                        await msg.edit(content='Failed to compile the data since your message is too long!\n No worries though, the staff team will still go through your application!')


                                break

                    else:
                        await channel.send("Since you don't meet the requirements, there's no point proceeding with the application. Kindly reapply once you meet all the requirements.")
                        break
                elif reply == "Gvg":
                    await channel.edit(name=f"GvG-Application-{name}", category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    embed = discord.Embed(title="To be eligible to apply for the GvG Team, you must meet any one of the following game-specific requirements.", color=0x00FFFF)
                    embed.add_field(name="Bedwars", value="500 Wins\n1.6 Final Kill-Death Ratio", inline=False)
                    embed.add_field(name="Skywars", value="1000 Wins\n1.2 Kill-Death Ratio", inline=False)
                    embed.add_field(name="Duels", value="2000 Wins\n1.5 Kill-Death Ratio", inline=False)
                    embed.add_field(name="Polyvalent (All gamemodes)", value="Must fulfill all requirements", inline=False)
                    await channel.send(embed=embed)

                    req = hypixel.get_data(name)
                    if req["player"] is None:
                        embed = discord.Embed(title='Unknown IGN', description='Kindly create a new ticket to sync your name and then create another ticket for the GvG Application!', color=0xff0000)
                        await channel.send(embed=embed)
                    else:
                        req = hypixel.get_data(name)
                        uuid = req['player']['uuid']

                        x=0
                        y=0
                        z=0

                        #Bedwars
                        bw_wins = int(req['player']['stats']['Bedwars']['wins_bedwars'])
                        bw_final_kills = int(req['player']['stats']['Bedwars']['final_kills_bedwars'])
                        bw_final_deaths = int(req['player']['stats']['Bedwars']['final_deaths_bedwars'])
                        bw_fkdr = bw_final_kills/bw_final_deaths
                        bw_fkdr = round(bw_fkdr, 2)

                        if bw_wins > 500:
                            x = x + 1
                        if bw_fkdr > 1.6:
                            x = x + 1



                        #Skywars
                        sw_wins_overall = int(req['player']['stats']['SkyWars']['wins'])
                        sw_wins_solo = int(req['player']['stats']['SkyWars']['wins_solo'])
                        sw_wins_doubles = int(req['player']['stats']['SkyWars']['wins_team'])
                        sw_kills = int(req['player']['stats']['SkyWars']['kills'])
                        sw_deaths = int(req['player']['stats']['SkyWars']['deaths'])
                        sw_kdr = sw_kills/sw_deaths
                        sw_kdr = round(sw_kdr, 2)
                        if sw_wins_overall > 1000:
                            y = y + 1
                        if sw_kdr > 1.2:
                            y = y + 1



                        #Duel
                        duels_wins = int(req['player']['stats']['Duels']['wins'])
                        duels_losses = int(req['player']['stats']['Duels']['losses'])
                        duels_kills = int(req['player']['stats']['Duels']['kills'])
                        duels_wlr = duels_wins/duels_losses
                        duels_wlr = round(duels_wlr, 2)

                        if duels_wins > 2000:
                            z = z + 1
                        if duels_wlr > 1.5:
                            z = z + 1


                        if x >= 2 and y >= 2 and z >= 2:
                            embed1 = discord.Embed(title="You're eligible for the Polyvalent GvG Team!", description="Kindly await staff assistance for further information!", color=0xff00f6)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bw_wins}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bw_fkdr}`')
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{sw_wins_overall}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{sw_wins_solo}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{sw_wins_doubles}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{sw_kdr}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_wins}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_wlr}`')
                            await channel.send(embed=embed1)
                            break

                        elif x == 1 and y == 1 and z == 1:
                            embed1 = discord.Embed(title="You're eligible for any two of the teams!\n You will be assigned to any two teams on the basis of your stats!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0xff00f6)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bw_wins}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bw_fkdr}`')
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{sw_wins_overall}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{sw_wins_solo}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{sw_wins_doubles}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{sw_kdr}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_wins}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_wlr}`')
                            await channel.send(embed=embed1)
                            break

                        elif x >= 1 and y >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Bedwars and Skywars GvG Teams!", description="Kindly await staff assistance for further information!", color=0xff00f6)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bw_wins}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bw_fkdr}`')
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{sw_wins_overall}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{sw_wins_solo}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{sw_wins_doubles}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{sw_kdr}`')
                            embed1.set_footer(text=f"Duels wins - {duels_wins}\nDuels WLR - {duels_wlr}")
                            await channel.send(embed=embed1)
                            break
                                
                        elif x >= 1 and z >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Bedwars and Duels GvG Teams!", description="Kindly await staff assistance for further information!", color=0xff00f6)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bw_wins}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bw_fkdr}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_wins}`')
                            embed1.add_field(name="Duels WLR;", value=f'`{duels_wlr}`')
                            embed1.set_footer(text=f"Skywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}")
                            await channel.send(embed=embed1)
                            break

                        elif y >= 1 and z >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Skywars and Duels GvG Teams!", description="Kindly await staff assistance for further information!", color=0xff00f6)
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{sw_wins_overall}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{sw_wins_solo}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{sw_wins_doubles}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{sw_kdr}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_wins}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_wlr}`')
                            embed1.set_footer(text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}")
                            await channel.send(embed=embed1)
                            break
                        elif x >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Bedwars GvG Team!", description="Kindly await staff assistance for further information!", color=0xff00f6)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bw_wins}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bw_fkdr}`')
                            embed1.set_footer(text=f"Skywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}\nDuels wins - {duels_wins}\nDuels Kills - {duels_kills}\nDuels WLR - {duels_wlr}")
                            await channel.send(embed=embed1)
                            break
                        elif y >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Skywars GvG Team!", description="Kindly await staff assistance for further information!", color=0xff00f6)
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{sw_wins_overall}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{sw_wins_solo}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{sw_wins_doubles}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{sw_kdr}`')
                            embed1.set_footer(text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}\nDuels wins - {duels_wins}\nDuels WLR - {duels_wlr}")
                            await channel.send(embed=embed1)
                            break
                        elif z >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Duels GvG Team!", description="Kindly await staff assistance for further information!", color=0xff00f6)
                            embed1.add_field(name="Duels Wins", value=f'`{duels_wins}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_wlr}`')
                            embed1.set_footer(text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}\nSkywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}")
                            await channel.send(embed=embed1)
                            break
                        else:
                            embed1 = discord.Embed(title="You're ineligible to apply GvG Team because you don't meet the requirements!", description="Kindly await staff assistance for further information!", color=0xcd5c5c)
                            embed1.set_footer(text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}\nSkywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}\nDuels wins - {duels_wins}\nDuels WLR - {duels_wlr}")
                            await channel.send(embed=embed1)
                            break

                elif reply == "Demotion":

                    admin = discord.utils.get(channel.guild.roles, name="Admin")
                    if admin in author.roles:
                        await channel.purge(limit=10)
                        embed = discord.Embed(title="Who would you like to demote?", description="Kindly mention them", color=0x00FFFF)
                        await channel.send(embed=embed)
                        user = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                        user = user.mentions[0]

                        username = user.nick
                        if username is None:
                            username = user.name

                        await channel.edit(name=f"Demotion-{username}")

                        embed = discord.Embed(title=f"What's the reason behind {username}'s demotion?", color=0x00FFFF)
                        await channel.send(embed=embed)
                        reason = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                        reason = reason.content

                        await channel.set_permissions(user, send_messages=True, read_messages=True,
                                                      add_reactions=True, embed_links=True,
                                                      attach_files=True, read_message_history=True,
                                                      external_emojis=True)
                        await channel.purge(limit=10)
                        embed = discord.Embed(title=f"{username} you are being demoted from the Miscellaneous staff team!", description=f"This is due to {reason}", color=0x8368ff)
                        await channel.send(embed=embed)
                        await channel.send(user.mention)
                        break
                    else:
                        embed = discord.Embed(title="My massive computer brain thinks you made a mistake.", color=0xff0000)
                        embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
                        embed.add_field(name="If this is false", value="Type `No`", inline=False)
                        await channel.send(embed=embed)
                        mistake = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                        mistake = mistake.content
                        mistake = mistake.capitalize()
                        if mistake == "Yes":
                            await channel.send("Great! Let's start over!")
                        else:
                            await channel.send(
                                "Hmm, seems like I'm dumb.\nKindly specify your reason behind creating this ticket and await staff assistance!")
                            break


                elif reply == "Other":
                        await channel.edit(name=f"Unknown-{name}", category=discord.utils.get(channel.guild.categories, name="OTHER"))
                        await channel.send(
                            "Okay. Kindly specify your reason behind creating this ticket and wait for staff to help you!")
                        break
                else:
                    embed = discord.Embed(title="My massive computer brain thinks you made a mistake.", color=0xff0000)
                    embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
                    embed.add_field(name="If this is false", value="Type `No`", inline=False)
                    await channel.send(embed=embed)
                    mistake = await client.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    mistake = mistake.content
                    mistake = mistake.capitalize()
                    if mistake == "Yes":
                        embed = discord.Embed(title="Great! Let's start over!",
                                              color=0x8368ff)
                        await channel.send(embed=embed)
                    else:
                        await channel.send(
                            "Hmm, seems like I'm dumb.\nKindly specify your reason behind creating this ticket and await staff assistance!")
                        break
                
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="You may proceed by elaborating on why you created this ticket so that the staff team can help you!",
                                  color=0xff0000)
            await channel.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {channel}\n{e}\n<@!326399363943497728>")


'----------------------------------------------------------------------------------------------------------------GENERAL----------------------------------------------------------------------------------------------------'


# help
@client.command()
async def help(ctx, *, a=None):

    if a is None:
        embed = discord.Embed(title="", description="",
                              url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz",
                              color=0x8368ff)
        embed.set_thumbnail(
            url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz")
        embed.add_field(name="help", value="Prints this help message!", inline=False)
        embed.add_field(name="help fun", value="Prints all the commands related to fun and games!", inline=False)
        embed.add_field(name="help moderation", value="Prints all the commands related to moderation!", inline=False)
        embed.add_field(name="help hypixel", value="Prints all the commands related to Hypixel!", inline=False)
        embed.add_field(name="help all",
                        value="Returns a list of all the commands and their functions",
                        inline=False)
        embed.set_author(name="General Help")
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)
    if a == 'fun':
        embed = discord.Embed(title="", description="",
                              url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz",
                              color=0x8368ff)
        embed.set_thumbnail(
            url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz")
        embed.add_field(name="8ball", value="Play with the magic 8ball", inline=False)
        embed.add_field(name="ping", value="Gives the bot's ping", inline=False)
        embed.add_field(name="pizza", value="Gives you a pizza", inline=False)
        embed.set_author(name="Help - Fun")
        embed.set_footer(text="Miscellaneous Bot | Coded by Rowdies")
        await ctx.send(embed=embed)
    if a == 'moderation':
        embed = discord.Embed(title="", description="",
                              url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz",
                              color=0x8368ff)
        embed.set_thumbnail(
            url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz")
        embed.add_field(name="clear `amount`", value='Clears the chat based on the given amount!', inline=False)
        embed.add_field(name="mute `user`", value='Mutes the mentioned user indefinately!', inline=False)
        embed.add_field(name="unmute `user`", value='Mutes the mentioned user', inline=False)
        embed.add_field(name="kick `Discord @` `Reason`", value='Kicks the mentioned user!', inline=False)
        embed.add_field(name="ban `Discord @` `Reason`", value='Bans the mentioned user!', inline=False)
        embed.add_field(name="unban `Name#Discrimitator`", value='Unbans the user!', inline=False)
        embed.set_author(name="Help - Moderation")
        embed.set_footer(text="Miscellaneous Bot | Coded by Rowdies")
        await ctx.send(embed=embed)
    if a == 'hypixel':
        embed = discord.Embed(title="", description="",
                              url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz",
                              color=0x8368ff)
        embed.set_thumbnail(
            url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz")
        embed.add_field(name="sync `IGN`",
                        value="Used to update your discord nick upon changing your minecraft name/leaving Miscellaneous!",
                        inline=False)
        embed.add_field(name="info `IGN`", value='Gives the hypixel stats of the requested player', inline=False)
        embed.add_field(name="dnkl `IGN` `Discord @|Use a random character` `Start Date` `End Date` `Reason`",
                        value="Adds the user to the do-not-kick-list!", inline=False)
        embed.add_field(name="bl `IGN` `End Date` `Reason`", value="Adds the user to the guild blacklist", inline=False)
        embed.add_field(name="ginfo `Username`", value="Gives basic information about the requested guild.",
                        inline=False)
        embed.add_field(name="gexp `Guild Name`", value="Lists the guild experience of the requested guild!", inline=False)
        embed.add_field(name="gmember `IGN`",
                        value="Gives the guild experience earned by the user over the course of a week.", inline=False)
        embed.add_field(name="gtop", value="Gives the weekly guild experience leaderboard!", inline=False)
        embed.add_field(name="dailylb `Number of days ago`",
                        value="Prints the daily guild leaderboard. The value defaults to the day prior.", inline=False)
        embed.add_field(name="gactive", value="Lists all the users in the guild who are eligible for active rank.",
                        inline=False)
        embed.add_field(name="ginactive",
                        value="Lists all the users in the guild who don't meet the guild requirements.", inline=False)
        embed.add_field(name="grank `rank`", value="Lists the guild experience of users with the specified rank.",
                        inline=False)
        embed.add_field(name="dnklcheck `IGN`",
                        value="A command to check whether or not you can apply for the do-not-kick-list.", inline=False)
        embed.set_author(name="Help - Hypixel")
        embed.set_footer(text="Miscellaneous Bot | Coded by Rowdies")
        await ctx.send(embed=embed)
    if a == 'staff':
        embed = discord.Embed(title="", description="", color=0x8368ff)
        embed.set_author(name="Help - Staff")
        embed.set_thumbnail(
            url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz")

        embed.add_field(name="requirements",
                        value="Lists the requirements",
                        inline=False)

        embed.add_field(name="resident",
                        value="Lists the methods to get the resident rank",
                        inline=False)

        embed.add_field(name="tickets",
                        value="Explains the entire ticket system",
                        inline=False)

        embed.add_field(name="staff",
                        value="Prints a list of users who need to be promoted, demoted, warned and kicked!",
                        inline=False)

        embed.add_field(name="dailylb `Number of days ago`",
                        value="Prints the daily guild leaderboard. The value defaults to the day prior.",
                        inline=False)

        embed.add_field(name="delete",
                        value="Deletes the ticket channel the command is used in.",
                        inline=False)

        embed.add_field(name="gtop",
                        value="Prints the weekly guild experience leaderboard!",
                        inline=False)

        embed.add_field(name="bl `IGN` `End Date` `Reason`",
                        value="Blacklists the user",
                        inline=False)

        embed.add_field(name="dnkladd `IGN` `Discord @|Use a random character` `Start Date` `End Date` `Reason`",
                        value="Adds a user to the do not kick list!",
                        inline=False)

        embed.add_field(name="dnklrmv `IGN`",
                        value="Removes a user from the do not kick list!",
                        inline=False)

        embed.add_field(name="rolecheck",
                        value="Checks the roles of all the users and changes them on the basis of their guild",
                        inline=False)

        embed.add_field(name="accept `Discord @`",
                        value="Used to accept staff applications. This command must be typed in the application channel. It doesn't work anywhere else.",
                        inline=False)

        embed.add_field(name="deny `Discord @` `Discord Channel #`",
                        value="Used to deny staff applications. This command can be used in any channel, provided, the syntax is met.",
                        inline=False)

        embed.add_field(name="forcesync `Discord @` `Player's IGN`", value="Used to forcefully sync a player's IGN", inline=False)
        await ctx.send(embed=embed)

    if a == 'all':
        # Fun
        embed = discord.Embed(title="", description="",
                              url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz",
                              color=0x8368ff)
        embed.set_thumbnail(
            url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz")

        embed.add_field(name="8ball",
                        value="Play with the magic 8ball",
                        inline=False)

        embed.add_field(name="ping",
                        value="Gives the bot's ping",
                        inline=False)

        embed.add_field(name="pizza",
                        value="Gives you a pizza",
                        inline=False)

        embed.set_author(name="Help - Fun")

        # Moderation
        embed1 = discord.Embed(title="", description="",
                               url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz",
                               color=0x8368ff)

        embed1.add_field(name="clear `amount`",
                         value='Clears the chat based on the given amount!',
                         inline=False)

        embed1.add_field(name="mute `user`",
                         value='Mutes the mentioned user indefinately!',
                         inline=False)

        embed1.add_field(name="unmute `user`",
                         value='Mutes the mentioned user',
                         inline=False)

        embed1.add_field(name="kick `Discord @` `Reason`",
                         value='Kicks the mentioned user!',
                         inline=False)

        embed1.add_field(name="ban `Discord @` `Reason`",
                         value='Bans the mentioned user!',
                         inline=False)

        embed1.add_field(name="unban `Name#Discrimitator`",
                         value='Unbans the user!',
                         inline=False)

        embed1.set_author(name="Help - Moderation")

# Hypixel
        embed2 = discord.Embed(title="", description="",
                               url="https://lh3.googleusercontent.com/6PxnnRn8AIQ9Mu5UXmKtL-j8Eh3ZRqZaHKvCKGShvUZRHOWwiXCBzWa-NuMNEpC9OdrzsTHP7isCIOvkgns_tBha_yQ_r_V2I4hRqWXPnjfkUOfHER_vHCCjWW56qkbhO5vM5rqz",
                               color=0x8368ff)

        embed2.add_field(name="sync `IGN`",
                         value="Used to update your discord nick upon changing your minecraft name/leaving Miscellaneous!",
                         inline=False)

        embed2.add_field(name="info `IGN`",
                         value='Gives the hypixel stats of the requested player',
                         inline=False)

        embed2.add_field(name="dnkl `IGN` `Discord @|Use a random character` `Start Date` `End Date` `Reason`",
                         value="Adds the user to the do-not-kick-list!",
                         inline=False)

        embed2.add_field(name="bl `IGN` `End Date` `Reason`",
                         value="Adds the user to the guild blacklist",
                         inline=False)

        embed2.add_field(name="ginfo `Username`",
                         value="Gives basic information about the requested guild.",
                         inline=False)

        embed2.add_field(name="gexp `Guild Name`",
                         value="Lists the guild experience of the requested guild!",
                         inline=False)

        embed2.add_field(name="gmember `IGN`",
                         value="Gives the guild experience earned by the user over the course of a week.",
                         inline=False)
        embed2.add_field(name="gtop",
                         value="Gives the weekly guild experience leaderboard!",
                         inline=False)
        embed.add_field(name="dailylb `Number of days ago`",
                        value="Prints the daily guild leaderboard. The value defaults to the day prior.",
                        inline=False)

        embed2.add_field(name="gactive",
                         value="Lists all the users in the guild who are eligible for active rank.",
                         inline=False)

        embed2.add_field(name="ginactive",
                         value="Lists all the users in the guild who don't meet the guild requirements.",
                         inline=False)

        embed2.add_field(name="grank `rank`",
                         value="Lists the guild experience of users with the specified rank.",
                         inline=False)

        embed2.add_field(name="dnklcheck `IGN`",
                         value="A command to check whether or not you can apply for the do-not-kick-list.",
                         inline=False)

        embed2.set_author(name="Help - Hypixel")

        await ctx.send(embed=embed)
        await ctx.send(embed=embed1)
        await ctx.send(embed=embed2)


# Ping
@client.command()
async def ping(ctx):
    embed = discord.Embed(title='Pong',
                          description=f"{round(client.latency * 1000)}ms",
                          color=0x8368ff)
    await ctx.send(embed=embed)


# Pizza
@client.command()
async def pizza(ctx):
    links = ['https://bit.ly/3ibK6PQ', 'https://bit.ly/2EZWZ1p', 'https://bit.ly/339ul5N', 'https://bit.ly/328OOIx',
             'https://bit.ly/3ibMqGy', 'https://bit.ly/2F8hd96', 'https://bit.ly/2R5XusZ', 'https://bit.ly/35fRqX7',
             'https://bit.ly/2F9Ec3B', 'https://bit.ly/3h9T8vI', 'https://bzfd.it/2GzzLzm', 'https://bit.ly/35fyKa7',
             'https://bit.ly/3lVF24F', 'https://bit.ly/2R2Ccg1', 'https://bit.ly/3haFhVZ', 'https://bit.ly/2DDaWkW',
             'https://bit.ly/2R893Qx']
    image = random.choice(links)
    embed = discord.Embed(title="Here's the pizza you requested:", color=0xD2691e)
    embed.set_image(url=image)
    await ctx.send(embed=embed)


# 8ball
@client.command(aliases=['8ball', 'eightball'])
async def _8ball(ctx, *, question):
    author = ctx.author
    user_name = author.nick
    if user_name is None:
        user_name = ctx.author.name
    responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.",
                 "Concentrate and ask again.", "Don’t count on it.", "It is certain.", "It is decidedly so.",
                 "Most likely", "My reply is no.", "My sources say no.", "Outlook not so good.", "Outlook good.",
                 "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Yes.",
                 "Yes – definitely.", "You may rely on it."]
    embed = discord.Embed(title=f'{random.choice(responses)}', color=0x0ffff)
    embed.set_author(name=f"{question}")
    embed.set_footer(text=f'{user_name}')
    await ctx.send(embed=embed)
@_8ball.error
async def _8ball_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="You're supposed to ask me a question ._.", description="8ball `question`",
                              color=0xff0000)
        await ctx.send(embed=embed)


# clear
@client.command(aliases=["purge", "prune"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please specify the number of messages to be deleted',
                              description='clear `amount of messages`', color=0xff0000)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to clear chat", color=0xff0000)
        await ctx.send(embed=embed)


# Mute
@client.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(role)
    embed = discord.Embed(title="User Muted!",
                          description="**{0}** was muted by **{1}**!".format(member, ctx.message.author),
                          color=0xff00f6)
    await ctx.send(embed=embed)
@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to mute a user", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


# Unmute
@client.command()
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(role)
    embed = discord.Embed(title="User unmuted!",
                          description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author),
                          color=0xff00f6)
    await ctx.send(embed=embed)
@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to unmute a user", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


# kick
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member} was kicked!")
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please specify the player to be banned! The syntax is as follows',
                              description="kick `Discord @` `reason`", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to kick a user", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


# ban
@client.command()
@commands.has_permissions(ban_members=True, kick_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member} was banned!")
    except Exception as e:
        error_channel = client.get_channel(523743721443950612)
        print(e)
        await error_channel.send(f"Error in {ctx.channel.name} while trying to use `ban`\n{e}\n<@!326399363943497728>")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please specify the player to be banned! The syntax is as follows',
                              description="ban `Discord @` `reason`", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to ban a user", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)
# unban
@client.command()
@commands.has_permissions(ban_members=True, kick_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discrimitator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.member_discrimitator) == (member_name, member_discrimitator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned')
            return
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please specify the player to be banned! The syntax is as follows',
                              description="unban `Discord @`", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to unban a user", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command(aliases=['del'])
async def delete(ctx):
    try:
        logs = client.get_channel(714821811832881222)
        Staff = discord.utils.get(ctx.guild.roles, name="Staff")
        if Staff in ctx.author.roles:
            if ctx.channel.category.name in ('RTickets',  '🎫 Ticket Section', 'OTHER', 'REPORTS', 'MILESTONES', 'DNKL'):
                name = ctx.channel.name
                embed = discord.Embed(title='This ticket will be deleted in 5 seconds!', description='', color=0xff0000)
                msg = await ctx.send(embed=embed)
                time.sleep(5)
                await discord.TextChannel.delete(ctx.channel)

                author = ctx.author
                name = author.nick
                if name is None:
                    x = author.name
                    name = x
                embed = discord.Embed(title=f'{ctx.channel.name} was deleted by {name}',
                                      description="", color=0x8368ff)
                await logs.send(embed=embed)
    except Exception as e:
        error_channel = client.get_channel(523743721443950612)
        print(e)
        await error_channel.send(f"Error in {ctx.channel.name}\n{e}\n<@!326399363943497728>")


@client.command()
async def accept(ctx,  member: discord.Member):
    try:
        if ctx.channel.category.name in ('RTickets', '🎫 Ticket Section', 'OTHER', 'REPORTS', 'MILESTONES', 'DNKL'):
            admin = discord.utils.get(ctx.guild.roles, name="Admin")
            if admin in ctx.author.roles:
                embed = discord.Embed(title=f"Congratulations {member.name}, your staff application has been accepted!", description="Please view the following as they'll help you become a better staff member!", color=0x8368ff)
                embed.set_footer(text="https://bit.ly/MiscStaffGuide\n"
                                      "#staff-faq")
                await ctx.send(embed=embed)
    except Exception as e:
        error_channel = client.get_channel(523743721443950612)
        print(e)
        await error_channel.send(f"Error in {ctx.channel.name} while running `deny`\n{e}\n<@!326399363943497728>")
@accept.error
async def accept_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please specify the player to be accepted! The syntax is as follows',
                              description="accept `Discord @`", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command()
async def deny(ctx, member: discord.Member, channel: discord.TextChannel):
    try:
        officer = discord.utils.get(ctx.guild.roles, name="Officer")
        admin = discord.utils.get(ctx.guild.roles, name="Admin")
        if officer or admin in ctx.author.roles:
            name = member.nick
            if name is None:
                x = member.name
                name = x

            embed = discord.Embed(title=f"{name}, your application has been denied!",
                                  description="The reasons are listed below",
                                  color=0xf04747)

            embed.set_footer(text="You may reapply in 2 weeks. \nFollowing is the transcript so that you can refer to it while reapplying.")

            question_number = {
                1: 'What is your age?',
                2: 'How long have you been in the guild for?',
                3: 'Have you had any past infractions on Hypixel?',
                4: 'Why have you decided to apply for staff?',
                5: 'What has brought you to Miscellaneous, and what has kept you here?',
                6: 'What is something you could suggest that would improve the guild?',
                7: 'You have just started as a trial officer and an officer starts arguing with another member. This argument starts to get serious quite quickly. What do you do?',
                8: 'Suppose it\'s your first week of being a trial officer and you guild-mute a well-known player. Your guildmates start spamming you calling you a bad officer and telling you to unmute them. What would you do?',
                9: 'Upon joining a game and you discover that a guild member is in your game and is hacking. What do you do?',
                10: 'Have you been staff in any other guild or on any server? If yes, which one?',
                11: 'How much time do you have to contribute to the role? (Per day)',
                12: 'Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?',
                13: 'Anything else you would us to know?',
                14: 'General Critiquing'
            }

            all_questions = ''
            for x in range(1,15):
                question = question_number.get(int(x), 'None')
                all_questions = all_questions + f"{x})" + question + "\n\n"

            embed1 = discord.Embed(title="Questions", description=all_questions, color=0x8368ff)
            await ctx.send(embed=embed1)
            while True:
                while True:
                    await ctx.send("What is the question number of the reply that you would like to critique?"
                                   "\n**Please just give the question number!**"
                                   "If you would like to critique something in general, reply with `14`")
                    question = await client.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                    question = question.content
                    if str(question) in ("1","2","3","4","5","6","7","8","9","10","11","12","13","14"):
                        question = question_number.get(int(question), 'None')
                        break
                    else:
                        await ctx.send("Please respond with a valid number. (1-14)")

                await ctx.send(f"`{question}`"
                               "\n**What was the issue that you found with their reply?**")
                critique = await client.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                critique = critique.content

                embed.add_field(name=question,
                                value=critique,
                                inline=False)
                z = 0
                await ctx.send(embed=embed)
                z = z + 1

                embed1 = discord.Embed(title="Would you like to critique more questions?", color=0x8368ff)
                embed1.add_field(name="If yes:", value="Reply with `Yes`")
                embed1.add_field(name="If not:", value="Reply with `No`")
                await ctx.send(embed=embed1)


                more = await client.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                more = more.content
                more = more.capitalize()

                if more in ('Yes', 'Yeah', 'Ye', 'Yea'):
                    continue
                else:
                    await channel.send(embed=embed)
                    break
    except Exception as e:
        error_channel = client.get_channel(523743721443950612)
        print(e)
        await error_channel.send(f"Error in {ctx.channel.name} while running `deny`\n{e}\n<@!326399363943497728>")
@deny.error
async def deny_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please specify the player to be denied! The syntax is as follows',
                              description="deny `Discord @` `Discord Channel #`", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(kick_members=True)
async def challenge(ctx, x):
    channel = client.get_channel(753103243659444286)
    staff = discord.utils.get(ctx.guild.roles, name="Staff")
    if staff in ctx.author.roles:
        if x == "e":
            msg = await ctx.send(content="**What would you like the first challenge under the easy category to be (name)?**")
            challenge1 = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1 = challenge1.content

            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge1_prize = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1_prize = challenge1_prize.content

            await msg.edit(
                content="**What would you like the second challenge under the easy category to be?"
                        "\nIf you don't want one, type None**")
            challenge2 = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2 = challenge2.content
            if challenge2 == "None":
                embed = discord.Embed(title="Easy", color=0x90ee90)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            else:
                await msg.edit(content="What is the prize for completing this challenge?")
                challenge2_prize = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
                challenge2_prize = challenge2_prize.content

                embed = discord.Embed(title="Easy", color=0x90ee90)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
                embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
            await channel.send(f'*Complete the following challenges to get prizes*\nTo view the store, use `!shop`')
            await channel.send(embed=embed)

        if x == "m":
            msg = await ctx.send("**What would you like the first challenge under the medium category to be (name)?**")
            challenge1 = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1 = challenge1.content

            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge1_prize = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1_prize = challenge1_prize.content

            await msg.edit(
                content="**What would you like the second challenge under the medium category to be?"
                        "\nIf you don't want one, type None**")
            challenge2 = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2 = challenge2.content
            if challenge2 == "None":
                embed = discord.Embed(title="Medium", color=0xffa500)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            else:
                await msg.edit(content="**What is the prize for completing this challenge?**")
                challenge2_prize = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
                challenge2_prize = challenge2_prize.content

                embed = discord.Embed(title="Medium", color=0xffa500)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
                embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
            await channel.send(embed=embed)

        if x == "h":
            msg = await ctx.send("**What would you like the challenge under the hard category to be (name)?**")
            challenge1 = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1 = challenge1.content

            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge1_prize = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge1_prize = challenge1_prize.content

            await msg.edit(
                content="**What would you like the second challenge under the hard category to be?"
                        "\nIf you don't want one, type None**")
            challenge2 = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2 = challenge2.content
            if challenge2 == "None":
                embed = discord.Embed(title="Hard", color=0xcd5c5c)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            else:
                await msg.edit(content="**What is the prize for completing this challenge?**")
                challenge2_prize = await client.wait_for('message', check=lambda x: x.author == ctx.message.author)
                challenge2_prize = challenge2_prize.content

                embed = discord.Embed(title="Hard", color=0xcd5c5c)
                embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
                embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
                embed.set_footer(text="You can only do one challenge once.")
            await channel.send(embed=embed)
    else:
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to create a challenge post!", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command()
async def messagespam(ctx, *, x):
    try:
        if ctx.author.name == "Amogh":
            y = 0
            while True:
                if y < 10:
                    await ctx.send(x)
                    y = y+1
                    continue
                else:
                    break
        else:
            embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                                  description="This command is exclusively for Rowdies", color=0xff0000)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=embed)
    except Exception as e:
        error_channel = client.get_channel(761227927583981598)
        print(e)
        await error_channel.send(f"Error in {ctx.channel.name}\n{e}\n<@!326399363943497728>")




'''-----------------------------------------------------------------------------------------------------Hypixel----------------------------------------------------------------------------------------------------------------'''
guild = 'Miscellaneous'


@client.command(aliases=['Register', 'reg', 'Reg', 'Verify', 'verify'])
async def register(ctx, name):
    try:
        async with ctx.channel.typing():
            author = ctx.author
            if str(ctx.channel) == "register":
                request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
                if request.status_code != 200:
                    await ctx.send('Please enter a valid ign!')
                else:
                    request = request.json()
                    ign = request['name']
                    uuid = request['id']

                    guild_name = hypixel.get_guild(name)
                    newmember = discord.utils.get(ctx.guild.roles, name="New Member")
                    awaiting_app = discord.utils.get(ctx.guild.roles, name="Awaiting Approval")
                    member = discord.utils.get(ctx.guild.roles, name="Member")
                    guest = discord.utils.get(ctx.guild.roles, name="Guest")
                    staff = discord.utils.get(ctx.guild.roles, name="Staff")
                    officer = discord.utils.get(ctx.guild.roles, name="Officer")
                    tofficer = discord.utils.get(ctx.guild.roles, name="Trial Officer")
                    xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")


                    nick = await author.edit(nick=ign)
                    if guild_name == "Miscellaneous":
                        await ctx.author.remove_roles(newmember)

                        await ctx.channel.purge(limit=1)
                        embed = discord.Embed(title="Registration successfull!")
                        embed.add_field(name=ign,
                                        value="Member of Miscellaneous")

                        embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                        await ctx.send(embed=embed)
                        await ctx.author.add_roles(member)

                    elif guild_name == "XL":
                        await ctx.author.remove_roles(newmember)
                        await ctx.author.add_roles(guest, xl_ally)


                        await ctx.channel.purge(limit=1)
                        embed = discord.Embed(title="Registration successfull!")
                        embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                        embed.add_field(name=ign, value="Member of XL")
                        await ctx.send(embed=embed)

                    elif guild_name not in ("Miscellaneous", "XL"):
                        await ctx.author.remove_roles(newmember)
                        await ctx.author.add_roles(awaiting_app)
                        if nick is None:
                            nick = author.name

                        await ctx.channel.purge(limit=1)
                        embed = discord.Embed(title="Registration successfull!")
                        embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                        embed.add_field(name=ign, value="New Member")
                        await ctx.send(embed=embed)

                        category = discord.utils.get(ctx.guild.categories, name="RTickets")
                        ticket_channel = await ctx.guild.create_text_channel(f"registration-ticket-{nick}",
                                                                             category=category)
                        await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False,
                                                             read_messages=False)
                        await ticket_channel.set_permissions(staff, send_messages=True, read_messages=True,
                                                             add_reactions=True, embed_links=True, attach_files=True,
                                                             read_message_history=True, external_emojis=True)
                        await ticket_channel.set_permissions(officer, send_messages=True, read_messages=True,
                                                             add_reactions=True, embed_links=True, attach_files=True,
                                                             read_message_history=True, external_emojis=True)
                        await ticket_channel.set_permissions(tofficer, send_messages=True, read_messages=True,
                                                             add_reactions=True, embed_links=True, attach_files=True,
                                                             read_message_history=True, external_emojis=True)
                        await ticket_channel.set_permissions(author, send_messages=True, read_messages=True,
                                                             add_reactions=True, embed_links=True, attach_files=True,
                                                             read_message_history=True, external_emojis=True)
                        await ticket_channel.set_permissions(newmember, send_messages=False, read_messages=False,
                                                             add_reactions=True, embed_links=True, attach_files=True,
                                                             read_message_history=True, external_emojis=True)

                        embed = discord.Embed(title="Miscellaneous Guild Requirements", description="These requirements are subject to change!", color=0x8368ff)
                        embed.add_field(name="Active",
                                        value=f"•  {format(active,',d')} Weekly Guild Experience",
                                        inline=False)
                        embed.add_field(name="DNKL Eligibility",
                                        value=f"•  {format(dnkl,',d')} Weekly Guild Experience",
                                        inline=False)
                        embed.add_field(name="Resident",
                                        value=f"•  {format(resident_req,',d')} Weekly Guild Experience",
                                        inline=False)
                        embed.add_field(name="Member",
                                        value=f"•  {format(inactive,',d')} Weekly Guild Experience",
                                        inline=False)
                        embed.add_field(name="New Member",
                                        value=f"•  {format(new_member,',d')} Daily Guild Experience",
                                        inline=False)
                        embed.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                                              "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
                        await ctx.author.send(embed=embed)
            else:
                await ctx.send('This command can only be used in the registration channel!')
    except Exception as e:
        error_channel = client.get_channel(523743721443950612)
        print(e)
        await error_channel.send(f"Error in {ctx.channel.name} while trying to use `register`\n{e}\n<@!326399363943497728>")


@client.command()
async def sync(ctx, name):
    try:
        author = ctx.author

        ign = hypixel.get_dispname(name)

        if ign is None:
            await ctx.send('Please enter a valid ign!')
        else:
            guild_name = hypixel.get_guild(name)
            guest = discord.utils.get(ctx.guild.roles, name="Guest")
            member = discord.utils.get(ctx.guild.roles, name="Member")
            awaiting_app = discord.utils.get(ctx.guild.roles, name="Awaiting Approval")
            xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")


            await author.edit(nick=ign)
            if guild_name == "Miscellaneous":
                await ctx.author.remove_roles(guest,awaiting_app)
                await ctx.author.add_roles(member)
                embed = discord.Embed(title="Your nick and role was succesfully changed!",
                                      description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                      color=0x8368ff)
                embed.set_footer(text="Member of Miscellaneous\n• Nick Changed\n• Guest & Awaiting Approval were removed\n• Member was given")
                await ctx.send(embed=embed)

            elif guild_name == "XL":
                await ctx.author.remove_roles(member, awaiting_app)
                await ctx.author.add_roles(guest, xl_ally)

                embed = discord.Embed(title="Your nick and role was succesfully changed!",
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
                    embed = discord.Embed(title="Your nick and role was succesfully changed!",
                                          description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                          color=0x8368ff)
                    embed.set_footer(text=f"Member of {guild_name}\n• Nick Changed\n• Member & Awaiting Approval were removed\n• Guest was given")
                    await ctx.send(embed=embed)
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!", color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while trying to use `sync`\n{e}\n<@!326399363943497728>")


@client.command(aliases=['ForceSync', 'Forcesync', 'forceSync', 'FORCESYNC', 'fs', 'Fs', 'FS', 'fS'])
async def forcesync(ctx, member: discord.Member, name):
    try:
        officer = discord.utils.get(ctx.guild.roles, name="Officer")
        admin = discord.utils.get(ctx.guild.roles, name="Admin")
        if officer or admin in ctx.author.roles:
            ign = hypixel.get_dispname(name)
            if ign is None:
                await ctx.send('Please enter a valid ign!')
            else:
                guild_name = hypixel.get_guild(name)
                newmember = discord.utils.get(ctx.guild.roles, name="New Member")
                guest = discord.utils.get(ctx.guild.roles, name="Guest")
                member_ = discord.utils.get(ctx.guild.roles, name="Member")
                awaiting_app = discord.utils.get(ctx.guild.roles, name="Awaiting Approval")
                xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")


                await member.edit(nick=ign)

                if guild_name == "Miscellaneous":
                    await member.remove_roles(guest,awaiting_app,newmember)
                    await member.add_roles(member_)
                    embed = discord.Embed(title=f"{member.name}'s nick and role were succesfully changed!",
                                          description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                          color=0x8368ff)
                    embed.set_footer(text="Member of Miscellaneous\n• Nick Changed\n• Guest & Awaiting Approval were removed\n• Member was given")
                    await ctx.send(embed=embed)


                elif guild_name == "XL":
                    await member.remove_roles(member_,awaiting_app)
                    await member.add_roles(guest, xl_ally)

                    embed = discord.Embed(title="Your nick and role was succesfully changed!",
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
                        embed = discord.Embed(title=f"{member.name}'s nick and role were succesfully changed!",
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
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while trying to use `forcesync`\n{e}\n<@!326399363943497728>")


@client.command(aliases=["i", "I"])
async def info(ctx, name=None):
    try:
        async with ctx.channel.typing():
            if name is None:
                author = ctx.author
                name = author.nick
                if name is None:
                    x = author.name
                    name = x
            req = hypixel.get_data(name)
            if req["player"] is None:
                embed = discord.Embed(title="Your discord nick doesn't match your minecraft name",
                                      description=',sync `Your minecraft name`', color=0xff0000)
                await ctx.channel.purge(limit=1)
                await ctx.send(embed=embed)
            else:
                ign = req["player"]["displayname"]
                uuid = req["player"]['uuid']
                api = hypixel.get_api()
                req2 = requests.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}').json()

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

    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!",description="Please try again in a while!",color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while trying to use `i` \n{e}\n<@!326399363943497728>")


# Do-Not-Kick-List
@client.command(aliases=["Dnkladd", "DNKLADD", "DnklAdd"])
@commands.has_permissions(manage_messages=True)
async def dnkladd(ctx, name = None, w = None, x = None, y = None, *, z = None):
    try:
        if name is not None:
            ign = hypixel.get_dispname(name)
            rank = hypixel.get_rank(name)
            request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{ign}')
            uuid = request.json()['id']
            with open('dnkl.json') as f:
                data = json.load(f)
            if request.status_code != 200:
                await ctx.send('Unknown IGN!')
            else:
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
                    embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
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
        else:
            await ctx.send("**What is the name of the user you wish to add to the do not kick list?**")

            name = await client.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            name = name.content
            ign = hypixel.get_dispname(name)
            rank = hypixel.get_rank(name)
            request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{ign}')
            uuid = request.json()['id']

            with open('dnkl.json') as f:
                data = json.load(f)

            if request.status_code != 200:
                await ctx.send('Unknown IGN!')
            else:
                await ctx.send("**What is the start date?** (DD/MM/YYYY)")
                start_date = await client.wait_for('message',
                                             check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                start_date = start_date.content
                await ctx.send("**What is the end date?** (DD/MM/YYYY)")
                end_date = await client.wait_for('message',
                                                   check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                end_date = end_date.content

                reason = await client.wait_for('message',
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
                    embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                    embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                    embed.add_field(name="Start:", value=f"{a} {start_month} {c}", inline=False)
                    embed.add_field(name="End:", value=f"{p} {end_month} {r}", inline=False)
                    embed.add_field(name="Reason", value=f"{reason}", inline=False)
                    embed.set_author(name="Do not kick list")
                    dnkl_channel = client.get_channel(523743721443950612)
                    message = await dnkl_channel.send(embed=embed)

                    dnkl_dict = {ign: message.id}

                    data.update(dnkl_dict)
                    with open('dnkl.json', 'w') as f:
                        json.dump(data, f)



    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!",
                                  description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error while trying to add a user to the DNKL\n{e}\n<@!326399363943497728>")
@dnkladd.error
async def dnkladd_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please check the command! The syntax is as follows',
                              description='dnkl `IGN` `Discord @|Use a random character` `Start Date` `End Date` `Reason`',
                              color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to add a user to the do not kick list!",
                              color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)
@client.command(aliases=['dnklrmv', 'Dnklrmv', 'DNKLRMV', 'DNKLrmv', 'DnklRmv'])
@commands.has_permissions(manage_messages=True)
async def dnklremove(ctx, name):
    try:
        request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
        if request.status_code != 200:
            await ctx.send('Unknown IGN!')
        else:
            ign = request.json()['name']
            with open("dnkl.json", 'r') as f:
                data = json.load(f)

            if ign not in data.keys():
                await ctx.send('This player is not on the Do-not-kick-list!')

            msgid = f"{data[ign]}"

            data.pop(ign)
            with open('dnkl.json', 'w') as f:
                json.dump(data, f)

            dnkl_channel = client.get_channel(629564802812870657)
            msg = await dnkl_channel.fetch_message(msgid)
            await msg.delete()

            await ctx.send(f'{ign} has been removed from the do-not-kick-list!')

    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!",
                                  description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            print(e)
            if str(e) == "404 Not Found (error code: 10008): Unknown Message":
                await ctx.send(f'{ign} was removed but the message was not found.')
@dnklremove.error
async def dnklremove_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please check the command! The syntax is as follows',
                              description='dnklrmv `IGN`',
                              color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to remove a user from the do not kick list!",
                              color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command(aliases=['Dnkllist', 'DNKLLIST', 'DnklList'])
async def dnkllist(ctx, raw=None):
    try:
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
    except Exception as e:
        error_channel = client.get_channel(523743721443950612)
        print(e)
        await error_channel.send(
            f"Error in {ctx.channel.name} while running dnkllist"
            f"\n{e}\n<@!326399363943497728>")

# Blacklist
@client.command(aliases=["blacklist", "Blacklist", "Bl"])
@commands.has_permissions(manage_messages=True)
async def bl(ctx, name, x, *, y):
    try:
        rank = hypixel.get_rank(name)

        request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
        if request.status_code != 200:
            await ctx.send('Unknown IGN!')
        else:
            ign = request.json()["name"]
            if x in ("None", "Never"):
                uuid = request.json()['id']
                embed = discord.Embed(title=f"{rank} {ign}",
                                      url=f'https://plancke.io/hypixel/player/stats/{ign}', color=0xff0000)
                embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                embed.add_field(name="End:", value="Never", inline=False)
                embed.add_field(name="Reason:", value=f"{y}", inline=False)
                embed.set_author(name="Blacklist")
                await ctx.channel.purge(limit=1)
                await ctx.send(embed=embed)
            else:
                t = x.split('/')
                a = int(t[0])
                b = int(t[1])
                c = int(t[2])
                if b > 12:
                    embed = discord.Embed(title='Please enter a valid date!', description="`DD/MM/YYYY`",
                                          color=0xff0000)
                    await ctx.send(embed=embed)
                if b <= 12:
                    dates = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
                    end_month = dates.get(b)

                    uuid = request.json()['id']
                    embed = discord.Embed(title=f"{rank} {ign}",
                                          url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                          color=0xff0000)
                    embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                    embed.add_field(name="IGN:", value=ign, inline=False)
                    embed.add_field(name="End:", value=f"{a} {end_month} {c}", inline=False)
                    embed.add_field(name="Reason:", value=y, inline=False)
                    embed.set_author(name="Blacklist")
                    await ctx.channel.purge(limit=1)
                    await ctx.send(embed=embed)
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!", color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while trying  to blacklist a user\n{e}\n<@!326399363943497728>")
@bl.error
async def bl_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please check the command! The syntax is as follows',
                              description='bl `IGN` `End Date` `Reason`', color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="Your role lacks permissions to blacklist a user", color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command(aliases=["gi", "Gi", "GI"])
async def ginfo(ctx, *, name):
    try:
        async with ctx.channel.typing():
            req = hypixel.get_guild_data(name)

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
            onlinerecord = hypixel.get_guild_onlinerecord(name)

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
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `ginfo`\n{e}\n<@!326399363943497728>")
@ginfo.error
async def ginfo_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please check the command! The syntax is as follows',
                              description='ginfo `Minecraft name`', color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command(aliases=['ge', "Ge", "Gexp"])
async def gexp(ctx, gname):
    try:
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = hypixel.get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.hypixel.net/guild?key={api}&name={gname}') as req:
                req = await req.json()
        array = {}
        exp = 0
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 20 seconds`")
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
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `gexp`\n{e}\n<@!326399363943497728>")
@gexp.error
async def gexp_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Please check the command! The syntax is as follows',
                              description='gexp `Guild Name`', color=0xff0000)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)


@client.command(aliases=["Gactive"])
async def gactive(ctx):
    try:
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        gname = 'Rowdies'
        link = f'https://api.slothpixel.me/api/guilds/{gname}'
        g = requests.get(link).json()
        array = {}
        exp = 0
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 5 seconds`")
        async with ctx.channel.typing():
            for i in range(len(g['members'])):
                expHistory = sum(g['members'][i]['exp_history'].values())
                if expHistory >= active:
                    uuid = g['members'][i]['uuid']
                    a = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
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
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `gactive`\n{e}\n<@!326399363943497728>")


@client.command(aliases=['Ginactive'])
async def ginactive(ctx):
    try:
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        gname = 'Rowdies'
        link = f'https://api.slothpixel.me/api/guilds/{gname}'
        g = requests.get(link).json()
        array = {}
        exp = 0
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 10 seconds!`")
        async with ctx.channel.typing():
            for i in range(len(g['members'])):
                expHistory = sum(g['members'][i]['exp_history'].values())
                if expHistory < inactive:
                    uuid = g['members'][i]['uuid']
                    a = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
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
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `ginactive`\n"
                                     f"{e}\n<@!326399363943497728>")


@client.command(aliases=['gr', 'Gr', 'Grank'])
async def grank(ctx, reqrank):
    try:
        reqrank = reqrank.capitalize()
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        gname = 'Rowdies'
        link = f'https://api.slothpixel.me/api/guilds/{gname}'
        g = requests.get(link).json()
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
                    a = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
                    name = a['name']
                    expHistory = sum(g['members'][i]['exp_history'].values())
                    name = name
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
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `grank`\n{e}\n<@!326399363943497728>")


@client.command(aliases=['gm', 'Gm', 'Gmember', 'g', 'G'])
async def gmember(ctx, name=None):
    try:
        if name is None:
            author = ctx.author
            name = author.nick
            if name is None:
                x = author.name
                name = x
        results = []
        dates = []
        weeklyexp = []
        if name in ('top', 'Top'):
            embed = discord.Embed(title="Incorrect syntax!",
                                  description="The command you're trying to use is `,gtop`", color=0xff0000)
            await ctx.send(embed=embed)
        else:
            request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
            if request.status_code != 200:
                await ctx.send('Unknown IGN!')
            else:
                name = request.json()['name']
                uuid = request.json()['id']
                api = hypixel.get_api()
                req = requests.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}').json()

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
                                if totalexp > resident_req:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("res_met")
                                else:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("res_not_met")
                            else:
                                if totalexp > active:
                                    colour, GraphColor, GraphBorder = hypixel.get_color("active")
                                elif totalexp > inactive:
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
                            if ctx.channel.name == "general":
                                name = name.replace("_",        "\_")
                                await ctx.send(f"__**{name}**__\n**Guild Experience-** `{totalexp}`")
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

    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!",
                                  description="Please try again in a while!", color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `g` \n{e}\n<@!326399363943497728>")


@client.command(aliases=['dnklchk', 'Dnklchk', 'DNKLCHK', 'Dnklcheck', 'DNKLCHECK'])
async def dnklcheck(ctx, name=None):
    try:
        if name is None:
            author = ctx.author
            name = author.nick
            if name is None:
                x = author.name
                name = x
        request = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
        if request.status_code != 200:
            await ctx.send('Unknown IGN!')
        else:
            name = request.json()['name']
            uuid = request.json()['id']
            api = hypixel.get_api()
            data = requests.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}').json()
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
                        if totalexp >= dnkl:
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
                                            value=f"You need a minimum of {format(dnkl,',d')} weekly guild experience.\n You have {totalexp} weekly guild experience.",
                                            inline=True)
                        else:
                            embed = discord.Embed(title=name,
                                                  url=f'https://visage.surgeplay.com/full/832/{uuid}',
                                                  color=0x333cff)
                            embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                            embed.set_author(name='Do-not-kick-list: Eligibility Check')
                            embed.add_field(name="You are eligible to apply for the do not kick list.",
                                            value=f"You meet the minimum of {format(dnkl,',d')} weekly guild experience.\n You have {totalexp} weekly guild experience.",
                                            inline=True)
                        await ctx.send(embed=embed)
    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!", color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `dnklchk`\n{e}\n<@!326399363943497728>")


@client.command(aliases=["Gtop", "gt", "Gt"], pass_context=True)
async def gtop(ctx):
    try:
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = hypixel.get_api()
        req = requests.get(f'https://api.hypixel.net/guild?key={api}&name=Miscellaneous').json()
        array = {}
        exp = 0
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 15 seconds`")
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
                    mojang = requests.get(
                        f'https://sessionserver.mojang.com/session/minecraft/profile/{user[0]}').json()
                    name = mojang['name']

                    data = requests.get(f"https://api.hypixel.net/player?key={api}&name={name}").json()

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
            image = requests.get(url)

            with open('temppicture.jpg', 'wb') as f:
                f.write(image.content)
            await ctx.send(file=discord.File('temppicture.jpg'))

    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again i n a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `gtop`\n{e}\n<@!326399363943497728>")


@client.command()
async def dailylb(ctx, x=1):
    try:
        await ctx.channel.purge(limit=1)
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = hypixel.get_api()
        req = requests.get(f'https://api.hypixel.net/guild?key={api}&name=Miscellaneous').json()
        array = {}
        await msg.edit(content=f"**Please wait!**\n `Approximate wait time: 15 seconds`")
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
                    mojang = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{user[0]}').json()
                    name = mojang['name']

                    data = requests.get(f"https://api.hypixel.net/player?key={api}&name={name}").json()

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
            image = requests.get(url)

            with open('temppicture.jpg', 'wb') as f:
                f.write(image.content)
            await ctx.send(file=discord.File('temppicture.jpg'))

    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `dailylb`\n{e}\n<@!326399363943497728>")

'-------------------------------------------------------------------------------------------------------STAFF COMMANDS----------------------------------------------------------------------------------------------------------'

@client.command(aliases=["Staff"])
async def staff(ctx):
    try:
        msg = await ctx.send("**Please wait!**\n `Approximate wait time: Calculating`")
        api = hypixel.get_api()
        link = f'https://api.hypixel.net/guild?key={api}&name=Miscellaneous'
        g = requests.get(link).json()

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
                if expHistory >= active and rank == "Member":
                    uuid = g['guild']['members'][i]['uuid']
                    a = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
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
                elif expHistory < active and rank == "Active":
                    uuid = g['guild']['members'][i]['uuid']
                    a = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
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
                elif expHistory < inactive:
                    if rank == "Member":
                        uuid = g['guild']['members'][i]['uuid']
                        a = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
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
                        if expHistory < resident_req:
                            uuid = g['guild']['members'][i]['uuid']
                            a = requests.get(f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}').json()
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
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `staff`\n{e}\n<@!326399363943497728>")


@client.command()
async def staffreview(ctx):
    try:
        channel = client.get_channel(523226672980557824)
        admin = discord.utils.get(ctx.guild.roles, name="Admin")
        if admin in ctx.author.roles:
            embed = discord.Embed(title="Staff checkup", color=0x8368ff)
            while True:
                await ctx.send('**What is the name of the staff member?**')
                staff_name = await client.wait_for('message', check=lambda x: x.author == ctx.message.author and x.channel == ctx.channel)
                staff_name = staff_name.content

                await ctx.send(f"**What are your comments about** *{staff_name}*")
                staff_comm = await client.wait_for('message', check=lambda x: x.author == ctx.message.author and x.channel == ctx.channel)
                staff_comm = staff_comm.content
                embed.add_field(name=staff_name, value=staff_comm, inline=False)


                embed1 = discord.Embed(title="Is that it or are there more staff members?", color=0x8368ff)
                embed1.add_field(name="If yes:", value="Reply with `Yes`")
                embed1.add_field(name="If not:", value="Reply with `No`")
                await ctx.send(embed=embed1)

                more = await client.wait_for('message', check=lambda x: x.channel == ctx.channel)
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
        error_channel = client.get_channel(523743721443950612)
        print(e)
        await error_channel.send(f"Error in {ctx.channel.name} while using `staffreview`\n{e}\n<@!326399363943497728>")


@client.command()
async def rolecheck(ctx):
    try:
        guild_master = discord.utils.get(ctx.guild.roles, name="Guild Master")
        staff = discord.utils.get(ctx.guild.roles, name="Staff")
        new_member = discord.utils.get(ctx.guild.roles, name="New Member")
        guest = discord.utils.get(ctx.guild.roles, name="Guest")
        member_role = discord.utils.get(ctx.guild.roles, name="Member")
        active_role = discord.utils.get(ctx.guild.roles, name="Active")
        inactive_role = discord.utils.get(ctx.guild.roles, name="Inactive")
        xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")
        jenos_ally = discord.utils.get(ctx.guild.roles, name="Jenos - Ally")
        betrayed_ally = discord.utils.get(ctx.guild.roles, name="Betrayed - Ally")

        msg = await ctx.send("**Processing all the prerequisites**")

        misc_uuids, xl_uuids, jenos_uuids, betrayed_uuids = hypixel.get_guild_members("Miscellaneous"),hypixel.get_guild_members("XL"),hypixel.get_guild_members("Jenos"),hypixel.get_guild_members("Betrayed")


        misc_members, calm_members, xl_members, jenos_members, betrayed_members = [], [], [],[],[]

        #Miscellaneous Member Names
        await msg.edit(content="**Processing** - 1/4")
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
        await msg.edit(content="**Processing** - 2/4")
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

        #Betrayed Member Names
        await msg.edit(content="**Processing** - 3/4")
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
                    for individual_uuid in jenos_uuids
                ]
                for response in await asyncio.gather(*tasks):  # Puts the result into a list
                    jenos_members.append(response)

        # Betrayed Member Names
        await msg.edit(content="**Processing** - 4/4")
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
                    for individual_uuid in betrayed_uuids
                ]
                for response in await asyncio.gather(*tasks):  # Puts the result into a list
                    betrayed_members.append(response)

        if staff in ctx.author.roles:  # Making sure that the user is Staff
            for guild in client.guilds:
                if str(guild) == "Miscellaneous [MISC]":  # Check if the Discord is Miscellaneous
                    for member in guild.members:  # For loop for all members in the Discord
                        if member.id != '326399363943497728' and member.bot is False:
                            name = member.nick  # Obtaining their nick
                            if name is None:  # If they don't have a nick, it uses their name.
                                name = member.name

                            else:
                                message = await ctx.send(f"Checking {name}")

                                mojang = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{name}')
                                if mojang.status_code != 200:  # If the IGN is invalid
                                    await member.remove_roles(member_role, guest)
                                    await member.add_roles(new_member)
                                    await message.edit(content=
                                                       f"{name} ||{member}|| Player doesn't exist. **++New Member | --Member | -- Guest**")
                                elif guild_master not in member.roles:
                                    ign = mojang.json()["name"]
                                    uuid = mojang.json()['id']
                                    await member.edit(nick=ign)


                                    #Miscellaneous
                                    if ign in misc_members and ign != "Rowdies":
                                        req = requests.get(f"https://api.hypixel.net/guild?key={hypixel.get_api()}&player={uuid}").json()


                                        if member_role not in member.roles:
                                            await member.add_roles(member)
                                            await member.remove_roles(new_member, guest)

                                            for user in req['guild']["members"]:
                                                if uuid == user["uuid"]:
                                                    totalexp = user['expHistory']
                                                    totalexp = sum(totalexp.values())

                                            if totalexp < inactive:
                                                await member.add_roles(inactive_role)
                                                await member.remove_roles(active_role)
                                                await message.edit(
                                                    content=f"{name} ||{member}|| **++Member \| ++Inactive \| --Active**")

                                            elif totalexp >= active:  # If the member is active
                                                await member.remove_roles(inactive_role, new_member)
                                                await member.add_roles(active_role)
                                                await message.edit(
                                                    content=f"{name} ||{member}|| **++Member \| ++Active \| --Inactive**")

                                            elif totalexp > inactive:
                                                await member.remove_roles(inactive_role, active_role)
                                                await message.edit(
                                                    content=f"{name} ||{member}|| **++Member \| --Inactive\| --Active**")

                                        elif member_role in member.roles:
                                            # No change in terms of membership

                                            for user in req['guild']["members"]:
                                                if uuid == user["uuid"]:
                                                    totalexp = user['expHistory']
                                                    totalexp = sum(totalexp.values())

                                            if totalexp < inactive:
                                                await member.add_roles(inactive_role)
                                                await member.remove_roles(active_role)
                                                await message.edit(
                                                    content=f"{name} ||{member}|| Already Member  **++Inactive \| --Active**")

                                            elif totalexp >= active:  # If the member is active
                                                await member.remove_roles(inactive_role, new_member)
                                                await member.add_roles(active_role)
                                                await message.edit(
                                                    content=f"{name} ||{member}|| Already Member **++Active \| --Inactive**")

                                            elif totalexp > inactive:
                                                await member.remove_roles(inactive_role)
                                                await member.remove_roles(active_role)
                                                await message.edit(
                                                    content=f"{name} ||{member}|| Already Member  **--Inactive\| --Active**")


                                    elif ign in xl_members:
                                        await member.add_roles(guest, xl_ally)
                                        await member.remove_roles(member_role, new_member, active_role)
                                        await message.edit(content=f"{name} ||{member}|| Member of XL **++XL - Ally \| ++Guest | --Member | --Active**")

                                    elif ign in jenos_members:
                                        await member.add_roles(guest, jenos_ally)
                                        await member.remove_roles(member_role, new_member, active_role)

                                        await message.edit(
                                            content=f"{name} ||{member}|| Member of Jenos **++Jenos - Ally \| ++Guest | --Member | --Active**")

                                    elif ign in betrayed_members:
                                        await member.add_roles(guest, betrayed_ally)
                                        await member.remove_roles(member_role, new_member, active_role)
                                        await message.edit(content=f"{name} ||{member}|| Member of Betrayed **++Betrayed - Ally \| ++Guest | --Member | --Active**")


                                    else:
                                        await member.add_roles(guest)
                                        await member.remove_roles(member_role, new_member, active_role)
                                        await message.edit(content=f"{name} ||{member}|| Member of an unallied guild **++Guest | --Member | --Active**")

        inactivity_channel = client.get_channel(848067712156434462)

        embed = discord.Embed(title="You do not meet the guild requirements!",
                              description=f"Member requirement - {format(inactive,',d')} Weekly Guild Experience",
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
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n{ctx.author.mention} please `forcesync` the last user on the list.")

        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(
                f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n<@!326399363943497728>")



@client.command()
async def newrolecheck(ctx):
    try:
        guild_master = discord.utils.get(ctx.guild.roles, name="Guild Master")
        staff = discord.utils.get(ctx.guild.roles, name="Staff")
        new_member = discord.utils.get(ctx.guild.roles, name="New Member")
        guest = discord.utils.get(ctx.guild.roles, name="Guest")
        member_role = discord.utils.get(ctx.guild.roles, name="Member")
        active_role = discord.utils.get(ctx.guild.roles, name="Active")
        inactive_role = discord.utils.get(ctx.guild.roles, name="Inactive")
        calm_ally = discord.utils.get(ctx.guild.roles, name="Calm - Ally")
        xl_ally = discord.utils.get(ctx.guild.roles, name="XL - Ally")
        jenos_ally = discord.utils.get(ctx.guild.roles, name="Jenos - Ally")
        betrayed_ally = discord.utils.get(ctx.guild.roles, name="Betrayed - Ally")

        misc_info, calm_members, xl_members, jenos_members, betrayed_members,discord_members,\
        invalid_members, active_members, regular_members,inactive_members,\
        calm_discord_members, xl_discord_members, betrayed_discord_members, jenos_discord_members , guest_list = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

        guild = client.get_guild(522586672148381726)
        memberList = guild.members

        msg = await ctx.send("**Processing all the prerequisites**")

        misc_details, calm_uuids, xl_uuids, jenos_uuids, betrayed_uuids = hypixel.get_misc_members(
            "Miscellaneous"), hypixel.get_guild_members("Calm"), hypixel.get_guild_members("XL"), hypixel.get_guild_members(
            "Jenos"), hypixel.get_guild_members("Betrayed")

        count = 0
        # Miscellaneous Member Names + gexp
        await msg.edit(content="**Processing** - 1/5")
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

        # Calm Member Names
        await msg.edit(content="**Processing** - 2/5")
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
                    for individual_uuid in calm_uuids
                ]
                for response in await asyncio.gather(*tasks):  # Puts the result into a list
                    calm_members.append(response)

        # XL Member Names
        await msg.edit(content="**Processing** - 3/5")
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

        # Betrayed Member Names
        await msg.edit(content="**Processing** - 4/5")
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
                    for individual_uuid in jenos_uuids
                ]
                for response in await asyncio.gather(*tasks):  # Puts the result into a list
                    jenos_members.append(response)

        # Betrayed Member Names
        await msg.edit(content="**Processing** - 5/5")
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
                    for individual_uuid in betrayed_uuids
                ]
                for response in await asyncio.gather(*tasks):  # Puts the result into a list
                    betrayed_members.append(response)

        if staff in ctx.author.roles:  # Making sure that the user is Staff
            for guild in client.guilds:
                if str(guild) == "Miscellaneous [MISC]":  # Check if the Discord is Miscellaneous
                    for member in guild.members:  # For loop for all members in the Discord
                        if not member.bot:
                            discord_members.append(member)

            invalid_names = active_names = inactive_names = member_names = calm_names = xl_names = betrayed_names = jenos_names = ""
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
                        if element[1] > active:
                            active_members.append(member)
                            active_names = active_names + str(member) + "\n"
                        elif element[1] > inactive:
                            if member_role not in member.roles:
                                regular_members.append(member)
                                member_names = member_names + str(member) + "\n"
                        elif element[1] < inactive:
                            inactive_members.append(member)
                            inactive_names = inactive_names + str(member) + "\n"

                if name in calm_members:
                    if calm_ally not in member.roles:
                        calm_discord_members.append(member)
                        calm_names = calm_names + str(member) + "\n"
                elif name in xl_members:
                    if xl_ally not in member.roles:
                        xl_discord_members.append(member)
                        xl_names = xl_names + str(member) + "\n"
                elif name in betrayed_members:
                    if betrayed_ally not in member.roles:
                        betrayed_discord_members.append(member)
                        betrayed_names = betrayed_names + str(member) + "\n"
                elif name in jenos_members:
                    if jenos_ally not in member.roles:
                        jenos_discord_members.append(member)
                        jenos_names = jenos_names + str(member) + "\n"
                else:
                    guest_list.append(member)
            invalid_embed = discord.Embed(title="Invalid: Given @New Member", description=invalid_names, color=0x620B06)
            active_embed = discord.Embed(title="Active: Given @Active", description=active_names, color=0x0073BF)
            member_embed = discord.Embed(title="Member: Given @Member", description=member_names, color=0x4DFF00)
            inactive_embed = discord.Embed(title="Inactive: Given @inactive", description=inactive_names, color=0xFF4C6E)
            calm_embed = discord.Embed(title="Calm: Given @calm_ally", description=calm_names, color=0xA05E75)
            xl_embed = discord.Embed(title="XL: Given @xl_ally", description=xl_names, color=0xA05E75)
            betrayed_embed = discord.Embed(title="Betrayed: Given @betrayed_ally", description=betrayed_names, color=0xA05E75)
            jenos_embed = discord.Embed(title="Jenos: Given @jenos_ally", description=jenos_names, color=0xA05E75)
            await ctx.send(embed=invalid_embed)
            await ctx.send(embed=active_embed)
            await ctx.send(embed=member_embed)
            await ctx.send(embed=inactive_embed)
            await ctx.send(embed=calm_embed)
            await ctx.send(embed=xl_embed)
            await ctx.send(embed=betrayed_embed)
            await ctx.send(embed=jenos_embed)






    except Exception as e:
        if str(e) == "Expecting value: line 1 column 1 (char 0)":
            embed = discord.Embed(title="The Hypixel API is down!", description="Please try again in a while!",
                                  color=0xff0000)
            await ctx.send(embed=embed)
            print(e)
        elif str(e) == "404 Not Found (error code: 10011): Unknown Role":
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n{ctx.author.mention} please `forcesync` the last user on the list.")

        else:
            error_channel = client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(
                f"Error in {ctx.channel.name} while using `rolecheck`\n{e}\n<@!326399363943497728>")

# ------------------------------------------------------------------------------------WIP-------------------------------------------------------------------------#


@client.command()
async def ticketss(ctx):
    embed = discord.Embed(title='Tickets',
                          description="Tickets can be created for any of the following reasons:-\n"
                                      "> Do Not Kick List\n"
                                      "> Discord Nick/Role Change\n"
                                      "> Problems/Queries/Complaint/Suggestion\n"
                                      "> Reporting a player\n"
                                      "> Milestone\n"
                                      "> Staff Application\n"
                                      "> Other\n"
                                      "The ticket reasons have been explained in detail towards the end of this message.\n"
                                      " Once you have created a ticket by reacting to the bot's message, you will see that there is a new ticket in the \"🎫 Ticket Section\" category.\n"
                                      " When you open the ticket, you will be greeted by a message from the Miscellaneous Bot.\n"
                                      " The bot will ask you to choose the reason behind the creation of your ticket from a given list."
                                      " Choose the appropriate reason and then proceed!\n"
                                      "Once you have created your ticket, staff will respond within 24 hours.\n",color = 0x8368ff)
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/650248396480970782/727875702187229234/Tickets.png?width=1440&height=360')
    embed2 = discord.Embed(title='',description="**Do Not Kick List**:-"
                                                "Once the ticket is created, follow the bots instructions.\n"
                                                "You must either have a valid reason for applying and also meet the do not kick list requirements.\n"
                                                "Accepted Reasons:\n"
                                                "> School\n"
                                                "> Medical Reasons\n"
                                                "> Punished by parents\n"
                                                "> Situations out of your control\n"
                                                "> Vacation (< 2 weeks)\n\n"
                                                "If your account is banned for more than 30 days, then it will be temporarily kicked until it's unbanned."
                                                " If you want to join with an alt, that's fine. "
                                                " We reserve the right to do this for any bans under 30 days as well."
                                                ""
                                                "**Discord Nick/Role Change**:-\n"
                                                "Once the ticket is created, the bot will attempt to automatically sync your roles if it is successful, inform staff that you got the change you desired. "
                                                "If not, inform staff what you would like to change and they will gladly help you!\n\n"
                                                ""
                                                "**Problems/Queries/Complaints/Suggestions**:-\n"
                                                " If you face difficulty in anything, create a ticket! We'll be glad to help you!\n\n"
                                                "**Reporting a player**:-\n"
                                                "When reporting a player, make sure to explain your situation in maximum detail."
                                                "Providing the following details is considered the bare minimum:-\n"
                                                "> Name of user you would like to report\n"
                                                "> Explaination about the offense\n"
                                                "> Time of offense\n"
                                                "> Proof of offense\n"
                                                "If you would like to report a staff member, DM Rowdies.\n\n"
                                                ""
                                                "**Milestone**:-\n"
                                                "Once you choose milestone as the reason behind the creation of your ticket, "
                                                "the bot will ask you to give your milestone that you achieved along with proof of this feat."
                                                "Once that's done, staff will review your milestone and if it is accepted, "
                                                "it will be included in the following Sunday's milestone post!", color=0x8368ff)
    await ctx.send(embed=embed)
    await ctx.send(embed=embed2)

@client.command()
async def deltest(ctx,msgid):
    try:
        print(type(msgid))
        msg = await ctx.fetch_message(msgid)
        await msg.delete()
    except Exception as e:
        print(e)

@client.command()
async def abc(ctx):
    message = await ctx.send('kjsdnas')
    print(message.id)

client.run(configFile['Token'])
