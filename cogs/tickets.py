import asyncio
import io

import aiohttp
import chat_exporter
import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, Select, SelectOption

from cogs.utils import utilities as utils


class Tickets(commands.Cog, name="Tickets"):
    def __init__(self, bot):
        self.bot = bot

    # Ticket Handling
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if channel.category.name == "RTickets":
            while True:
                embed = discord.Embed(
                    title="Do you wish to join Miscellaneous in-game?",
                    color=0x8368ff)
                yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                no = Button(style=ButtonStyle.red, label="No", id="no")

                await channel.send(embed=embed, components=[[yes, no]])

                click = await self.bot.wait_for("button_click")
                author = self.bot.guild.get_member(int(click.user.id))
                name = await utils.name_grabber(author)
                if click.component.id == "yes":
                    await channel.edit(name=f"join-request-{name}")
                    await channel.purge(limit=10)
                    embed = discord.Embed(title=f"{name} wishes to join Miscellaneous", description="Please wait until staff get in contact with you.\n\n"
                                                                                                    "You are recommended to leave your present guild (if any) so that staff can invite you to Miscellaneous ASAP\n\n"
                                                                                                    "If you get in the guild and want the member role in the discord, use \n,sync `Your Minecraft Name`",
                                          color=0x8368ff)
                    embed.add_field(name="Miscellaneous Guild Requirements",
                                    value=f"**Active**\n•  {format(self.bot.active, ',d')} Weekly Guild Experience\n\n"
                                          f"**Do Not Kick List Eligibility**\n•  {format(self.bot.dnkl, ',d')} Weekly Guild Experience\n\n"
                                          f"**Resident**\n•  {format(self.bot.resident_req, ',d')} Weekly Guild Experience\n\n"
                                          f"**Member**\n•  {format(self.bot.inactive, ',d')} Weekly Guild Experience\n\n"
                                          f"**New Member**\n•  {format(self.bot.new_member, ',d')} Daily Guild Experience")
                    embed.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                                          "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")

                    await channel.send(embed=embed)
                    break
                elif click.component.id == "no":
                    await channel.purge(limit=10)
                    embed = discord.Embed(title="Why did you join the Miscellaneous Discord?",
                                          description="Please select your reason from the dropdown list below!",
                                          color=0x8368ff)
                    success_ticket = discord.Embed(title="Success!",
                                                   color=0x00A86B)

                    await click.respond(embed=success_ticket)
                    await channel.send(
                        embed=embed,
                        components=[
                            [
                                Select(placeholder="Select max 1!", options=[
                                    SelectOption(label="Alliance/Partner Request", value="Alliance",
                                                 emoji="🤝"),
                                    SelectOption(label="GvG Request", value="GvG",
                                                 emoji="⚔️"),
                                    SelectOption(label="Exploring/You have friends here", value="Exploring",
                                                 emoji="🌏"),
                                    SelectOption(label="Other", value="Other", emoji="❓")
                                ], max_values=1, min_values=0)
                            ]
                        ]
                    )
                    interaction = await self.bot.wait_for("select_option")
                    response_embed = discord.Embed(title="Ticket Reason Selected!", color=0x00A86B)
                    response_embed.set_footer(text=interaction.values[0])
                    await interaction.respond(embed=response_embed)  # interaction.values is a list
                    reply = interaction.values[0]

                    if reply == "Alliance":
                        embed = discord.Embed(title=f"Alliance/Partner Request - {name}",
                                              color=0x8368ff)
                        await channel.purge(limit=10)
                        await channel.send(embed=embed)
                        guildname_embed = discord.Embed(title="What is the name of your guild?",
                                                        description="Please reply with the name of your guild!",
                                                        color=0x8368ff)
                        embed.set_footer(text="If you aren't a guild that's looking to ally, reply with None")
                        await channel.send(embed=guildname_embed)
                        guildname = await self.bot.wait_for('message',
                                                            check=lambda x: x.author == author and x.channel == channel)
                        guildname = guildname.content
                        if guildname in ('None', 'none'):
                            guildname_embed = discord.Embed(title="What is the name of your Organization?",
                                                            description="Please reply with the name of your Organization!",
                                                            color=0x8368ff)
                            await channel.send(embed=guildname_embed)
                            guildname = await self.bot.wait_for('message', check=lambda
                                x: x.author == author and x.channel == channel)
                            guildname = guildname.content

                            await channel.edit(name=f"Partner-{guildname.replace(' ', '-')}")

                            position_embed = discord.Embed(title=f"What is your position in {guildname}?",
                                                           description="Staff Position\nExample:\n Admin, Moderator, Co-Owner, Guild Master etc.",
                                                           color=0x8368ff)
                            await channel.send(embed=position_embed)
                            position = await self.bot.wait_for('message', check=lambda
                                x: x.author == author and x.channel == channel)
                            position = position.content

                            embed = discord.Embed(title=f"Partner Request from {guildname} (Organization)",
                                                  description="The application process has concluded. Please wait for staff assistance.",
                                                  color=0x8368ff)
                            embed.set_footer(text=f"Position of Applicant: **{position}**")
                            await channel.send(embed=embed)
                            break

                        await channel.edit(name=f"Alliance-{guildname.replace(' ', '-')}")
                        guild_planke = f"https://plancke.io/hypixel/guild/name/{guildname.replace(' ', '%20')}"
                        api = utils.get_api()
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                    f'https://api.hypixel.net/guild?key={api}&name={guildname.replace(" ", "%20")}') as resp:
                                req = await resp.json(content_type=None)
                                await session.close()
                        level = await utils.get_guild_level(req['guild']['exp'])
                        if level > 100:
                            position_embed = discord.Embed(title=f"What is your position in {guildname}?",
                                                           description="Staff Position\nExample:\n Admin, Moderator, Co-Owner, Guild Master etc.",
                                                           color=0x8368ff)
                            await channel.send(embed=position_embed)
                            position = await self.bot.wait_for('message', check=lambda
                                x: x.author == author and x.channel == channel)
                            position = position.content
                            embed = discord.Embed(title=f"Partner Request from {guildname} (Organization)",
                                                  description="The application process has concluded. Please wait for staff assistance.",
                                                  color=0x8368ff)
                            embed.set_footer(text=f"Position of Applicant: **{position}**")
                            embed.add_field(name="Level:", value=level, inline=True)
                            await channel.send(embed=embed)
                            break
                        else:
                            failure_embed = discord.Embed(
                                title="Sorry! Your guild doesn't meet the minimum requirement of being level 100!",
                                description="If you wish to change our mind, you can convey your message through this ticket.\n"
                                            "If you made a mistake, click restart.",
                                color=0x8368ff)
                            failure_embed.set_footer(text="If you wish to join the discord, press restart!")
                            restart = Button(style=ButtonStyle.grey, label="Restart", id="restart")

                            await channel.send(embed=failure_embed, components=[restart])

                            click = await self.bot.wait_for("button_click")
                            if click.component.id == "restart":
                                embed = discord.Embed(title="Great! Restarting the ticketing process!",
                                                      color=0x00A86B)
                                await click.respond(embed=embed)
                    elif reply == "GvG":
                        embed = discord.Embed(title=f"GvG Request - {name}",
                                              color=0x8368ff)
                        await channel.purge(limit=10)
                        await channel.send(embed=embed)
                        guildname_embed = discord.Embed(title="What is the name of your guild?",
                                                        description="Please reply with the name of your guild!",
                                                        color=0x8368ff)
                        await channel.send(embed=guildname_embed)
                        guildname = await self.bot.wait_for('message',
                                                            check=lambda x: x.author == author and x.channel == channel)
                        guildname = guildname.content
                        await channel.edit(name=f"Gvg-Request-{guildname.replace(' ', '-')}")
                        guild_planke = f"https://plancke.io/hypixel/guild/name/{guildname.replace(' ', '%20')}"
                        api = utils.get_api()
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                    f'https://api.hypixel.net/guild?key={api}&name={guildname.replace(" ", "%20")}') as resp:
                                req = await resp.json(content_type=None)
                                await session.close()
                        level = await utils.get_guild_level(req['guild']['exp'])
                        if level > 50:
                            position_embed = discord.Embed(title=f"What is your position in {guildname}?",
                                                           description="Staff Position\nExample:\n Admin, Moderator, Co-Owner, Guild Master etc.",
                                                           color=0x8368ff)
                            await channel.send(embed=position_embed)
                            position = await self.bot.wait_for('message', check=lambda
                                x: x.author == author and x.channel == channel)
                            position = position.content
                            embed = discord.Embed(title=f"Partner Request from {guildname} (Organization)",
                                                  description="The application process has concluded. Please wait for staff assistance.",
                                                  color=0x8368ff)
                            embed.set_footer(text=f"Position of Applicant: **{position}**")
                            embed.add_field(name="Level:", value=level, inline=True)
                            await channel.send(embed=embed)
                            break
                        else:
                            failure_embed = discord.Embed(
                                title="Sorry! Your guild doesn't meet the minimum requirement of being level 50!",
                                description="If you wish to change our mind, you can convey your message through this ticket.\n"
                                            "If you made a mistake, click restart.",
                                color=0x8368ff)
                            failure_embed.set_footer(text="If you wish to join the discord, press restart!")
                            restart = Button(style=ButtonStyle.grey, label="Restart", id="restart")

                            await channel.send(embed=failure_embed, components=[restart])

                            click = await self.bot.wait_for("button_click")
                            if click.component.id == "restart":
                                embed = discord.Embed(title="Great! Restarting the ticketing process!",
                                                      color=0x00A86B)
                                await click.respond(embed=embed)
                    elif reply == "Exploring":
                        await channel.edit(name=f"Guest-{name}")
                        embed = discord.Embed(title=f"{name} wishes to join the Miscellaneous Discord as a Guest",
                                              description="Kindly await staff assistance!\n\n"
                                                          "Staff, if you wish to let them in, hit approve, else, hit deny.",
                                              color=0x8368ff)
                        approve = Button(style=ButtonStyle.blue, label="Approve", id="approve")
                        deny = Button(style=ButtonStyle.red, label="Deny", id="deny")

                        await channel.purge(limit=10)
                        await channel.send(embed=embed, components=[[approve, deny]])
                        while True:
                            click = await self.bot.wait_for("button_click", check=lambda x: x.channel == channel and self.bot.staff in x.author.roles)
                            if click.component.id == "approve":
                                await author.add_roles(self.bot.guest, reason="Registration")
                                await author.remove_roles(self.bot.awaiting_app, self.bot.new_member_role,
                                                          reason="Registration")
                                success_embed = discord.Embed(title="Success", color=0x00A86B)
                                await click.respond(embed=success_embed)

                                embed = discord.Embed(title=f"{author}, welcome to the Miscellaneous discord!",
                                                      description="If you have any queries, you ask ask them in this ticket!\n"
                                                                  "If you don't and wish to close this ticket, click `Close Ticket`",
                                                      color=0x8368ff)

                                yes = Button(style=ButtonStyle.blue, label="Close Ticket", id="yes")
                                no = Button(style=ButtonStyle.red, label="Don't Close", id="no")
                                await channel.purge(limit=10)

                                await channel.send(embed=embed, components=[[yes, no]])

                                click = await self.bot.wait_for("button_click",
                                                                check=lambda x: (
                                                                                        x.author == author and x.channel == channel) or (
                                                                                        self.bot.staff in (
                                                                                    self.bot.guild.get_member(
                                                                                        x.author.id).roles) and x.channel == channel))

                                if click.component.id == "yes":
                                    success_embed = discord.Embed(title="Success", color=0x00A86B)
                                    await click.respond(embed=success_embed)
                                    transcript = await chat_exporter.export(channel)
                                    if transcript is None:
                                        pass
                                    else:
                                        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                                       filename=f"deleted-{channel.name}.html")

                                    if channel.category.name in self.bot.ticket_categories:
                                        name = channel.name
                                        embed = discord.Embed(title='This registration ticket will be deleted in 10 seconds!',
                                                              description='',
                                                              color=0xDE3163)
                                        msg = await channel.send(embed=embed)
                                        await asyncio.sleep(10)
                                        await discord.TextChannel.delete(channel)

                                        name = await utils.name_grabber(author)
                                        embed = discord.Embed(title=f'{channel.name} was deleted by {name}',
                                                              description="They deleted their own ticket.",
                                                              color=0x8368ff)
                                        await self.bot.log_channel.send(embed=embed)
                                        '''await self.bot.log_channel.send(file=discord.File(transcript_file))'''
                                        break
                                elif click.component.id == "no":
                                    success_embed = discord.Embed(title="Success", color=0x00A86B)
                                    await click.respond(embed=success_embed)
                                    embed = discord.Embed(title="The ticket will not be closed. ",
                                                          description="Kindly await staff assistance!", color=0xde3163)
                                    await channel.send(embed=embed)
                                    break
                                break
                            elif click.component.id == "deny":
                                await channel.purge(limit=10)
                                embed = discord.Embed(title = "Entry Denied!",
                                                        description = "Your entry to the server has been denied!",
                                                        color = 0xDE3163)
                                await channel.send(embed=embed)
                                success_embed = discord.Embed(title="Success",
                                                              description="Please specify why you denied entry to this member!",
                                                              color=0x00A86B)
                                await click.respond(embed=success_embed)
                                break
                        break
                    elif reply == "Other":
                        embed = discord.Embed(title=f"Other - {name}",
                                              color=0x8368ff)
                        await channel.purge(limit=10)
                        await channel.send(embed=embed)
                        embed = discord.Embed(
                            title="Alright! Kindly specify why you joined the discord and await staff assistance!",
                            color=0x8368ff)
                        await channel.send(embed=embed)
                        break
                    else:
                        await channel.purge(limit=10)
                        mistake = discord.Embed(
                            title="Did you make a mistake while specifying why you joined Miscellaneous?",
                            description="Click `Yes` if you did. This will restart the registration process.\n Click `No` if you didn't make a mistake and wish to wait for staff assistance.",
                            color=0x8368ff)
                        yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                        no = Button(style=ButtonStyle.red, label="No", id="no")

                        await channel.send(embed=mistake, components=[[yes, no]])

                        while True:
                            click = await self.bot.wait_for("button_click",
                                                            check=lambda x: (
                                                                                    x.author == author and x.channel == channel) or (
                                                                                    self.bot.staff in x.author.roles and x.channel == channel))

                            if click.component.id == "yes":
                                embed = discord.Embed(title="Great! Restarting the registration process!",
                                                      color=0x00A86B)
                                await click.respond(embed=embed)
                            elif click.component.id == "no":
                                embed = discord.Embed(
                                    title="Alright, kindly specify why you joined and then await staff assistance!",
                                    color=0x00A86B)
                                await click.respond(embed=embed)
                                break
        elif channel.category.name == '🎫 Ticket Section' and 'giveaway-winner' not in channel.name:
            while True:
                await asyncio.sleep(3)
                ticket_embed = discord.Embed(title="What did you make this ticket?",
                                             description="Please select your reason from the dropdown given below!",
                                             color=0x8368ff)
                ticket_embed.set_footer(text="You can see more reasons if you scroll!")
                await channel.send(
                    embed=ticket_embed,
                    components=[
                        [
                            Select(placeholder="Select your reason!", options=[
                                SelectOption(label="Christmas Event", value="Christmas Event", emoji="🎅"),
                                SelectOption(label="Update your Role/Username/Tag", value="Discord Nick Change",
                                             emoji="👨"),
                                SelectOption(label="Register a Milestone", value="Milestone Registration", emoji="🏆"),
                                SelectOption(label="Apply for the Do-Not-Kick-List",
                                             value="Do not kick list application",
                                             emoji=self.bot.get_emoji(877657298703634483)),
                                SelectOption(label="Report a player", value="Player Report", emoji="🗒️"),
                                SelectOption(label="Query/Problem", value="Query/Problem", emoji="🤔"),
                                SelectOption(label="Apply for staff", value="Staff Application", emoji="🤵"),
                                SelectOption(label="Apply for the GvG Team", value="Gvg Application", emoji="⚔️"),
                                SelectOption(label="Other", value="Other", emoji="❓")
                            ], max_values=1, min_values=0)
                        ]
                    ]
                )
                interaction = await self.bot.wait_for("select_option", check=lambda
                    x: x.channel == channel)
                author = self.bot.guild.get_member(int(interaction.user.id))
                response_embed = discord.Embed(title="Ticket Reason Selected!", color=0x00A86B)
                response_embed.set_footer(text=interaction.values[0])
                await channel.send(embed=response_embed)
                await interaction.respond(content="Great! Now answer the bot's prompts!")  # interaction.values is a list
                reply = interaction.values[0]

                author = self.bot.guild.get_member(int(interaction.user.id))
                name = await utils.name_grabber(author)

                if reply == "Do not kick list application":


                    await channel.edit(name=f"DNKL-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="DNKL"))
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                            request = await resp.json(content_type=None)
                        if resp.status != 200:
                            await channel.send('Unknown IGN!')
                        await session.close()

                    name = request['name']
                    uuid = request['id']
                    api = utils.get_api()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}') as resp:
                            data = await resp.json(content_type=None)
                            await session.close()
                    if data['guild'] != None:
                        gname = data['guild']['name']
                        if gname != 'Miscellaneous':
                            await channel.purge(limit=10)
                            embed = discord.Embed(title='DNKL Request Failed!',
                                                  descrption='To apply for the do-not-kick-list, you must be in Miscellaneous!', color=0xDE3163)
                            await channel.send(embed=embed)
                        else:
                            for member in data["guild"]["members"]:
                                if uuid == member["uuid"]:
                                    await channel.purge(limit=10)
                                    totalexp = member['expHistory']
                                    totalexp = int(sum(totalexp.values()))
                                    if totalexp >= self.bot.dnkl:
                                        eligiblity = True
                                        footer_text = f"{name} meets the DNKL Requirements!"
                                    else:
                                        eligiblity = False
                                        footer_text = f"{name} doesn't meet the DNKL Requirements!"
                                    totalexp = (format(totalexp, ',d'))
                                    if eligiblity is False:
                                        embed = discord.Embed(title=f"{name} wishes to apply for the do-not-kick-list!",
                                                              description="They **DO NOT MEET** the requirements!",
                                                              url=f'https://minotar.net/helm/{uuid}/512.png',
                                                              color=0xDE3163)
                                        embed.set_thumbnail(
                                            url=f'https://minotar.net/helm/{uuid}/512.png')
                                        embed.set_author(name="Do-not-kick-list: Ineligible")
                                        embed.set_footer(text="Even though you do not meet the requirements,"
                                                              " you might still be accepted so we shall proceed with the application process!")
                                        embed.add_field(name="You are not eligible to apply for the do not kick list.",
                                                        value=f"You need a minimum of {format(self.bot.dnkl, ',d')} weekly guild experience."
                                                              f"\n You have {totalexp} weekly guild experience.",
                                                        inline=True),
                                        await channel.send(embed=embed)
                                    if eligiblity is True:
                                        embed = discord.Embed(title=f"{name} wishes to apply for the do-not-kick-list!",
                                                              description="They **MEET** the requirements!",
                                                              url=f'https://minotar.net/helm/{uuid}/512.png',
                                                              color=0x333cff)
                                        embed.set_thumbnail(
                                            url=f'https://minotar.net/helm/{uuid}/512.png')
                                        embed.set_author(name='Do-not-kick-list: Eligible')
                                        embed.add_field(name="You are eligible to apply for the do not kick list.",
                                                        value=f"You meet the minimum of {format(self.bot.dnkl, ',d')} weekly guild experience."
                                                              f"\n You have {totalexp} weekly guild experience.",
                                                        inline=True)
                                        await channel.send(embed=embed)

                                    embed = discord.Embed(title="When will your inactivity begin? (Start date)",
                                                          description="DD/MM/YYYY",
                                                          color=0x8368ff)
                                    embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                                    await channel.send(embed=embed)
                                    start = await self.bot.wait_for('message',
                                                                    check=lambda
                                                                        x: x.author == author and x.channel == channel)
                                    start = start.content
                                    embed = discord.Embed(title="When will your inactivity end? (End date)",
                                                          description="DD/MM/YYYY",
                                                          color=0x8368ff)
                                    embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                                    await channel.send(embed=embed)
                                    end = await self.bot.wait_for('message',
                                                                  check=lambda
                                                                      x: x.author == author and x.channel == channel)
                                    end = end.content
                                    embed = discord.Embed(title="What's the reason behind your inactivity?",
                                                          color=0x8368ff)
                                    await channel.send(embed=embed)
                                    reason = await self.bot.wait_for('message',
                                                                     check=lambda
                                                                         x: x.author == author and x.channel == channel)
                                    reason = reason.content

                                    if int(start.split('/')[1]) > 12:
                                        newdate = f'{start.split("/")[1]}/{start.split("/")[0]}/{start.split("/")[2]}'
                                        start = newdate
                                        await channel.send(
                                            "You entered the start date incorrectly. This was automatically corrected.")
                                    if int(end.split('/')[1]) > 12:
                                        newdate = f'{end.split("/")[1]}/{end.split("/")[0]}/{end.split("/")[2]}'
                                        end = newdate
                                        await channel.send(
                                            "You entered the end date incorrectly. This was automatically corrected.")

                                    a, b, c = start.split('/')
                                    p, q, r = end.split('/')
                                    ign, uuid = await utils.get_dispnameID(name)
                                    rank = await utils.get_rank(name)
                                    dates = {1: "January", 2: "February", 3: "March", 4: "April",
                                             5: "May",
                                             6: "June", 7: "July", 8: "August", 9: "September",
                                             10: "October", 11: "November", 12: "December"}
                                    start_month = dates.get(int(b))
                                    end_month = dates.get(int(q))

                                    dnkl_staff_embed = discord.Embed(title=f"{rank} {ign}",
                                                          url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                                          color=0x0ffff)
                                    dnkl_staff_embed.set_thumbnail(
                                        url=f'https://crafatar.com/renders/body/{uuid}')
                                    dnkl_staff_embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                                    dnkl_staff_embed.add_field(name="Start:", value=f"{a} {start_month} {c}",
                                                    inline=False)
                                    dnkl_staff_embed.add_field(name="End:", value=f"{p} {end_month} {r}",
                                                    inline=False)
                                    dnkl_staff_embed.add_field(name="Reason", value=f"{reason}", inline=False)
                                    dnkl_staff_embed.set_author(name="Do not kick list")
                                    dnkl_embed = dnkl_staff_embed
                                    dnkl_staff_embed.set_footer(text=footer_text)
                                    await channel.send(embed=dnkl_staff_embed)


                                    dnkl_decision = discord.Embed(
                                        title="Staff, what do you wish to do with this dnkl request?",
                                        description=f"\nClick `Approve` to approve the do-not-kick-list request"
                                                    f"\nClick `Deny` to deny the do-not-kick-list request"
                                                    f"\nClick `Error` if the user made an error while applying for the do not kick list",
                                        color=0x8368ff)
                                    dnkl_decision.set_footer(text="This embed is for the Miscellaneous staff team!\n"
                                                                  "Please wait for the Miscellaneous staff team to respond!")
                                    approve = Button(style=ButtonStyle.blue, label="Approve", id="approve")
                                    deny = Button(style=ButtonStyle.red, label="Deny", id="deny")
                                    error = Button(style=ButtonStyle.grey, label="Error", id="error")

                                    await channel.send(embed=dnkl_decision, components=[[approve, deny], [error]])

                                    click = await self.bot.wait_for("button_click",
                                                                    check=lambda x: x.channel == channel and (
                                                                            self.bot.staff in self.bot.guild.get_member(
                                                                        x.author.id).roles or self.bot.helper in self.bot.guild.get_member(
                                                                        x.author.id).roles))

                                    if click.component.id == "approve":
                                        dnkl_staff_embed.set_footer(text="")
                                        message = await self.bot.dnkl_channel.send(embed=dnkl_embed)

                                        cursor = await self.bot.db.execute("SELECT message_id FROM DNKL WHERE username = (?)", (ign,))
                                        row = await cursor.fetchone()
                                        await cursor.close()

                                        if row == None:
                                            await self.bot.db.execute("INSERT INTO DNKL VALUES (?, ?)", (message.id, ign,))
                                        else:
                                            await self.bot.db.execute("UPDATE DNKL SET message_id = (?) WHERE username = (?)", (message.id, ign,))
                                        await self.bot.db.commit()
                                        
                                        embed = discord.Embed(title="This DNKL Application has been accepted!",
                                                              description="The DNKL Embed has been sent to <#629564802812870657>",
                                                              color=0x00A86B)
                                        await channel.send(embed=embed)
                                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                                        await click.respond(embed=success_embed)
                                        break
                                    elif click.component.id == "deny":
                                        if eligiblity is False:
                                            description = "Your DNKL request was denied because of your inability to meet the guild requirements!"
                                        else:
                                            description = None
                                        embed = discord.Embed(title="This do not kick list request has been denied",
                                                              description=description,
                                                              color=0xDE3163)
                                        await channel.send(embed=embed)
                                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                                        await click.respond(embed=success_embed)
                                        break

                                    elif click.component.id == "error":
                                        embed = discord.Embed(title="What is their username?",
                                                              color=0x8368ff)
                                        await channel.send(embed=embed)

                                        name = await self.bot.wait_for('message', check=lambda
                                            x: x.channel == channel)
                                        name = name.content
                                        async with aiohttp.ClientSession() as session:
                                            async with session.get(
                                                    f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                                                request = await resp.json(content_type=None)
                                                ign = request['name']
                                                uuid = request['id']
                                                rank = await utils.get_rank(name)

                                                if resp.status_code != 200:
                                                    await channel.send('Unknown IGN!')
                                                else:
                                                    embed = discord.Embed(
                                                        title="When will their inactivity begin? (Start date)",
                                                        description="DD/MM/YYYY",
                                                        color=0x8368ff)
                                                    embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                                                    await channel.send(embed=embed)
                                                    start_date = await self.bot.wait_for('message',
                                                                                         check=lambda
                                                                                             x: x.author == author and x.channel == channel)
                                                    start_date = start_date.content
                                                    embed = discord.Embed(
                                                        title="When will their inactivity end? (End date)",
                                                        description="DD/MM/YYYY",
                                                        color=0x8368ff)
                                                    embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                                                    await channel.send(embed=embed)
                                                    end_date = await self.bot.wait_for('message',
                                                                                       check=lambda
                                                                                           x: x.channel == channel)
                                                    end_date = end_date.content
                                                    a, b, c = start_date.split('/')
                                                    p, q, r = end_date.split('/')

                                                    embed = discord.Embed(
                                                        title="What's the reason behind their inactivity?",
                                                        color=0x8368ff)
                                                    reason = await self.bot.wait_for('message',
                                                                                     check=lambda
                                                                                         x: x.channel == channel)
                                                    reason = reason.content

                                                    if int(b) > 12:
                                                        embed = discord.Embed(
                                                            title='Please enter a valid date!',
                                                            description="`DD/MM/YYYY`",
                                                            color=0xff0000)
                                                        await channel.send(embed=embed)
                                                    if int(q) > 12:
                                                        embed = discord.Embed(
                                                            title='Please enter a valid date!',
                                                            description="`DD/MM/YYYY`",
                                                            color=0xff0000)
                                                        await channel.send(embed=embed)
                                                    if int(b) & int(q) <= 12:
                                                        dates = {1: "January", 2: "February", 3: "March",
                                                                 4: "April", 5: "May",
                                                                 6: "June", 7: "July", 8: "August",
                                                                 9: "September",
                                                                 10: "October", 11: "November", 12: "December"}
                                                        start_month = dates.get(int(b))
                                                        end_month = dates.get(int(q))

                                                        embed = discord.Embed(title=f"{rank} {ign}",
                                                                              url=f'https://plancke.io/hypixel/player/stats/{ign}',
                                                                              color=0x0ffff)
                                                        embed.set_thumbnail(
                                                            url=f'https://crafatar.com/renders/body/{uuid}')
                                                        embed.add_field(name="IGN:", value=f"{ign}",
                                                                        inline=False)
                                                        embed.add_field(name="Start:",
                                                                        value=f"{a} {start_month} {c}",
                                                                        inline=False)
                                                        embed.add_field(name="End:",
                                                                        value=f"{p} {end_month} {r}",
                                                                        inline=False)
                                                        embed.add_field(name="Reason", value=f"{reason}",
                                                                        inline=False)
                                                        embed.set_author(name="Do not kick list")
                                                        await channel.purge(limit=1)

                                                        message = await self.bot.dnkl_channel.send(embed=embed)
                                                        
                                                        cursor = await self.bot.db.execute("SELECT message_id FROM DNKL WHERE username = (?)", (ign,))
                                                        row = await cursor.fetchone()
                                                        await cursor.close()

                                                        if row == None:
                                                            await self.bot.db.execute("INSERT INTO DNKL VALUES (?, ?)", (message.id, ign,))
                                                        else:
                                                            await self.bot.db.execute("UPDATE DNKL SET message_id = (?) WHERE username = (?)", (message.id, ign,))
                                                        await self.bot.db.commit()

                                                        await session.close()
                                                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                                                        await click.respond(embed=success_embed)
                                                        break
                    else:
                        await channel.purge(limit=10)
                        embed = discord.Embed(title='DNKL Request Failed!',
                                              descrption='To apply for the do-not-kick-list, you must be in Miscellaneous!',
                                              color=0xDE3163)
                        await channel.send(embed=embed)

                    stop_embed = discord.Embed(title="Can this ticket be closed?",
                                               description="Click `Yes` if you resolved your issue and want to delete the ticket.\n Click `No` if you wish to wait for staff assistance\nClick `Restart` if you wish to restart the ticket process",
                                               color=0x8368ff)
                    yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                    no = Button(style=ButtonStyle.red, label="No", id="no")
                    restart = Button(style=ButtonStyle.grey, label="Restart", id="restart")

                    await channel.send(embed=stop_embed, components=[[yes, no], [restart]])

                    click = await self.bot.wait_for("button_click",
                                                    check=lambda x: (
                                                                            x.author == author and x.channel == channel) or (
                                                                            self.bot.staff in (
                                                                        self.bot.guild.get_member(
                                                                            x.author.id).roles) and x.channel == channel))

                    if click.component.id == "yes":
                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                        await click.respond(embed=success_embed)
                        transcript = await chat_exporter.export(channel)
                        if transcript is None:
                            pass
                        else:
                            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                           filename=f"deleted-{channel.name}.html")

                        if channel.category.name in self.bot.ticket_categories:
                            embed = discord.Embed(title='This ticket will be deleted in 10 seconds!',
                                                  description='',
                                                  color=0xDE3163)
                            await channel.send(embed=embed)
                            await asyncio.sleep(10)
                            await discord.TextChannel.delete(channel)

                            name = await utils.name_grabber(author)
                            embed = discord.Embed(title=f'{channel.name} was deleted by {name}',
                                                  description="They deleted their own ticket.", color=0x8368ff)
                            await self.bot.log_channel.send(embed=embed)
                            await self.bot.log_channel.send(file=discord.File(transcript_file))
                            break
                    elif click.component.id == "no":
                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                        await click.respond(embed=success_embed)
                        embed = discord.Embed(title="The ticket will not be closed. ",
                                              description="Kindly await staff assistance!", color=0xde3163)
                        await channel.send(embed=embed)
                        break
                    elif click.component.id == "restart":
                        embed = discord.Embed(title="Restarting",
                                              description="The ticket process will restart in 5 seconds!",
                                              color=0x00a86b)
                        await asyncio.sleep(2)
                elif reply == "Discord Nick Change":
                    await channel.edit(name=f"Role/Name/Tag-change-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    embed = discord.Embed(tile=f"{name} wishes to change their Role/Name/Tag",
                                        description="Please proceed by answering the bot's prompts!",
                                        color=0x8368ff)
                    await channel.purge(limit=10)
                    await channel.send(embed=embed)
                    embed = discord.Embed(title="What is your Minecraft username?",
                                          color=0x8368ff)
                    await channel.send(embed=embed)
                    role_reply = await self.bot.wait_for('message',
                                                         check=lambda x: x.channel == channel and x.author == author)
                    name = role_reply.content
                    ign, uuid = await utils.get_dispnameID(name)
                    if ign is None:
                        embed = discord.Embed(title="Please enter a valid minecraft username!",
                                              description="The ticket process will be restarted so you can rectify your mistake!",
                                              color=0xDE3163)
                        await channel.send(embed=embed)
                    elif ign in self.bot.staff_names and self.bot.staff not in author.roles:
                        embed = discord.Embed(title="Staff impersonation is a punishable offense!",
                                              description="The ticket process will be restarted!",
                                              color=0xDE3163)
                        await channel.send(embed=embed)
                    else:
                        guild_name = await utils.get_guild(ign)
                        await author.edit(nick=ign)
                        has_tag_perms = any(role in author.roles for role in self.bot.tag_allowed_roles)

                        if guild_name == "Miscellaneous" or has_tag_perms is True:
                            if has_tag_perms is True:
                                while True:
                                    embed = await utils.get_tag_message()
                                    await channel.send(embed=embed)
                                    tag = await self.bot.wait_for('message',
                                                                    check=lambda
                                                                        x: x.channel == channel and x.author == author)
                                    tag = tag.content
                                    tag_check_success, tag_check_reason = await utils.check_tag(tag)

                                    if tag_check_success:
                                        new_nick = ign + f' [{tag}]'
                                        await author.edit(nick=new_nick)
                                        break
                                    else:
                                        await channel.send(tag_check_reason)

                            await author.add_roles(self.bot.member_role, reason="Ticket Sync")
                            embed = discord.Embed(title="Your nick and role was successfully changed!",
                                                  description="await staff assistance.",
                                                  color=0x8368ff)
                            embed.set_footer(text="Member of Miscellaneous"
                                                  "\n• Guest & Awaiting Approval were removed"
                                                  "\n• Member was given")
                            embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')

                            await channel.send(embed=embed)
                        elif guild_name in self.bot.misc_allies:
                            for guild in self.bot.misc_allies:
                                if guild == guild_name:
                                    gtag = await utils.get_gtag(guild)
                                    if author.nick is None or str(gtag) not in author.nick:
                                        new_nick = ign + " " + str(gtag)
                                        await author.edit(nick=new_nick)

                                    await author.remove_roles(self.bot.new_member_role, self.bot.awaiting_app,
                                                              self.bot.member_role, reason="Ticket Sync")
                                    await author.add_roles(self.bot.guest, self.bot.ally, reason="Ticket Sync")

                                    embed = discord.Embed(title="Your nick, role and tag were successfully changed!",
                                                          description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                                          color=0x8368ff)
                                    embed.set_footer(
                                        text=f"Member of {guild}\n• Nick & Tag Changed\n• Member & Awaiting Approval were removed\n• Guest and Ally were given")
                                    embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')
                                    await channel.send(embed=embed)

                        elif guild_name != "Miscellaneous" and guild_name not in self.bot.misc_allies:
                            if str(channel.category.name) == "RTickets":
                                await channel.send(
                                    "You aren't in Miscellaneous in-game. Kindly await staff assistance!")
                            else:
                                await author.remove_roles(self.bot.member_role, self.bot.awaiting_app,
                                                          reason="Ticket Sync")
                                await author.add_roles(self.bot.guest, reason="Ticket Sync")
                                embed = discord.Embed(title="Your nick and role was successfully changed!",
                                                      description="If this wasn't the change you anticipated, "
                                                                  "await staff assistance.",
                                                      color=0x8368ff)
                                embed.set_footer(text=f"Member of {guild_name}"
                                                      f"\n• Member & Awaiting Approval were removed"
                                                      f"\n• Guest was given")
                                embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')
                                await channel.send(embed=embed)

                    stop_embed = discord.Embed(title="Can this ticket be closed?",
                                               description="Click `Yes` if you resolved your issue and want to delete the ticket.\n Click `No` if you wish to wait for staff assistance\nClick `Restart` if you wish to restart the ticket process",
                                               color=0x8368ff)
                    yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                    no = Button(style=ButtonStyle.red, label="No", id="no")
                    restart = Button(style=ButtonStyle.grey, label="Restart", id="restart")

                    await channel.send(embed=stop_embed, components=[[yes, no], [restart]])

                    click = await self.bot.wait_for("button_click",
                                                    check=lambda x: (
                                                                            x.author == author and x.channel == channel) or (
                                                                            self.bot.staff in x.author.roles and x.channel == channel))

                    if click.component.id == "yes":
                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                        await click.respond(embed=success_embed)
                        transcript = await chat_exporter.export(channel)
                        if transcript is None:
                            pass
                        else:
                            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                           filename=f"deleted-{channel.name}.html")

                        if channel.category.name in self.bot.ticket_categories:
                            embed = discord.Embed(title='This ticket will be deleted in 10 seconds!',
                                                  description='',
                                                  color=0xDE3163)
                            await channel.send(embed=embed)
                            await asyncio.sleep(10)
                            await discord.TextChannel.delete(channel)

                            name = await utils.name_grabber(author)
                            embed = discord.Embed(title=f'{channel.name} was deleted by {name}',
                                                  description="They deleted their own ticket.", color=0x8368ff)
                            await self.bot.log_channel.send(embed=embed)
                            await self.bot.log_channel.send(file=discord.File(transcript_file))
                            break
                    elif click.component.id == "no":
                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                        await click.respond(embed=success_embed)
                        embed = discord.Embed(title="The ticket will not be closed. ",
                                              description="Kindly await staff assistance!", color=0xde3163)
                        await channel.send(embed=embed)
                        break
                    elif click.component.id == "restart":
                        embed = discord.Embed(title="Restarting",
                                              description="The ticket process will restart in 5 seconds!",
                                              color=0x00a86b)
                        await asyncio.sleep(2)
                elif reply == "Player Report":
                    embed = discord.Embed(title=f"{name} wishes to file a player report!",
                                          description="You are expected to provide maximum detail about the offense.\n"
                                                      "Following is considered the bare minimum:\n"
                                                      "> Username of the accused\n"
                                                      "> Explanation of the offense\n"
                                                      "> Time of offense\n"
                                                      "> Proof of offense\n"
                                                      "If you wish to report a staff member, DM <@!326399363943497728>",
                                          color=0x8368ff)
                    await channel.purge(limit=10)
                    await channel.send(embed=embed)
                    await channel.edit(name=f"Report-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="REPORTS"))
                    break
                elif reply == "Query/Problem":
                    embed = discord.Embed(title=f"{name} has query/problem",
                                          description="Please elaborate on your problem/query so that the staff team can help you out!",
                                          color=0x8368ff)
                    await channel.purge(limit=10)
                    await channel.send(embed=embed)
                    await channel.edit(name=f"General-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    break
                elif reply == "Milestone Registration":
                    embed = discord.Embed(title=f"{name} would like to register a milestone!",
                                          description="Kindly provide a screenshot followed by a message specifying your milestone!\n"
                                                      "If your milestone is approved, you will be included in the following sunday's milestone post!",
                                          color=0x8368ff)
                    await channel.purge(limit=10)
                    await channel.send(embed=embed)
                    await channel.edit(name=f"Milestone-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="MILESTONES"))
                    break
                elif reply == "Staff Application":
                    req_embed = discord.Embed(title=f"{name} wishes to apply for staff!",
                                          description="Please respond to the bot's prompts appropriately!",
                                          color=0x4b89e4)
                    req_embed.add_field(name="Do you meet the following requirements?",
                                        value="• You must be older than 13 years."
                                              "\n• You must have enough knowledge about the bots in this Discord."
                                              "\n• You must be active both on Hypixel and in the guild Discord."
                                              "\n• You must have a good reputation amongst guild members.",
                                        inline=False)
                    await channel.purge(limit=10)


                    yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                    no = Button(style=ButtonStyle.red, label="No", id="no")

                    await channel.send(embed=req_embed, components=[[yes, no]])

                    click = await self.bot.wait_for("button_click",
                                                    check=lambda x: (
                                                                            x.author == author and x.channel == channel) or (
                                                                            self.bot.staff in x.author.roles and x.channel == channel))

                    if click.component.id == "no":
                        await click.respond(content=f"Alright let's proceed!")
                        stop_embed = discord.Embed(
                            title="Since you don't meet the requirements, can this ticket be closed?",
                            description="Click `Yes` if you wish to delete the ticket.\n Click `No` if you wish to wait for staff assistance\nClick `Restart` if you wish to restart the ticket process",
                            color=0x8368ff)
                        yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                        no = Button(style=ButtonStyle.red, label="No", id="no")
                        restart = Button(style=ButtonStyle.grey, label="Restart", id="restart")

                        await channel.send(embed=stop_embed, components=[[yes, no], [restart]])

                        click = await self.bot.wait_for("button_click",
                                                        check=lambda x: (
                                                                x.author == author and x.channel == channel))

                        if click.component.id == "yes":
                            success_embed = discord.Embed(title="Success", color=0x00A86B)
                            await click.respond(embed=success_embed)
                            transcript = await chat_exporter.export(channel)
                            if transcript is None:
                                pass
                            else:
                                transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                               filename=f"deleted-{channel.name}.html")

                            if channel.category.name in self.bot.ticket_categories:
                                embed = discord.Embed(title='This ticket will be deleted in 10 seconds!',
                                                      description='',
                                                      color=0xDE3163)
                                await channel.send(embed=embed)
                                await asyncio.sleep(10)
                                await discord.TextChannel.delete(channel)

                                name = await utils.name_grabber(author)
                                embed = discord.Embed(title=f'{channel.name} was deleted by {name}',
                                                      description="They deleted their own ticket.", color=0x8368ff)
                                await self.bot.log_channel.send(embed=embed)
                                await self.bot.log_channel.send(file=discord.File(transcript_file))
                                break
                        elif click.component.id == "no":
                            success_embed = discord.Embed(title="Success", color=0x00A86B)
                            await click.respond(embed=success_embed)
                            embed = discord.Embed(title="The ticket will not be closed. ",
                                                  description="Kindly await staff assistance!", color=0xde3163)
                            await channel.send(embed=embed)
                            break
                        elif click.component.id == "restart":
                            embed = discord.Embed(title="Restarting",
                                                  description="The ticket process will restart in 5 seconds!",
                                                  color=0x00a86b)
                            await click.respond(embed=embed)
                            await asyncio.sleep(2)
                            break

                    if click.component.id == "yes":
                        embed = discord.Embed(title="Does your discord nick match your Minecraft Username?",
                                              color=0x4b89e4)

                        yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                        no = Button(style=ButtonStyle.red, label="No", id="no")

                        await channel.send(embed=embed, components=[[yes, no]])

                        click = await self.bot.wait_for("button_click",
                                                        check=lambda x: (
                                                                x.author == author and x.channel == channel))

                        if click.component.id == 'yes':
                            await click.respond(content=f"Alright let's proceed!")
                            name = await utils.name_grabber(author)
                        else:
                            await click.respond(content=f"Alright let's proceed!")
                            embed = discord.Embed(title="What is your Minecraft Username?",
                                                  color=0x4b89e4)
                            await channel.send(embed=embed)
                            username = await self.bot.wait_for('message',
                                                               check=lambda
                                                                   x: x.channel == channel and x.author == author)
                            name = username.content
                            ign, uuid = await utils.get_dispnameID(name)

                        async with aiohttp.ClientSession() as session:
                            async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                                request = await resp.json(content_type=None)
                                await session.close()
                        uuid = request['id']
                        await channel.edit(name=f"Staff-Application-{name}",
                                           category=discord.utils.get(channel.guild.categories, name="OTHER"))
                        '''AGE'''
                        embed = discord.Embed(title="What is your age?",
                                              description="Kindly reply with a number",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        age = await self.bot.wait_for('message',
                                                      check=lambda x: x.channel == channel and x.author == author)
                        age = age.content

                        '''VETERENCY'''
                        embed = discord.Embed(title="For how long have you been in Miscellaneous?",
                                              description="You can check this through \"/g menu\" ingame",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        veterency = await self.bot.wait_for('message',
                                                            check=lambda x: x.channel == channel and x.author == author)
                        veterency = veterency.content

                        '''PAST INFRACTIONS'''
                        embed = discord.Embed(title="Have you had any past infractions on Hypixel?",
                                              description="Kindly reply with a Yes or No",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        infractions = await self.bot.wait_for('message',
                                                              check=lambda
                                                                  x: x.channel == channel and x.author == author)
                        infractions = infractions.content
                        infractions = infractions.capitalize()

                        embed = discord.Embed(title="Kindly make sure that your answers are as detailed as possible."
                                                    "\nGiving short answers will hinder your chances at getting staff.",
                                              description="When answering, answer in the form of one message. One question, one message!",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        await asyncio.sleep(3)

                        '''------------------------------------------------------Questions------------------------------------------------'''

                        '''WHY STAFF'''
                        embed = discord.Embed(title="Why have you decided to apply for staff?",
                                              description="Please make sure that you respond in one message",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        whystaff = await self.bot.wait_for('message',
                                                           check=lambda x: x.channel == channel and x.author == author)
                        whystaff = whystaff.content

                        '''WHY MISC'''
                        embed = discord.Embed(title="What brought you to Miscellaneous, and what has kept you here?",
                                              description="Please make sure that you respond in one message",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        whymisc = await self.bot.wait_for('message',
                                                          check=lambda x: x.channel == channel and x.author == author)
                        whymisc = whymisc.content

                        '''Suggest'''
                        embed = discord.Embed(
                            title="What is something that you could suggest that could improve the guild?",
                            description="Please make sure that you respond in one message",
                            color=0x4b89e4)
                        await channel.send(embed=embed)
                        suggestion = await self.bot.wait_for('message',
                                                             check=lambda
                                                                 x: x.channel == channel and x.author == author)
                        suggestion = suggestion.content

                        '''SCENARIO 1'''
                        embed = discord.Embed(
                            title="You have just started as a helper and a moderator starts arguing with another member. "
                                  "This argument starts to get serious quite quickly. What do you do? ",
                            description="Make your answer as detailed as possible!",
                            color=0x4b89e4)
                        await channel.send(embed=embed)
                        scen1 = await self.bot.wait_for('message',
                                                        check=lambda x: x.channel == channel and x.author == author)
                        scen1 = scen1.content

                        '''SCENARIO 2'''
                        embed = discord.Embed(
                            title="Suppose it's your first week of being a helper and you guild-mute a well-known player. "
                                  "Your guildmates start spamming you calling you a bad moderator and telling you to unmute them. "
                                  "What would you do?",
                            description="Make your answer as detailed as possible!",
                            color=0x4b89e4)
                        await channel.send(embed=embed)
                        scen2 = await self.bot.wait_for('message',
                                                        check=lambda x: x.channel == channel and x.author == author)
                        scen2 = scen2.content

                        '''SCENARIO 3'''
                        embed = discord.Embed(
                            title="Upon joining a game and you discover that a guild member is in your game and is hacking. "
                                  "What do you do?",
                            description="Please make sure that you respond in one message",
                            color=0x4b89e4)
                        await channel.send(embed=embed)
                        scen3 = await self.bot.wait_for('message',
                                                        check=lambda x: x.channel == channel and x.author == author)
                        scen3 = scen3.content

                        '''STAFF'''
                        embed = discord.Embed(title="Have you been staff in any other guild or on any server? "
                                                    "If yes, which one?",
                                              description="Please make sure that you respond in one message",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        staff = await self.bot.wait_for('message',
                                                        check=lambda x: x.channel == channel and x.author == author)
                        staff = staff.content

                        '''TIME'''
                        embed = discord.Embed(title="How much time do you have to contribute to the role? (Per day)",
                                              description="Please make sure that you respond in one message",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        time_ = await self.bot.wait_for('message',
                                                        check=lambda x: x.channel == channel and x.author == author)
                        time_ = time_.content

                        '''GENERAL QUESTION'''
                        embed = discord.Embed(title="Tell us about a time you made a mistake within the last year. "
                                                    "How did you deal with it? What did you learn?",
                                              escription="Make your answer as detailed as possible!",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        question = await self.bot.wait_for('message',
                                                           check=lambda x: x.channel == channel and x.author == author)
                        question = question.content

                        '''ANYTHING ELSE'''
                        embed = discord.Embed(title="Anything else you would like us to know?",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        random = await self.bot.wait_for('message',
                                                         check=lambda x: x.channel == channel and x.author == author)
                        random = random.content

                        await channel.send("Great! You're done with the application!"
                                           "\nI'm working on compiling the application and I'll send it once I'm done compiling!")

                        embed = discord.Embed(title=f"{name}'s Staff Application", color=0x4b89e4)
                        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
                        embed.add_field(name="1) What is your age?", value=age, inline=False)
                        embed.add_field(name="2) How long have you been in the guild for?", value=veterency,
                                        inline=False)
                        embed.add_field(name="3) Have you had any past infractions on Hypixel?", value=infractions,
                                        inline=False)
                        embed.add_field(name="4) Why have you decided to apply for staff?", value=whystaff,
                                        inline=False)
                        embed.add_field(name="5) What brought you to Miscellaneous, and what has kept you here?",
                                        value=whymisc, inline=False)
                        embed.add_field(name="6) What is something you could suggest that would improve the guild?",
                                        value=suggestion, inline=False)
                        embed.add_field(
                            name="7) You have just started as a helper and a moderator starts arguing with another member. This argument starts to get serious quite quickly. What do you do?",
                            value=scen1, inline=False)
                        embed.add_field(
                            name="8) Suppose it's your first week of being a helper and you guild-mute a well-known player. Your guildmates start spamming you calling you a bad moderator and telling you to unmute them. What would you do?",
                            value=scen2, inline=False)
                        embed.add_field(
                            name="9) Upon joining a game and you discover that a guild member is in your game and is hacking. What do you do?",
                            value=scen3, inline=False)
                        embed.add_field(
                            name="10) Have you been staff in any other guild or on any server? If yes, which one?",
                            value=staff, inline=False)
                        embed.add_field(name="11) How much time do you have to contribute to the role? (Per day)",
                                        value=time_, inline=False)
                        embed.add_field(
                            name="12) Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?",
                            value=question, inline=False)
                        embed.add_field(name="13) Anything else you would us to know?", value=random, inline=False)
                        await channel.send(embed=embed)
                        await channel.send(
                            "If you made any error, make a new ticket, rectify your mistake and copy paste your answer.")
                        break
                elif reply == "Gvg Application":
                    embed = discord.Embed(title=f"{name} wishes to apply for the GvG Team!",
                                          description="To be eligible to apply for the GvG Team, you must meet any one of the following game-specific requirements. "
                                                      "The bot will automatically check if you're eligible for the gvg tem!",
                                          color=0x8368ff)
                    embed.add_field(name="Bedwars",
                                    value="500 Wins\n1.6 Final Kill-Death Ratio",
                                    inline=False)
                    embed.add_field(name="Skywars",
                                    value="1000 Wins\n1.2 Kill-Death Ratio",
                                    inline=False)
                    embed.add_field(name="Duels",
                                    value="2000 Wins\n1.5 Kill-Death Ratio",
                                    inline=False)
                    embed.add_field(name="Polyvalent (All gamemodes)",
                                    value="Must fulfill all requirements",
                                    inline=False)
                    await channel.edit(name=f"GvG-Application-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    await channel.purge(limit=10)
                    await channel.send(embed=embed)

                    req = await utils.get_data(name)
                    if req["player"] is None:
                        embed = discord.Embed(title='Unknown IGN',
                                              description='Kindly create a new ticket to sync your name and then create another ticket for the GvG Application!',
                                              color=0xff0000)
                        await channel.send(embed=embed)
                    else:
                        req = await utils.get_data(name)
                        uuid = req['player']['uuid']
                        x = 0
                        y = 0
                        z = 0
                        # Bedwars
                        bw_list_of_fields=['wins_bedwars','final_kills_bedwars','final_deaths_bedwars']

                        bw_wins=0
                        final_kills_bedwars=1
                        final_deaths_bedwars=2
                        bw_fkdr=3

                        bedwars_stats=[]

                        for field in bw_list_of_fields:
                            try:
                                stat = int(req['player']['stats']['Bedwars'][field])
                            except:
                                stat = 0
                            bedwars_stats.append(stat)
                        if bedwars_stats[final_deaths_bedwars] == 0:
                            bedwars_stats[final_deaths_bedwars] = 1
                        bedwars_stats.append(round((bedwars_stats[final_kills_bedwars]/bedwars_stats[final_deaths_bedwars]), 2))


                        if bedwars_stats[bw_wins] > 500:
                            x = x + 1
                        if bedwars_stats[bw_fkdr] > 1.6:
                            x = x + 1

                        # Skywars
                        sw_list_of_fields = ['wins', 'wins_solo', 'wins_team', 'kills', 'deaths']
                        skywars_stats = []

                        sw_wins_overall = 0
                        sw_wins_solo = 1
                        sw_wins_doubles = 2
                        sw_kills = 3
                        sw_deaths = 4
                        sw_kdr = 5

                        for field in sw_list_of_fields:
                            try:
                                stat = int(req['player']['stats']['SkyWars'][field])
                            except:
                                stat = 0
                            skywars_stats.append(stat)
                        if skywars_stats[sw_deaths] == 0:
                            skywars_stats[sw_deaths]=1
                        skywars_stats.append(round((skywars_stats[sw_kills]/skywars_stats[sw_deaths]), 2))


                        if skywars_stats[sw_wins_overall] > 1000:
                            y = y + 1
                        if skywars_stats[sw_kdr] > 1.2:
                            y = y + 1

                        # Duel
                        duel_list_of_fields = ['wins', 'losses', 'kills']
                        duels_stats = []
                        duels_wins = 0
                        duels_losses = 1
                        duels_kills = 2
                        duels_wlr = 3

                        for field in duel_list_of_fields:
                            try:
                                stat = int(req['player']['stats']['Duels'][field])
                            except:
                                stat = 0
                            duels_stats.append(stat)
                        if duels_stats[duels_losses] == 0:
                            duels_stats[duels_losses] = 1
                        duels_stats.append(round((duels_stats[duels_wins]/duels_stats[duels_losses]), 2))


                        if duels_stats[duels_wins] > 2000:
                            z = z + 1
                        if duels_stats[duels_wlr] > 1.5:
                            z = z + 1

                        if x >= 2 and y >= 2 and z >= 2:
                            embed1 = discord.Embed(title="You're eligible for the Polyvalent GvG Team!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0x8368ff)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bedwars_stats[bw_wins]}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bedwars_stats[bw_fkdr]}`')
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{skywars_stats[sw_wins_overall]}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{skywars_stats[sw_wins_solo]}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{skywars_stats[sw_wins_doubles]}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{skywars_stats[sw_kdr]}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_stats[duels_wins]}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_stats[duels_wlr]}`')
                            await channel.send(embed=embed1)
                            break

                        elif x == 1 and y == 1 and z == 1:
                            embed1 = discord.Embed(
                                title="You're eligible for any two of the teams!\n You will be assigned to any two teams on the basis of your stats!",
                                description="Kindly await staff assistance for further information!",
                                color=0x8368ff)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bedwars_stats[bw_wins]}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bedwars_stats[bw_fkdr]}`')
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{skywars_stats[sw_wins_overall]}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{skywars_stats[sw_wins_solo]}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{skywars_stats[sw_wins_doubles]}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{skywars_stats[sw_kdr]}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_stats[duels_wins]}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_stats[duels_wlr]}`')
                            await channel.send(embed=embed1)
                            break

                        elif x >= 1 and y >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Bedwars and Skywars GvG Teams!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0x8368ff)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bedwars_stats[bw_wins]}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bedwars_stats[bw_fkdr]}`')
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{skywars_stats[sw_wins_overall]}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{skywars_stats[sw_wins_solo]}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{skywars_stats[sw_wins_doubles]}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{skywars_stats[sw_kdr]}`')
                            embed1.set_footer(text=f"Duels wins - {duels_stats[duels_wins]}`\nDuels WLR - {duels_stats[duels_wlr]}")
                            await channel.send(embed=embed1)
                            break

                        elif x >= 1 and z >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Bedwars and Duels GvG Teams!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0x8368ff)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bedwars_stats[bw_wins]}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bedwars_stats[bw_fkdr]}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_stats[duels_wins]}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_stats[duels_wlr]}`')
                            embed1.set_footer(
                                text=f"Skywars Wins (Overall) - {skywars_stats[sw_wins_overall]}\nSkywars Wins (Solo) - {skywars_stats[sw_wins_solo]}\nSkywars Wins (Doubles) - {skywars_stats[sw_wins_doubles]}\nSkywars KDR - {skywars_stats[sw_kdr]}")
                            await channel.send(embed=embed1)
                            break

                        elif y >= 1 and z >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Skywars and Duels GvG Teams!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0x8368ff)
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{skywars_stats[sw_wins_overall]}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{skywars_stats[sw_wins_solo]}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{skywars_stats[sw_wins_doubles]}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{skywars_stats[sw_kdr]}`')
                            embed1.add_field(name="Duels Wins", value=f'`{duels_stats[duels_wins]}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_stats[duels_wlr]}`')
                            embed1.set_footer(text=f"Bedwars Wins - {bedwars_stats[bw_wins]}\nBedwars FKDR - {bedwars_stats[bw_fkdr]}")
                            await channel.send(embed=embed1)
                            break
                        elif x >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Bedwars GvG Team!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0x8368ff)
                            embed1.add_field(name="Bedwars Wins", value=f'`{bedwars_stats[bw_wins]}`')
                            embed1.add_field(name="Bedwars FKDR", value=f'`{bedwars_stats[bw_fkdr]}`')
                            embed1.set_footer(
                                text=f"Skywars Wins (Overall) - {skywars_stats[sw_wins_overall]}\nSkywars Wins (Solo) - {skywars_stats[sw_wins_solo]}\nSkywars Wins (Doubles) - {skywars_stats[sw_wins_doubles]}\nSkywars KDR - {skywars_stats[sw_kdr]}\nDuels wins - {duels_stats[duels_wins]}\nDuels WLR - {duels_stats[duels_wlr]}")
                            await channel.send(embed=embed1)
                            break
                        elif y >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Skywars GvG Team!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0x8368ff)
                            embed1.add_field(name="Skywars Wins (Overall)", value=f'`{skywars_stats[sw_wins_overall]}`')
                            embed1.add_field(name="Skywars Wins (Solo)", value=f'`{skywars_stats[sw_wins_solo]}`')
                            embed1.add_field(name="Skywars Wins (doubles)", value=f'`{skywars_stats[sw_wins_doubles]}`')
                            embed1.add_field(name="Skywars KDR", value=f'`{skywars_stats[sw_kdr]}`')
                            embed1.set_footer(
                                text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}\nDuels wins - {duels_stats[duels_wins]}`\nDuels WLR - {duels_stats[duels_wlr]}")
                            await channel.send(embed=embed1)
                            break
                        elif z >= 1:
                            embed1 = discord.Embed(title="You're eligible for the Duels GvG Team!",
                                                   description="Kindly await staff assistance for further information!",
                                                   color=0x8368ff)
                            embed1.add_field(name="Duels Wins", value=f'`{duels_stats[duels_wins]}`')
                            embed1.add_field(name="Duels WLR", value=f'`{duels_stats[duels_wlr]}`')
                            embed1.set_footer(
                                text=f"Bedwars Wins - {bedwars_stats[bw_wins]}\nBedwars FKDR - {bedwars_stats[bw_fkdr]}\nSkywars Wins (Overall) - {skywars_stats[sw_wins_overall]}\nSkywars Wins (Solo) - {skywars_stats[sw_wins_solo]}\nSkywars Wins (Doubles) - {skywars_stats[sw_wins_doubles]}\nSkywars KDR - {skywars_stats[sw_kdr]}")
                            await channel.send(embed=embed1)
                            break
                        else:
                            embed1 = discord.Embed(
                                title="You're ineligible to apply GvG Team because you don't meet the requirements!",
                                description="Kindly await staff assistance for further information!", color=0xcd5c5c)
                            embed1.set_footer(
                                text=f"Bedwars Wins - {bedwars_stats[bw_wins]}\nBedwars FKDR - {bedwars_stats[bw_fkdr]}\nSkywars Wins (Overall) - {skywars_stats[sw_wins_overall]}\nSkywars Wins (Solo) - {skywars_stats[sw_wins_solo]}\nSkywars Wins (Doubles) - {skywars_stats[sw_wins_doubles]}\nSkywars KDR - {skywars_stats[sw_kdr]}\nDuels wins - {duels_stats[duels_wins]}`\nDuels WLR - {duels_stats[duels_wlr]}")
                            await channel.send(embed=embed1)
                            stop_embed = discord.Embed(
                                title="Since you don't meet the requirements, can this ticket be closed?",
                                description="Click `Yes` if you wish to delete the ticket.\n Click `No` if you wish to wait for staff assistance\nClick `Restart` if you wish to restart the ticket process",
                                color=0x8368ff)
                            yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                            no = Button(style=ButtonStyle.red, label="No", id="no")
                            restart = Button(style=ButtonStyle.grey, label="Restart", id="restart")

                            await channel.send(embed=stop_embed, components=[[yes, no], [restart]])

                            while True:
                                click = await self.bot.wait_for("button_click",
                                                                check=lambda x: (
                                                                                        x.author == author and x.channel == channel) or (
                                                                                        self.bot.staff in x.author.roles and x.channel == channel))

                                if click.component.id == "yes":
                                    success_embed = discord.Embed(title="Success", color=0x00A86B)
                                    await click.respond(embed=success_embed)
                                    transcript = await chat_exporter.export(channel)
                                    if transcript is None:
                                        pass
                                    else:
                                        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                                       filename=f"deleted-{channel.name}.html")

                                    if channel.category.name in self.bot.ticket_categories:
                                        embed = discord.Embed(title='This ticket will be deleted in 10 seconds!',
                                                              description='',
                                                              color=0xDE3163)
                                        await channel.send(embed=embed)
                                        await asyncio.sleep(10)
                                        await discord.TextChannel.delete(channel)

                                        name = await utils.name_grabber(author)
                                        embed = discord.Embed(title=f'{channel.name} was deleted by {name}',
                                                              description="They deleted their own ticket.",
                                                              color=0x8368ff)
                                        await self.bot.log_channel.send(embed=embed)
                                        await self.bot.log_channel.send(file=transcript_file)
                                        break
                                elif click.component.id == "no":
                                    success_embed = discord.Embed(title="Success", color=0x00A86B)
                                    await click.respond(embed=success_embed)
                                    embed = discord.Embed(title="The ticket will not be closed. ",
                                                          description="Kindly await staff assistance!", color=0xde3163)
                                    await channel.send(embed=embed)
                                    break
                                elif click.component.id == "restart":
                                    embed = discord.Embed(title="Restarting",
                                                          description="The ticket process will restart in 5 seconds!",
                                                          color=0x00a86b)
                                    await asyncio.sleep(2)
                            break


                if reply == "Christmas Event":
                    embed = discord.Embed(title="What is your Minecraft Username?",
                        color=0x4b89e4)
                    await channel.send(embed=embed)
                    username = await self.bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    name, uuid = await utils.get_dispnameID(username.content)

                    if name != None:
                        await channel.edit(name=f"Event-{name}",
                            category=discord.utils.get(channel.guild.categories, name="CHRISTMAS COUNTDOWN"))
                        embed = discord.Embed(title="General Information", description="Following is some general information surrounding the event.", color=0x8368ff)
                        embed.add_field(name="Miscellaneous Christmas Countdown", value="""Every day from the 1st to the 24th of December, a series of challenges
                                                                                            will be released for participants to complete.\n
                                                                                            Additionally, there will be one extra member/ally only challenge, and an open challenge for everyone on weekends.""", inline=False)
                        embed.add_field(name="Scaled challenges", value="""As part of the daily challenges, scaled challenges will reward differing points depending on how well you performed compared to other participants. Point distribution is as follows:\n
                                                                            1st-3rd - 3 points
                                                                            4th-10th - 2 points
                                                                            Remaining players - 1 point""", inline=False)
                        embed.add_field(name="Rules", value='''All Hypixel rules apply. This includes:
                                    - No cheating
                                    - No account sharing
                                    - No boosting, etc''',inline=False)
                        embed.add_field(name="Submitting", value="""Every day, along with the challenges, a unique password will be given for that days challenges.
                        When submitting your challenges, you will be required to have the password written in your chat box (Example below).
                        Submissions can take the form of an unedited screenshot or short video, whatever works best.
                        You can only submit challenges from the day you're submitting, 
                        so previously given challenges will not be awarded with points.""", inline=False)
                        embed.set_image(url="https://media.discordapp.net/attachments/911761019947352074/911792454099947580/unknown.png?width=1111&height=625")
                        await channel.send(embed=embed)

                        await author.add_roles(self.bot.christmas_event)

                        embed = discord.Embed(title=":ballot_box_with_check: Registration Successful!", color=0xFFFDD0)
                        embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
                        embed.add_field(name=name, value="To unregister, please ping a staff member!", inline=False)
                        await channel.send(embed=embed)
                        break

                    else:
                        await channel.send("Unkown IGN! Restarting ticket process...")
                


                elif reply == "Other":
                    embed = discord.Embed(title=f"{name} created this ticket for an unspecified reason!",
                                        description="Kindly specify your reason behind creating this ticket and wait for staff to help you!")
                    await channel.edit(name=f"Unknown-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    await channel.purge(limit=10)
                    await channel.send(embed=embed)
                    break
                else:
                    mistake = discord.Embed(
                        title="Did you make a mistake while specifying why you created this ticket?",
                        description="Click `Yes` if you did. This will restart the ticketing process.\n Click `No` if you didn't make a mistake and wish to wait for staff assistance.",
                        color=0x8368ff)
                    yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                    no = Button(style=ButtonStyle.red, label="No", id="no")

                    await channel.send(embed=mistake, components=[[yes, no]])

                    while True:
                        click = await self.bot.wait_for("button_click",
                                                        check=lambda x: (
                                                                                x.author == author and x.channel == channel) or (
                                                                                self.bot.staff in x.author.roles and x.channel == channel))

                        if click.component.id == "yes":
                            embed = discord.Embed(title="Great! Restarting the ticketing process!",
                                                  color=0x00A86B)
                            await click.respond(embed=embed)
                        elif click.component.id == "no":
                            embed = discord.Embed(
                                title="Alright, kindly specify why you created this ticket and then await staff assistance!",
                                color=0x00A86B)
                            await click.respond(embed=embed)
                            break

    @commands.command(aliases=['reg', 'verify'])
    async def register(self, ctx, name):
        async with ctx.channel.typing():
            author = ctx.author
            if ctx.channel.id == 714882620001091585:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                        request = await resp.json(content_type=None)

                    if resp.status != 200:
                        embed = discord.Embed(title="Please enter a valid minecraft username!",
                                              color=0xDE3163)
                        await ctx.channel.send(embed=embed)
                    elif request['name'] in self.bot.staff_names and self.bot.staff not in ctx.author.roles:
                        embed = discord.Embed(title="Staff impersonation is a punishable offense!",
                                              color=0xDE3163)
                        await ctx.channel.send(embed=embed)
                    else:
                        ign = request['name']
                        uuid = request['id']

                        guild_name = await utils.get_guild(name)

                        nick = await author.edit(nick=ign)
                        if guild_name == "Miscellaneous":
                            await ctx.author.remove_roles(self.bot.new_member_role, reason="Register")

                            await ctx.channel.purge(limit=1)
                            embed = discord.Embed(title="Registration successful!")
                            embed.add_field(name=ign,
                                            value="Member of Miscellaneous")

                            embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
                            await ctx.send(embed=embed)
                            await ctx.author.add_roles(self.bot.member_role, reason="Register")

                        elif guild_name in self.bot.misc_allies:
                            for guild in self.bot.misc_allies:
                                if guild == guild_name:
                                    gtag = await utils.get_gtag(guild)
                                    if ctx.author.nick is None or str(gtag) not in ctx.author.nick:
                                        ign = ign + " " + str(gtag)
                                    await ctx.author.edit(nick=ign)
                                    await ctx.author.remove_roles(self.bot.new_member_role, reason="Register")
                                    await ctx.author.add_roles(self.bot.guest, self.bot.ally, reason="Register")

                                    await ctx.channel.purge(limit=1)
                                    embed = discord.Embed(title="Registration successful!")
                                    embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
                                    embed.add_field(name=ign, value=f"Member of {guild}")
                                    await ctx.send(embed=embed)

                        elif guild_name != "Miscellaneous" and guild_name not in self.bot.misc_allies:
                            await ctx.author.remove_roles(self.bot.new_member_role, reason="Register")
                            await ctx.author.add_roles(self.bot.awaiting_app, reason="Register")
                            if nick is None:
                                nick = author.name

                            await ctx.channel.purge(limit=1)
                            embed = discord.Embed(title="Registration successful!")
                            embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}/512.png')
                            embed.add_field(name=ign, value="New Member")
                            await ctx.send(embed=embed)

                            category = discord.utils.get(ctx.guild.categories, name="RTickets")
                            ticket_channel = await ctx.guild.create_text_channel(f"registration-ticket-{nick}",
                                                                                 category=category)
                            await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False,
                                                                 read_messages=False)
                            await ticket_channel.set_permissions(self.bot.staff, send_messages=True, read_messages=True,
                                                                 add_reactions=True, embed_links=True,
                                                                 attach_files=True,
                                                                 read_message_history=True, external_emojis=True)
                            await ticket_channel.set_permissions(self.bot.helper, send_messages=True,
                                                                 read_messages=True,
                                                                 add_reactions=True, embed_links=True,
                                                                 attach_files=True,
                                                                 read_message_history=True, external_emojis=True)
                            await ticket_channel.set_permissions(author, send_messages=True, read_messages=True,
                                                                 add_reactions=True, embed_links=True,
                                                                 attach_files=True,
                                                                 read_message_history=True, external_emojis=True)
                            await ticket_channel.set_permissions(self.bot.new_member_role, send_messages=False,
                                                                 read_messages=False,
                                                                 add_reactions=True, embed_links=True,
                                                                 attach_files=True,
                                                                 read_message_history=True, external_emojis=True)

                            try:
                                embed = discord.Embed(title="Miscellaneous Guild Requirements",
                                                      description="These requirements are subject to change!",
                                                      color=0x8368ff)
                                embed.add_field(name="Active",
                                                value=f"•  {format(self.bot.active, ',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="DNKL Eligibility",
                                                value=f"•  {format(self.bot.dnkl, ',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="Resident",
                                                value=f"•  {format(self.bot.resident_req, ',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="Member",
                                                value=f"•  {format(self.bot.inactive, ',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="New Member",
                                                value=f"•  {format(self.bot.new_member, ',d')} Daily Guild Experience",
                                                inline=False)
                                embed.set_footer(
                                    text="You are considered a New Member for the first 7 days after joining the guild"
                                         "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
                                await ctx.author.send(embed=embed)
                            except Exception:
                                pass
                    await session.close()

            else:
                await ctx.send('This command can only be used in the registration channel!')

    @commands.command(aliases=['del'])
    async def delete(self, ctx):
        """Deletes the ticket channel the command is used in.
        """

        if self.bot.staff in ctx.author.roles:
            if ctx.channel.category.name in self.bot.ticket_categories:

                embed = discord.Embed(title='This ticket will be deleted in 10 seconds!', description='',
                                      color=0xDE3163)
                await ctx.send(embed=embed)
                await asyncio.sleep(10)
                transcript = await chat_exporter.export(ctx.channel)

                if transcript is None:
                    embed = discord.Embed(text="Transcript creation failed!",
                                          color=0xDE3163)
                    await ctx.send(embed=embed)
                    return
                transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                               filename=f"transcript-{ctx.channel.name}.html")

                await discord.TextChannel.delete(ctx.channel)

                name = await utils.name_grabber(ctx.author)
                embed = discord.Embed(title=f'{ctx.channel.name} was deleted by {name}',
                                      description="", color=0x8368ff)
                embed.set_footer(text="Following is the transcript")
                await self.bot.log_channel.send(embed=embed)
                await self.bot.log_channel.send(file=transcript_file)

    @commands.command()
    @commands.has_role("Staff")
    async def add(self, ctx, member: discord.Member):
        """Adds the specified user to the ticket.
        """
        if ctx.channel.category.name in self.bot.ticket_categories:
            await ctx.channel.set_permissions(member, send_messages=True, read_messages=True,
                                              add_reactions=True, embed_links=True,
                                              attach_files=True,
                                              read_message_history=True, external_emojis=True)
            embed = discord.Embed(title=f"{member.name} has been added to the ticket!",
                                  color=0x00A86B)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("Staff")
    async def remove(self, ctx, member: discord.Member):
        """Removes the specified user from the ticket.
        """
        if ctx.channel.category.name in self.bot.ticket_categories:
            await ctx.channel.set_permissions(member, send_messages=False, read_messages=False,
                                              add_reactions=False, embed_links=False,
                                              attach_files=False,
                                              read_message_history=False, external_emojis=False)
            embed = discord.Embed(title=f"{member.name} has been removed from the ticket!",
                                  color=0x00A86B)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("Staff")
    async def rename(self, ctx, *, channel_name):
        """Renames the channel
        """
        await ctx.message.delete()
        if ctx.channel.category.name in self.bot.ticket_categories:
            channel_name = channel_name.replace(" ", "-")
            await ctx.channel.edit(name=f"{channel_name}")

    @commands.command()
    @commands.has_role("Staff")
    async def transcript(self, ctx):
        """Creates a transcript for the channel the command is entered in
        """
        if ctx.channel.category.name in self.bot.ticket_categories:
            transcript = await chat_exporter.export(ctx.channel)

            if transcript is None:
                embed = discord.Embed(text="Transcript creation failed!",
                                      color=0xDE3163)
                await ctx.send(embed=embed)
                return

            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                           filename=f"transcript-{ctx.channel.name}.html")

            await ctx.send(file=transcript_file)

    @commands.command()
    @commands.has_role("Admin")
    async def accept(self, ctx, member: discord.Member):
        """Used to accept staff applications. This command must be typed in the application channel. It doesn't work elsewhere.
        """
        if ctx.channel.category.name in self.bot.ticket_categories:
            embed = discord.Embed(title=f"Congratulations {member}, your staff application has been accepted!",
                                  description="Please view the following as they'll help you become a better staff member!",
                                  color=0x8368ff)
            embed.set_footer(text="https://bit.ly/MiscStaffGuide\n"
                                  "#staff-faq")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def deny(self, ctx, channel: discord.TextChannel):
        """Used to deny staff applications. This command can be used in any channel provided, the syntax is met.
        """
        embed = discord.Embed(title="Your staff application has been denied!",
                              description="The reasons are listed below",
                              color=0xDE3163)

        embed.set_footer(
            text="You may reapply in 2 weeks. \nFollowing is the transcript so that you can refer to it while reapplying.")

        question_number = {
            1: 'What is your age?',
            2: 'How long have you been in the guild for?',
            3: 'Have you had any past infractions on Hypixel?',
            4: 'Why have you decided to apply for staff?',
            5: 'What has brought you to Miscellaneous, and what has kept you here?',
            6: 'What is something you could suggest that would improve the guild?',
            7: 'You have just started as a helper and a moderator starts arguing with another member. This argument starts to get serious quite quickly. What do you do?',
            8: 'Suppose it\'s your first week of being a helper and you guild-mute a well-known player. Your guildmates start spamming you calling you a bad moderator and telling you to unmute them. What would you do?',
            9: 'Upon joining a game and you discover that a guild member is in your game and is hacking. What do you do?',
            10: 'Have you been staff in any other guild or on any server? If yes, which one?',
            11: 'How much time do you have to contribute to the role? (Per day)',
            12: 'Tell us about a time you made a mistake within the last year. How did you deal with it? What did you learn?',
            13: 'Anything else you would us to know?',
            14: 'General Critiquing'
        }

        all_questions = ''
        for x in range(1, 15):
            question = question_number.get(int(x), 'None')
            all_questions = all_questions + f"{x})" + question + "\n\n"

        embed1 = discord.Embed(title="Questions", description=all_questions, color=0x8368ff)
        await ctx.send(embed=embed1)
        while True:
            while True:
                await ctx.send("What is the question number of the reply that you would like to critique?"
                               "\n**Please just give the question number!**"
                               "If you would like to critique something in general, reply with `14`")
                question = await self.bot.wait_for('message',
                                                   check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                question = question.content
                if str(question) in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"):
                    question = question_number.get(int(question), 'None')
                    break
                else:
                    await ctx.send("Please respond with a valid number. (1-14)")

            await ctx.send(f"`{question}`"
                           "\n**What was the issue that you found with their reply?**")
            critique = await self.bot.wait_for('message',
                                               check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
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

            while True:
                more = await self.bot.wait_for('message',
                                            check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                more = more.content
                more = more.capitalize()

                if more in ('Yes', 'Yeah', 'Ye', 'Yea'):
                    break
                elif more in ('No', 'Nah', 'Nope'):
                    await channel.send(embed=embed)
                    transcript = await chat_exporter.export(channel)

                    if transcript is None:
                        embed = discord.Embed(text="Transcript creation failed!",
                                              color=0xDE3163)
                        await ctx.send(embed=embed)
                        return

                    transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                   filename=f"transcript-{channel.name}.html")

                    await channel.send(file=transcript_file)

    @commands.command()
    async def new(self, ctx):
        name = await utils.name_grabber(ctx.author)

        category = discord.utils.get(self.bot.guild.categories, name="🎫 Ticket Section")
        ticket_channel = await self.bot.guild.create_text_channel(f"ticket-{name}",
                                                                       category=category,
                                                                       topic="<:t:869239368060112906><:i:869239367942697010><:c:869239368383074414>"
                                                                             "<:k:869239367854612480><:e:869239368517287936><:t:869239368060112906>")
        creating_ticket = discord.Embed(title="Click here to go to your ticket!",
                                        url=f"https://discord.com/channels/522586672148381726/{ticket_channel.id}",
                                        color=0x00A86B)
        creating_ticket.set_author(name="Ticket successfully created!")

        await ctx.send(embed=creating_ticket)

        await ticket_channel.set_permissions(self.bot.guild.get_role(self.bot.guild.id), send_messages=False,
                                             read_messages=False)
        await ticket_channel.set_permissions(self.bot.staff, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(self.bot.helper, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(self.bot.new_member_role, send_messages=False,
                                             read_messages=False,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.send(f"{ctx.author.mention}")


def setup(bot):
    bot.add_cog(Tickets(bot))
