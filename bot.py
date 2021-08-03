import asyncio
import json
import logging
import sys
import traceback

import io
import aiohttp
import discord
import toml
import chat_exporter
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from cogs.utils import hypixel

logging.basicConfig(level=logging.INFO)

config = toml.load('config.toml')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['bot']['prefix']), intents=intents,
                   status=discord.Status.idle, activity=discord.Game(config['bot']['status']), case_insensitive=True)

bot.config = config
bot.token = config['bot']['token']
bot.api_tokens = config['hypixel']['api_keys']
bot.owner_id = config['bot']['ownerID']
bot.resident_req = int(50000)
bot.active = int(280000)
bot.inactive = int(105000)
bot.dnkl = bot.inactive * 2
bot.new_member = int(25000)


class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page, color=0x8368ff)
            await destination.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=0x8368ff)
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)


bot.help_command = HelpCommand(command_attrs={'hidden': True})

initial_extensions = ['cogs.fun', 'cogs.hypixel', 'cogs.mod', 'cogs.staff', 'cogs.ticket', 'cogs.owner']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'{extension} Loaded!')
        except Exception as e:
            print(f'Failed to load extention {extension}', file=sys.stderr)


@bot.event
async def on_ready():
    print('The Miscellaneous Bot is ONLINE!')


@bot.event
async def on_command_error(ctx, error):
    # Prevents commands with local handlers or cogs with overwrritten on_command_errors being handled here
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title='Invalid Command!',
                              descrption='Use `,help` to view a list of all commands!', color=0xDE3163)
        await ctx.send(embed=embed)
        return
    elif ctx.command.has_error_handler() or ctx.cog.has_error_handler():
        return

    # Checks for the original exception raised and send to CommandInvokeError
    error = getattr(error, 'original', error)

    if isinstance(error, commands.NotOwner):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="You are not the owner of this bot!", color=0xDE3163)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRole):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="You do not have the required roles to access this restricted command!",
                              color=0xDE3163)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                              description="You do not have the required roles to access this restricted command!",
                              color=0xDE3163)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        usage = f"{ctx.prefix}{ctx.command.name}"
        for key, value in ctx.command.clean_params.items():
            if value.default == None:
                usage += " [" + key + "]"
            else:
                usage += " <" + key + ">"
        embed = discord.Embed(title="Missing arguments",
                              description=f"Command usage:\n`{usage}`\nFor more help, see `{ctx.prefix}help {ctx.command}`",
                              color=0xDE3163)
        await ctx.send(embed=embed)

    else:
        # All other errors get sent to the error channel
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        await bot.error_channel.send(f"Ignoring exception in command {ctx.command}:\n```py\n{tb}\n```")


@bot.event
async def on_error(event, *args, **kwargs):
    # Grabs the error being handled, formats it and sends it to the error channel
    tb = traceback.format_exc()
    await bot.error_channel.send(f"Ignoring exception in event {event}:\n```py\n{tb}\n```")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(714882620001091585)
    role = discord.utils.get(member.guild.roles, name="New Member")
    await member.add_roles(role)

    embed = discord.Embed(title=f"Welcome to the Miscellaneous Discord, {member.name}", color=0x8368ff)
    embed.add_field(name="Register using the following command:", value="**,register** `Your Minecraft Name`",
                    inline=False)
    embed.set_footer(text="Example:\n,register John")

    await channel.send(embed=embed)


"------------------------------------------------------------------------------------------------------------------Tickets------------------------------------------------------------------------------------------------------"


# Ticket Handling
@bot.event
async def on_guild_channel_create(channel):
    if channel.category.name == "RTickets":
        embed = discord.Embed(title="Do you wish to join Miscellaneous in-game?", color=0x8368ff)
        embed.add_field(name="If you do", value="Type `Yes`")
        embed.add_field(name="If you don't", value="Type `No`")
        await channel.send(embed=embed)
        reply = await bot.wait_for('message', check=lambda x: x.channel == channel)
        author = reply.author
        reply = reply.content
        reply = reply.capitalize()
        if reply in ('Yes', 'Yeah', 'Ye', 'Yea'):
            await channel.send(
                'Alright. Kindly wait until staff get in contact with you.'
                '\n`You are recommended to leave your present guild (if any) so that staff can invite you to Miscellaneous ASAP`'
                '\nIf you get in the guild and want the member role in the discord, use ,sync `Your Minecraft Name` ! ')
            await asyncio.sleep(3)
            embed1 = discord.Embed(title="Miscellaneous Guild Requirements",
                                   description="These requirements are subject to change!",
                                   color=0x8368ff)
            embed1.set_author(name="While you wait, kindly take a look a the guild requirements!")
            embed1.add_field(name="Active",
                             value=f"•  {format(bot.active, ',d')} Weekly Guild Experience",
                             inline=False)
            embed1.add_field(name="Do Not Kick List Eligibility",
                             value=f"•  {format(bot.dnkl, ',d')} Weekly Guild Experience",
                             inline=False)
            embed1.add_field(name="Resident", value=f"•  {format(bot.resident_req, ',d')} Weekly Guild Experience",
                             inline=False)
            embed1.add_field(name="Member",
                             value=f"•  {format(bot.inactive, ',d')} Weekly Guild Experience",
                             inline=False)
            embed1.add_field(name="New Member",
                             value=f"•  {format(bot.new_member, ',d')} Daily Guild Experience",
                             inline=False)
            embed1.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                                   "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
            await channel.send(embed=embed1)
        elif reply in ('No', 'Nah', 'Nope'):
            embed = discord.Embed(title="Did you join the discord to organize a GvG with Miscellaneous?",
                                  color=0x8368ff)
            embed.add_field(name="If yes", value="Type `Yes`")
            embed.add_field(name="If not", value="Type `No`")
            await channel.send(embed=embed)
            noreply = await bot.wait_for('message', check=lambda x: x.channel == channel)
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
            elif noreply == "No":
                await channel.send(
                    "**Okay, kindly specify your reason behind joining the Miscellaneous discord and then await staff help!**")
            else:
                embed = discord.Embed(title="My massive computer brain thinks you made a mistake.",
                                      color=0xff0000)
                embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
                embed.add_field(name="If this is false", value="Type `No`", inline=False)
                await channel.send(embed=embed)
                errorreply = await bot.wait_for('message', check=lambda x: x.channel == channel)
                errorreply = errorreply.content
                errorreply = errorreply.capitalize()
                if errorreply in ('Yes', 'Yeah', 'Ye', 'Yea'):
                    embed = discord.Embed(title="Great! Let's start over!",
                                          color=0x8368ff)
                    await channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Alright! Kindly specify why you joined the discord and await staff assistance!",
                        color=0x8368ff)
                    await channel.send(embed=embed)
        else:
            embed = discord.Embed(title="My massive computer brain thinks you made a mistake.",
                                  color=0xff0000)
            embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
            embed.add_field(name="If this is false", value="Type `No`", inline=False)
            await channel.send(embed=embed)
            errorreply = await bot.wait_for('message', check=lambda x: x.channel == channel)
            errorreply = errorreply.content
            errorreply = errorreply.capitalize()
            if errorreply in ('Yes', 'Yeah', 'Ye', 'Yea'):
                embed = discord.Embed(title="Great! Let's start over!",
                                      color=0x8368ff)
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Alright! Kindly specify why you joined the discord and await staff assistance!",
                    color=0x8368ff)
                await channel.send(embed=embed)
    elif channel.category.name == '🎫 Ticket Section':
        while True:
            await asyncio.sleep(3)
            embed = discord.Embed(title="What did you make this ticket?",
                                  description="Please reply with your reason from the list given below!",
                                  color=0x8368ff)
            embed.add_field(name="Do-Not-Kick-List", value="Reply with `DNKL`", inline=False)
            embed.add_field(name="Role/Username/Tag Change", value="Reply with `Role`", inline=False)
            embed.add_field(name="Report", value="Reply with `Report`", inline=False)
            embed.add_field(name="Problem/Query/Complaint/Suggestion", value="Reply with `General`", inline=False)
            embed.add_field(name="Milestone", value="Reply with `Milestone`", inline=False)
            embed.add_field(name="Staff Application", value="Reply with `Staff`", inline=False)
            embed.add_field(name="GvG Team Application", value="Reply with `GvG`", inline=False)
            embed.add_field(name="Other", value="Reply with `Other`", inline=False)
            await channel.send(embed=embed)
            reply = await bot.wait_for('message', check=lambda x: x.channel == channel)

            author = reply.author
            name = await hypixel.name_grabber(author)

            reply = reply.content
            reply = reply.capitalize()

            if reply in ("Dnkl", "Do not kick list", "Do-Not-Kick-List"):

                name = await hypixel.name_grabber(author)

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
                api = hypixel.get_api()
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://api.hypixel.net/guild?key={api}&player={uuid}') as resp:
                        data = await resp.json()
                        await session.close()
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
                                                      color=0xDE3163)
                                embed.set_thumbnail(
                                    url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                embed.set_author(name="Do-not-kick-list: Eligibility Check")
                                embed.set_footer(text="Even though you do not meet the requirements,"
                                                      " you might still be accepted so we shall proceed with the application process!")
                                embed.add_field(name="You are not eligible to apply for the do not kick list.",
                                                value=f"You need a minimum of {format(bot.dnkl, ',d')} weekly guild experience."
                                                      f"\n You have {totalexp} weekly guild experience.",
                                                inline=True)
                                await channel.send(embed=embed)
                            if eligiblity is True:
                                embed = discord.Embed(title=name,
                                                      url=f'https://visage.surgeplay.com/full/832/{uuid}',
                                                      color=0x333cff)
                                embed.set_thumbnail(
                                    url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                embed.set_author(name='Do-not-kick-list: Eligibility Check')
                                embed.add_field(name="You are eligible to apply for the do not kick list.",
                                                value=f"You meet the minimum of {format(bot.dnkl, ',d')} weekly guild experience."
                                                      f"\n You have {totalexp} weekly guild experience.",
                                                inline=True)
                                await channel.send(embed=embed)

                            embed = discord.Embed(title="When will your inactivity begin? (Start date)",
                                                  description="DD/MM/YYYY",
                                                  color=0x8368ff)
                            embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                            await channel.send(embed=embed)
                            start = await bot.wait_for('message',
                                                       check=lambda x: x.author == author and x.channel == channel)
                            start = start.content
                            embed = discord.Embed(title="When will your inactivity end? (End date)",
                                                  description="DD/MM/YYYY",
                                                  color=0x8368ff)
                            embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                            await channel.send(embed=embed)
                            end = await bot.wait_for('message',
                                                     check=lambda x: x.author == author and x.channel == channel)
                            end = end.content
                            embed = discord.Embed(title="What's the reason behind your inactivity?",
                                                  color=0x8368ff)
                            await channel.send(embed=embed)
                            reason = await bot.wait_for('message',
                                                        check=lambda x: x.author == author and x.channel == channel)
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
                            await channel.send(
                                f"Alright! Kindly await staff assistance!"
                                f"\n**Start:** {start}"
                                f"\n**End:** {end}"
                                f"\n**Reason:** {reason}"
                                f"\n*If you made an error, kindly notify staff by typing after this message*"
                                f"\n\n||,dnkladd {name} {author.mention} {start} {end} {reason}||"
                            )

                            dnkl_decision = discord.Embed(title="Staff, what do you wish to do with this dnkl request?",
                                                          description=f"\nClick `Approve` to approve the do-not-kick-list request"
                                                                      f"\nClick `Deny` to deny the do-not-kick-list request"
                                                                      f"\nClick `Error` if the user made an error while applying for the do not kick list",
                                                          color=0x8368ff)

                            approve = Button(style=ButtonStyle.blue, label="Approve", id="approve")
                            deny = Button(style=ButtonStyle.red, label="Deny", id="deny")
                            error = Button(style=ButtonStyle.grey, label="Error", id="error")

                            await channel.send(embed=dnkl_decision, components=[[approve, deny], [error]])

                            while True:
                                click = await bot.wait_for("button_click",
                                                           check=lambda x: x.channel == channel and (
                                                                   bot.staff in bot.misc_guild.get_member(
                                                               x.author.id).roles or bot.t_officer in bot.misc_guild.get_member(
                                                               x.author.id).roles))

                                if click.component.id == "approve":
                                    a, b, c = start.split('/')
                                    p, q, r = end.split('/')
                                    ign, uuid = await hypixel.get_dispnameID(name)
                                    rank = await hypixel.get_rank(name)
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
                                        url=f'https://crafatar.com/renders/body/{uuid}')
                                    embed.add_field(name="IGN:", value=f"{ign}", inline=False)
                                    embed.add_field(name="Start:", value=f"{a} {start_month} {c}",
                                                    inline=False)
                                    embed.add_field(name="End:", value=f"{p} {end_month} {r}",
                                                    inline=False)
                                    embed.add_field(name="Reason", value=f"{reason}", inline=False)
                                    embed.set_author(name="Do not kick list")
                                    message = await bot.dnkl_channel.send(embed=embed)

                                    with open('dnkl.json') as f:
                                        data = json.load(f)
                                    dnkl_dict = {ign: message.id}

                                    data.update(dnkl_dict)
                                    with open('dnkl.json', 'w') as f:
                                        json.dump(data, f)
                                    embed = discord.Embed(title="This DNKL Application has been accepted!",
                                                          description="The DNKL Embed has been sent to <#629564802812870657>",
                                                          color=0x00A86B)
                                    await channel.send(embed=embed)
                                    success_embed = discord.Embed(title="Success", color=0x00A86B)
                                    await click.respond(embed=success_embed)
                                    break
                                elif click.component.id == "deny":
                                    embed = discord.Embed(title="This do not kick list request has been denied",
                                                          color=0xDE3163)
                                    await channel.send(embed=embed)
                                    success_embed = discord.Embed(title="Success", color=0x00A86B)
                                    await click.respond(embed=success_embed)
                                    break

                                elif click.component.id == "error":
                                    embed = discord.Embed(title="What is their username?",
                                                          color=0x8368ff)
                                    await channel.send(embed=embed)

                                    name = await bot.wait_for('message', check=lambda
                                        x: x.channel == channel.channel)
                                    name = name.content
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(
                                                f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                                            request = await resp.json()
                                            ign = request['name']
                                            uuid = request['id']
                                            rank = await hypixel.get_rank(name)
                                            with open('dnkl.json') as f:
                                                data = json.load(f)
                                            if resp.status_code != 200:
                                                await channel.send('Unknown IGN!')
                                            else:
                                                embed = discord.Embed(
                                                    title="When will their inactivity begin? (Start date)",
                                                    description="DD/MM/YYYY",
                                                    color=0x8368ff)
                                                embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                                                await channel.send(embed=embed)
                                                start_date = await bot.wait_for('message',
                                                                                check=lambda
                                                                                    x: x.author == author and x.channel == channel)
                                                start_date = start_date.content
                                                embed = discord.Embed(
                                                    title="When will their inactivity end? (End date)",
                                                    description="DD/MM/YYYY",
                                                    color=0x8368ff)
                                                embed.set_footer(text="For Example:\n 1/2/2021 = 1st Feb 2021")
                                                await channel.send(embed=embed)
                                                end_date = await bot.wait_for('message',
                                                                              check=lambda
                                                                                  x: x.channel == channel.channel)
                                                end_date = end_date.content
                                                a, b, c = start_date.split('/')
                                                p, q, r = end_date.split('/')

                                                embed = discord.Embed(
                                                    title="What's the reason behind their inactivity?",
                                                    color=0x8368ff)
                                                reason = await bot.wait_for('message',
                                                                            check=lambda
                                                                                x: x.channel == channel.channel)
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
                                                    await channel.channel.purge(limit=1)

                                                    message = await bot.dnkl_channel.send(embed=embed)

                                                    dnkl_dict = {ign: message.id}

                                                    data.update(dnkl_dict)
                                                    with open('dnkl.json', 'w') as f:
                                                        json.dump(data, f)

                                                    await session.close()
                                                    success_embed = discord.Embed(title="Success", color=0x00A86B)
                                                    await click.respond(embed=success_embed)
                                                    break

                stop_embed = discord.Embed(title="Can this ticket be closed?",
                                           description="Click `Yes` if you resolved your issue and want to delete the ticket.\n Click `No` if you wish to wait for staff assistance\nClick `Restart` if you wish to restart the ticket process",
                                           color=0x8368ff)
                yes = Button(style=ButtonStyle.blue, label="Yes", id="yes")
                no = Button(style=ButtonStyle.red, label="No", id="no")
                restart = Button(style=ButtonStyle.grey, label="Restart", id="restart")

                await channel.send(embed=stop_embed, components=[[yes, no], [restart]])

                while True:
                    click = await bot.wait_for("button_click",
                                               check=lambda x: (x.author == author and x.channel == channel) or (bot.staff in x.author.roles and x.channel == channel))

                    if click.component.id == "yes":
                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                        await click.respond(embed=success_embed)
                        transcript = await chat_exporter.export(channel)
                        if transcript is None:
                            pass
                        else:
                            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                           filename=f"deleted-{channel.name}.html")

                        if channel.category.name in bot.ticket_categories:
                            name = channel.name
                            embed = discord.Embed(title='This ticket will be deleted in 10 seconds!',
                                                  description='',
                                                  color=0xDE3163)
                            msg = await channel.send(embed=embed)
                            await asyncio.sleep(10)
                            await discord.TextChannel.delete(channel)

                            name = await hypixel.name_grabber(author)
                            embed = discord.Embed(title=f'{channel.name} was deleted by {name}',
                                                  description="They deleted their own ticket.", color=0x8368ff)
                            await bot.logs.send(embed=embed)
                            await bot.logs.send(file=transcript_file)
                            break
                    elif click.component.id == "no":
                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                        await click.respond(embed=success_embed)
                        embed = discord.Embed(title="The ticket will not be closed. ",
                                              description="Kindly await staff assistance!", color=0xde3163)
                        await channel.send(embed=embed)
                        break
                    elif click.component.id == "restart":
                        embed = discord.Embed(title="Restarting", description="The ticket process will restart in 5 seconds!",
                                              color=0x00a86b)
                        asyncio.sleep(2)

            elif reply in ("Role", "Username", "Name"):
                await channel.edit(name=f"Role/NameChange-{name}",
                                   category=discord.utils.get(channel.guild.categories, name="OTHER"))
                embed = discord.Embed(title="What is your Minecraft username?",
                                      color=0x8368ff)
                await channel.send(embed=embed)
                role_reply = await bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                name = role_reply.content
                ign, uuid = await hypixel.get_dispnameID(name)
                if ign is None:
                    embed = discord.Embed(title="Please enter a valid minecraft username!",
                                          description="The ticket process will be restarted so you can rectify your mistake!",
                                          color=0xDE3163)
                    await channel.channel.send(embed=embed)
                elif ign in bot.staff_names and bot.staff not in author.roles:
                    embed = discord.Embed(title="Staff impersonation is a punishable offense!",
                                          description="The ticket process will be restarted!",
                                          color=0xDE3163)
                    await channel.send(embed=embed)
                else:
                    guild_name = await hypixel.get_guild(ign)
                    await author.edit(nick=ign)

                    has_tag_perms = any(role in author.roles for role in bot.tag_allowed_roles)

                    if guild_name == "Miscellaneous" or has_tag_perms is True:
                        if has_tag_perms is True:
                            while True:
                                embed = discord.Embed(title="What would you like your tag to be? ",
                                                      url="https://media.discordapp.net/attachments/420572640172834816/867506975884181554/unknown.png",
                                                      description="**Rules:**\n• Tags can have a maximum length of 6 characters. \n• Tags cannot include special characters. \n• Tags cannot include profane language. ")
                                embed.set_thumbnail(
                                    url="https://media.discordapp.net/attachments/420572640172834816/867506975884181554/unknown.png")
                                embed.set_footer(text="If you don't want a tag, type: None")
                                await channel.send(embed=embed)
                                tag = await bot.wait_for('message',
                                                         check=lambda
                                                             x: x.channel == channel and x.author == author)
                                tag = tag.content
                                with open('badwords.txt', 'r') as f:
                                    badwords = f.read()
                                if tag.isascii() is False:
                                    await channel.send(
                                        "The tag may not include special characters unless it's the tag of an ally guild.")
                                elif len(tag) > 6:
                                    await channel.send("The tag may not be longer than 6 characters.")
                                elif tag.lower() in badwords.split('\n'):
                                    await channel.send("The tag may not include profanity")
                                else:
                                    new_nick = ign + f' [{tag}]'
                                    await author.edit(nick=new_nick)
                                    break

                        await author.add_roles(bot.member_role)
                        embed = discord.Embed(title="Your nick and role was successfully changed!",
                                              description="await staff assistance.",
                                              color=0x8368ff)
                        embed.set_footer(text="Member of Miscellaneous"
                                              "\n• Guest & Awaiting Approval were removed"
                                              "\n• Member was given")
                        embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')

                        await channel.send(embed=embed)
                    elif guild_name in bot.misc_allies:
                        for guild in bot.misc_allies:
                            if guild == guild_name:
                                gtag = await hypixel.get_gtag(guild)
                                if author.nick is None or str(gtag) not in author.nick:
                                    ign = ign + " " + str(gtag)

                                await author.remove_roles(bot.new_member_role, bot.awaiting_app,
                                                          bot.member_role)
                                await author.add_roles(bot.guest, bot.ally)

                                embed = discord.Embed(title="Your nick, role and tag were successfully changed!",
                                                      description="If this wasn't the change you anticipated, kindly create a ticket or get in contact with staff!",
                                                      color=0x8368ff)
                                embed.set_footer(
                                    text=f"Member of {guild}\n• Nick & Tag Changed\n• Member & Awaiting Approval were removed\n• Guest and Ally were given")
                                embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{uuid}')
                                await channel.send(embed=embed)

                    elif guild_name != "Miscellaneous" and guild_name not in bot.misc_allies:
                        if str(channel.channel.category.name) == "RTickets":
                            await channel.send("You aren't in Miscellaneous in-game. Kindly await staff assistance!")
                        else:
                            await author.remove_roles(bot.member_role, bot.awaiting_app)
                            await author.add_roles(bot.guest)
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

                while True:
                    click = await bot.wait_for("button_click",
                                               check=lambda x: (x.author == author and x.channel == channel) or (
                                                       bot.staff in x.author.roles and x.channel == channel))

                    if click.component.id == "yes":
                        success_embed = discord.Embed(title="Success", color=0x00A86B)
                        await click.respond(embed=success_embed)
                        transcript = await chat_exporter.export(channel)
                        if transcript is None:
                            pass
                        else:
                            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                                           filename=f"deleted-{channel.name}.html")

                        if channel.category.name in bot.ticket_categories:
                            name = channel.name
                            embed = discord.Embed(title='This ticket will be deleted in 10 seconds!',
                                                  description='',
                                                  color=0xDE3163)
                            msg = await channel.send(embed=embed)
                            await asyncio.sleep(10)
                            await discord.TextChannel.delete(channel)

                            name = await hypixel.name_grabber(author)
                            embed = discord.Embed(title=f'{channel.name} was deleted by {name}',
                                                  description="They deleted their own ticket.", color=0x8368ff)
                            await bot.logs.send(embed=embed)
                            await bot.logs.send(file=transcript_file)
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
                        asyncio.sleep(2)


            elif reply in "Report":
                await channel.edit(name=f"Report-{name}",
                                   category=discord.utils.get(channel.guild.categories, name="REPORTS"))
                await channel.send(
                    "Alright. Please provide adequate details about the user and await staff assistance!")
                break
            elif reply in ("General", "Problem", "Query", "Complaint", "Suggestion"):
                await channel.edit(name=f"General-{name}",
                                   category=discord.utils.get(channel.guild.categories, name="OTHER"))
                await channel.send(
                    "Alright. Kindly specify the reason you created this ticket and wait for staff assistance!")
                break
            elif reply == "Milestone":
                await channel.edit(name=f"Milestone-{name}",
                                   category=discord.utils.get(channel.guild.categories, name="MILESTONES"))
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

                reqs = await bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                reqs = reqs.content
                reqs = reqs.capitalize()

                if reqs in ('Yes', 'Ye', 'Yup', 'Y', 'Yeah', 'Yus'):
                    embed = discord.Embed(title="Does your discord nick match your Minecraft Username?",
                                          description="Kindly reply with a Yes or No",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    nickmatching = await bot.wait_for('message',
                                                      check=lambda x: x.channel == channel and x.author == author)
                    nickmatching = nickmatching.content
                    nickmatching = nickmatching.capitalize()
                    if nickmatching in ('Yes', 'Ye', 'Yup', 'Y', 'Yeah', 'Yus'):
                        name = await hypixel.name_grabber(author)
                    else:
                        embed = discord.Embed(title="What is your Minecraft Username?",
                                              color=0x4b89e4)
                        await channel.send(embed=embed)
                        username = await bot.wait_for('message',
                                                      check=lambda x: x.channel == channel and x.author == author)
                        name = username.content
                        ign, uuid = await hypixel.get_dispnameID(name)

                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                            request = await resp.json()
                            await session.close()
                    uuid = request['id']
                    await channel.edit(name=f"Staff-Application-{name}",
                                       category=discord.utils.get(channel.guild.categories, name="OTHER"))
                    '''AGE'''
                    embed = discord.Embed(title="What is your age?",
                                          description="Kindly reply with a number",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    age = await bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    age = age.content

                    '''VETERENCY'''
                    embed = discord.Embed(title="For how long have you been in Miscellaneous?",
                                          description="You can check this through \"/g menu\" ingame",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    veterency = await bot.wait_for('message',
                                                   check=lambda x: x.channel == channel and x.author == author)
                    veterency = veterency.content

                    '''PAST INFRACTIONS'''
                    embed = discord.Embed(title="Have you had any past infractions on Hypixel?",
                                          description="Kindly reply with a Yes or No",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    infractions = await bot.wait_for('message',
                                                     check=lambda x: x.channel == channel and x.author == author)
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
                    whystaff = await bot.wait_for('message',
                                                  check=lambda x: x.channel == channel and x.author == author)
                    whystaff = whystaff.content

                    '''WHY MISC'''
                    embed = discord.Embed(title="What brought you to Miscellaneous, and what has kept you here?",
                                          description="Please make sure that you respond in one message",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    whymisc = await bot.wait_for('message',
                                                 check=lambda x: x.channel == channel and x.author == author)
                    whymisc = whymisc.content

                    '''Suggest'''
                    embed = discord.Embed(
                        title="What is something that you could suggest that could improve the guild?",
                        description="Please make sure that you respond in one message",
                        color=0x4b89e4)
                    await channel.send(embed=embed)
                    suggestion = await bot.wait_for('message',
                                                    check=lambda x: x.channel == channel and x.author == author)
                    suggestion = suggestion.content

                    '''SCENARIO 1'''
                    embed = discord.Embed(
                        title="You have just started as a trial officer and an officer starts arguing with another member. "
                              "This argument starts to get serious quite quickly. What do you do? ",
                        description="Make your answer as detailed as possible!",
                        color=0x4b89e4)
                    await channel.send(embed=embed)
                    scen1 = await bot.wait_for('message',
                                               check=lambda x: x.channel == channel and x.author == author)
                    scen1 = scen1.content

                    '''SCENARIO 2'''
                    embed = discord.Embed(
                        title="Suppose it's your first week of being a trial officer and you guild-mute a well-known player. "
                              "Your guildmates start spamming you calling you a bad officer and telling you to unmute them. "
                              "What would you do?",
                        description="Make your answer as detailed as possible!",
                        color=0x4b89e4)
                    await channel.send(embed=embed)
                    scen2 = await bot.wait_for('message',
                                               check=lambda x: x.channel == channel and x.author == author)
                    scen2 = scen2.content

                    '''SCENARIO 3'''
                    embed = discord.Embed(
                        title="Upon joining a game and you discover that a guild member is in your game and is hacking. "
                              "What do you do?",
                        description="Please make sure that you respond in one message",
                        color=0x4b89e4)
                    await channel.send(embed=embed)
                    scen3 = await bot.wait_for('message',
                                               check=lambda x: x.channel == channel and x.author == author)
                    scen3 = scen3.content

                    '''STAFF'''
                    embed = discord.Embed(title="Have you been staff in any other guild or on any server? "
                                                "If yes, which one?",
                                          description="Please make sure that you respond in one message",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    staff = await bot.wait_for('message',
                                               check=lambda x: x.channel == channel and x.author == author)
                    staff = staff.content

                    '''TIME'''
                    embed = discord.Embed(title="How much time do you have to contribute to the role? (Per day)",
                                          description="Please make sure that you respond in one message",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    time_ = await bot.wait_for('message',
                                               check=lambda x: x.channel == channel and x.author == author)
                    time_ = time_.content

                    '''GENERAL QUESTION'''
                    embed = discord.Embed(title="Tell us about a time you made a mistake within the last year. "
                                                "How did you deal with it? What did you learn?",
                                          escription="Make your answer as detailed as possible!",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    question = await bot.wait_for('message',
                                                  check=lambda x: x.channel == channel and x.author == author)
                    question = question.content

                    '''ANYTHING ELSE'''
                    embed = discord.Embed(title="Anything else you would like us to know?",
                                          color=0x4b89e4)
                    await channel.send(embed=embed)
                    random = await bot.wait_for('message',
                                                check=lambda x: x.channel == channel and x.author == author)
                    random = random.content

                    await channel.send("Great! You're done with the application!"
                                       "\nI'm working on compiling the application and I'll send it once I'm done compiling!")

                    embed = discord.Embed(title=f"{name}'s Staff Application", color=0x4b89e4)
                    embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
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
                        name="7) You have just started as a trial officer and an officer starts arguing with another member. This argument starts to get serious quite quickly. What do you do?",
                        value=scen1, inline=False)
                    embed.add_field(
                        name="8) Suppose it's your first week of being a trial officer and you guild-mute a well-known player. Your guildmates start spamming you calling you a bad officer and telling you to unmute them. What would you do?",
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

                else:
                    await channel.send(
                        "Since you don't meet the requirements, there's no point proceeding with the application. Kindly reapply once you meet all the requirements.")
                    break
            elif reply == "Gvg":
                await channel.edit(name=f"GvG-Application-{name}",
                                   category=discord.utils.get(channel.guild.categories, name="OTHER"))
                embed = discord.Embed(
                    title="To be eligible to apply for the GvG Team, you must meet any one of the following game-specific requirements.",
                    color=0x00FFFF)
                embed.add_field(name="Bedwars", value="500 Wins\n1.6 Final Kill-Death Ratio", inline=False)
                embed.add_field(name="Skywars", value="1000 Wins\n1.2 Kill-Death Ratio", inline=False)
                embed.add_field(name="Duels", value="2000 Wins\n1.5 Kill-Death Ratio", inline=False)
                embed.add_field(name="Polyvalent (All gamemodes)", value="Must fulfill all requirements", inline=False)
                await channel.send(embed=embed)

                req = await hypixel.get_data(name)
                if req["player"] is None:
                    embed = discord.Embed(title='Unknown IGN',
                                          description='Kindly create a new ticket to sync your name and then create another ticket for the GvG Application!',
                                          color=0xff0000)
                    await channel.send(embed=embed)
                else:
                    req = await hypixel.get_data(name)
                    uuid = req['player']['uuid']

                    x = 0
                    y = 0
                    z = 0

                    # Bedwars
                    bw_wins = int(req['player']['stats']['Bedwars']['wins_bedwars'])
                    bw_final_kills = int(req['player']['stats']['Bedwars']['final_kills_bedwars'])
                    bw_final_deaths = int(req['player']['stats']['Bedwars']['final_deaths_bedwars'])
                    bw_fkdr = bw_final_kills / bw_final_deaths
                    bw_fkdr = round(bw_fkdr, 2)

                    if bw_wins > 500:
                        x = x + 1
                    if bw_fkdr > 1.6:
                        x = x + 1

                    # Skywars
                    sw_wins_overall = int(req['player']['stats']['SkyWars']['wins'])
                    sw_wins_solo = int(req['player']['stats']['SkyWars']['wins_solo'])
                    sw_wins_doubles = int(req['player']['stats']['SkyWars']['wins_team'])
                    sw_kills = int(req['player']['stats']['SkyWars']['kills'])
                    sw_deaths = int(req['player']['stats']['SkyWars']['deaths'])
                    sw_kdr = sw_kills / sw_deaths
                    sw_kdr = round(sw_kdr, 2)
                    if sw_wins_overall > 1000:
                        y = y + 1
                    if sw_kdr > 1.2:
                        y = y + 1

                    # Duel
                    duels_wins = int(req['player']['stats']['Duels']['wins'])
                    duels_losses = int(req['player']['stats']['Duels']['losses'])
                    duels_kills = int(req['player']['stats']['Duels']['kills'])
                    duels_wlr = duels_wins / duels_losses
                    duels_wlr = round(duels_wlr, 2)

                    if duels_wins > 2000:
                        z = z + 1
                    if duels_wlr > 1.5:
                        z = z + 1

                    if x >= 2 and y >= 2 and z >= 2:
                        embed1 = discord.Embed(title="You're eligible for the Polyvalent GvG Team!",
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

                    elif x == 1 and y == 1 and z == 1:
                        embed1 = discord.Embed(
                            title="You're eligible for any two of the teams!\n You will be assigned to any two teams on the basis of your stats!",
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
                        embed1 = discord.Embed(title="You're eligible for the Bedwars and Skywars GvG Teams!",
                                               description="Kindly await staff assistance for further information!",
                                               color=0xff00f6)
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
                        embed1 = discord.Embed(title="You're eligible for the Bedwars and Duels GvG Teams!",
                                               description="Kindly await staff assistance for further information!",
                                               color=0xff00f6)
                        embed1.add_field(name="Bedwars Wins", value=f'`{bw_wins}`')
                        embed1.add_field(name="Bedwars FKDR", value=f'`{bw_fkdr}`')
                        embed1.add_field(name="Duels Wins", value=f'`{duels_wins}`')
                        embed1.add_field(name="Duels WLR;", value=f'`{duels_wlr}`')
                        embed1.set_footer(
                            text=f"Skywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}")
                        await channel.send(embed=embed1)
                        break

                    elif y >= 1 and z >= 1:
                        embed1 = discord.Embed(title="You're eligible for the Skywars and Duels GvG Teams!",
                                               description="Kindly await staff assistance for further information!",
                                               color=0xff00f6)
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
                        embed1 = discord.Embed(title="You're eligible for the Bedwars GvG Team!",
                                               description="Kindly await staff assistance for further information!",
                                               color=0xff00f6)
                        embed1.add_field(name="Bedwars Wins", value=f'`{bw_wins}`')
                        embed1.add_field(name="Bedwars FKDR", value=f'`{bw_fkdr}`')
                        embed1.set_footer(
                            text=f"Skywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}\nDuels wins - {duels_wins}\nDuels Kills - {duels_kills}\nDuels WLR - {duels_wlr}")
                        await channel.send(embed=embed1)
                        break
                    elif y >= 1:
                        embed1 = discord.Embed(title="You're eligible for the Skywars GvG Team!",
                                               description="Kindly await staff assistance for further information!",
                                               color=0xff00f6)
                        embed1.add_field(name="Skywars Wins (Overall)", value=f'`{sw_wins_overall}`')
                        embed1.add_field(name="Skywars Wins (Solo)", value=f'`{sw_wins_solo}`')
                        embed1.add_field(name="Skywars Wins (doubles)", value=f'`{sw_wins_doubles}`')
                        embed1.add_field(name="Skywars KDR", value=f'`{sw_kdr}`')
                        embed1.set_footer(
                            text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}\nDuels wins - {duels_wins}\nDuels WLR - {duels_wlr}")
                        await channel.send(embed=embed1)
                        break
                    elif z >= 1:
                        embed1 = discord.Embed(title="You're eligible for the Duels GvG Team!",
                                               description="Kindly await staff assistance for further information!",
                                               color=0xff00f6)
                        embed1.add_field(name="Duels Wins", value=f'`{duels_wins}`')
                        embed1.add_field(name="Duels WLR", value=f'`{duels_wlr}`')
                        embed1.set_footer(
                            text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}\nSkywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}")
                        await channel.send(embed=embed1)
                        break
                    else:
                        embed1 = discord.Embed(
                            title="You're ineligible to apply GvG Team because you don't meet the requirements!",
                            description="Kindly await staff assistance for further information!", color=0xcd5c5c)
                        embed1.set_footer(
                            text=f"Bedwars Wins - {bw_wins}\nBedwars FKDR - {bw_fkdr}\nSkywars Wins (Overall) - {sw_wins_overall}\nSkywars Wins (Solo) - {sw_wins_solo}\nSkywars Wins (Doubles) - {sw_wins_doubles}\nSkywars KDR - {sw_kdr}\nDuels wins - {duels_wins}\nDuels WLR - {duels_wlr}")
                        await channel.send(embed=embed1)
                        break

            elif reply == "Demotion":

                admin = discord.utils.get(channel.guild.roles, name="Admin")
                if admin in author.roles:
                    await channel.purge(limit=10)
                    embed = discord.Embed(title="Who would you like to demote?", description="Kindly mention them",
                                          color=0x00FFFF)
                    await channel.send(embed=embed)
                    user = await bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    user = user.mentions[0]

                    username = user.nick
                    if username is None:
                        username = user.name

                    await channel.edit(name=f"Demotion-{username}")

                    embed = discord.Embed(title=f"What's the reason behind {username}'s demotion?", color=0x00FFFF)
                    await channel.send(embed=embed)
                    reason = await bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    reason = reason.content

                    await channel.set_permissions(user, send_messages=True, read_messages=True,
                                                  add_reactions=True, embed_links=True,
                                                  attach_files=True, read_message_history=True,
                                                  external_emojis=True)
                    await channel.purge(limit=10)
                    embed = discord.Embed(title=f"{username} you are being demoted from the Miscellaneous staff team!",
                                          description=f"This is due to {reason}", color=0x8368ff)
                    await channel.send(embed=embed)
                    await channel.send(user.mention)
                    break
                else:
                    embed = discord.Embed(title="My massive computer brain thinks you made a mistake.", color=0xff0000)
                    embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
                    embed.add_field(name="If this is false", value="Type `No`", inline=False)
                    await channel.send(embed=embed)
                    mistake = await bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
                    mistake = mistake.content
                    mistake = mistake.capitalize()
                    if mistake == "Yes":
                        await channel.send("Great! Let's start over!")
                    else:
                        await channel.send(
                            "Hmm, seems like I'm dumb.\nKindly specify your reason behind creating this ticket and await staff assistance!")
                        break

            elif reply == "Other":
                await channel.edit(name=f"Unknown-{name}",
                                   category=discord.utils.get(channel.guild.categories, name="OTHER"))
                await channel.send(
                    "Okay. Kindly specify your reason behind creating this ticket and wait for staff to help you!")
                break
            else:
                embed = discord.Embed(title="My massive computer brain thinks you made a mistake.", color=0xff0000)
                embed.add_field(name="If this is true", value="Type `Yes`", inline=False)
                embed.add_field(name="If this is false", value="Type `No`", inline=False)
                await channel.send(embed=embed)
                mistake = await bot.wait_for('message', check=lambda x: x.channel == channel and x.author == author)
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


@tasks.loop(count=1)
async def ticketer():
    print("ticketer was started!")
    await bot.ticket_channel.purge(limit=1)

    ticket_embed = discord.Embed(title="Click the following button to create a ticket!",
                                 description="If you're facing any issues, message a staff member!\n\nOnce you create the ticket, you'll see the bot's prompt. Respond appropriately.",
                                 color=0x8368ff)
    creating_ticket = discord.Embed(title="Ticket successfully created!", color=0x00A86B)

    ticket_creation = Button(style=ButtonStyle.blue, label="✉️Create Ticket", id="embed")

    await bot.ticket_channel.send(embed=ticket_embed, components=[ticket_creation])

    while True:
        click = await bot.wait_for("button_click",
                                   check=lambda x: x.channel == bot.ticket_channel)
        clicker_id = click.author.id
        clicker = bot.misc_guild.get_member(clicker_id)
        await click.respond(type=InteractionType.ChannelMessageWithSource, embed=creating_ticket)

        name = await hypixel.name_grabber(clicker)

        category = discord.utils.get(bot.misc_guild.categories, name="🎫 Ticket Section")
        ticket_channel = await bot.misc_guild.create_text_channel(f"ticket-{name}",
                                                                  category=category)
        print("Channel created")
        await ticket_channel.set_permissions(bot.misc_guild.get_role(bot.misc_guild.id), send_messages=False,
                                             read_messages=False)
        await ticket_channel.set_permissions(bot.staff, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(bot.t_officer, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(clicker, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(bot.new_member_role, send_messages=False,
                                             read_messages=False,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.send(f"{clicker.mention}")



@tasks.loop(count=1)
async def after_cache_ready():
    # replace the below IDs in testing servers - make sure to revert before committing.
    bot.error_channel = bot.get_channel(523743721443950612)
    bot.dnkl_channel = bot.get_channel(629564802812870657)
    bot.ticket_channel = bot.get_channel(650248396480970782)
    bot.logs = bot.get_channel(714821811832881222)
    bot.misc_guild = bot.get_guild(522586672148381726)
    bot.guild_master = discord.utils.get(bot.misc_guild.roles, name="Guild Master")
    bot.admin = discord.utils.get(bot.misc_guild.roles, name="Admin")
    bot.staff = discord.utils.get(bot.misc_guild.roles, name="Staff")
    bot.t_officer = discord.utils.get(bot.misc_guild.roles, name="Trial Officer")
    bot.former_staff = discord.utils.get(bot.misc_guild.roles, name="Former Staff")
    bot.new_member_role = discord.utils.get(bot.misc_guild.roles, name="New Member")
    bot.guest = discord.utils.get(bot.misc_guild.roles, name="Guest")
    bot.member_role = discord.utils.get(bot.misc_guild.roles, name="Member")
    bot.active_role = discord.utils.get(bot.misc_guild.roles, name="Active")
    bot.inactive_role = discord.utils.get(bot.misc_guild.roles, name="Inactive")
    bot.awaiting_app = discord.utils.get(bot.misc_guild.roles, name="Awaiting Approval")
    bot.ally = discord.utils.get(bot.misc_guild.roles, name="Ally")
    bot.server_booster = discord.utils.get(bot.misc_guild.roles, name="Server Booster")
    bot.tag_allowed_roles = (bot.active_role, bot.staff, bot.former_staff, bot.server_booster)
    bot.ticket_categories = ('RTickets', '🎫 Ticket Section', 'OTHER', 'REPORTS', 'MILESTONES', 'DNKL')
    bot.misc_allies = ("XL", "Lucid", "Cronos", "OUT")
    bot.adminids = [x.id for x in bot.admin.members]
    bot.staff_names = [await hypixel.name_grabber(member) for member in bot.staff.members]

    DiscordComponents(bot)
    chat_exporter.init_exporter(bot)

    #ticketer.start()

    print("Cache filled and task complete.")


@after_cache_ready.before_loop
async def before_cache_loop():
    print("Waiting for cache...")
    await bot.wait_until_ready()


after_cache_ready.start()
bot.run(bot.token)
