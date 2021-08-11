import asyncio

import aiohttp
import discord
import io
import chat_exporter
from discord.ext import commands

from cogs.utils import hypixel


class Tickets(commands.Cog, name="Tickets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['reg', 'verify'])
    async def register(self, ctx, name):
        async with ctx.channel.typing():
            author = ctx.author
            if str(ctx.channel) == "register":
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

                        guild_name = await hypixel.get_guild(name)

                        nick = await author.edit(nick=ign)
                        if guild_name == "Miscellaneous":
                            await ctx.author.remove_roles(self.bot.new_member_role, reason="Register")

                            await ctx.channel.purge(limit=1)
                            embed = discord.Embed(title="Registration successful!")
                            embed.add_field(name=ign,
                                            value="Member of Miscellaneous")

                            embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                            await ctx.send(embed=embed)
                            await ctx.author.add_roles(self.bot.member_role, reason="Register")

                        elif guild_name in self.bot.misc_allies:
                            for guild in self.bot.misc_allies:
                                if guild == guild_name:
                                    gtag = await hypixel.get_gtag(guild)
                                    if ctx.author.nick is None or str(gtag) not in ctx.author.nick:
                                        ign = ign + " " + str(gtag)
                                    await ctx.author.edit(nick=ign)
                                    await ctx.author.remove_roles(self.bot.new_member_role, reason="Register")
                                    await ctx.author.add_roles(self.bot.guest, self.bot.ally, reason="Register")

                                    await ctx.channel.purge(limit=1)
                                    embed = discord.Embed(title="Registration successful!")
                                    embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                    embed.add_field(name=ign, value=f"Member of {guild}")
                                    await ctx.send(embed=embed)

                        elif guild_name != "Miscellaneous" and guild_name not in self.bot.misc_allies:
                            await ctx.author.remove_roles(self.bot.new_member_role, reason="Register")
                            await ctx.author.add_roles(self.bot.awaiting_app, reason="Register")
                            if nick is None:
                                nick = author.name

                            await ctx.channel.purge(limit=1)
                            embed = discord.Embed(title="Registration successful!")
                            embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
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
                            await ticket_channel.set_permissions(self.bot.t_officer, send_messages=True,
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
        transcript = await chat_exporter.export(ctx.channel)
        if transcript is None:
            pass
        else:
            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                           filename=f"deleted-{ctx.channel.name}.html")

        if self.bot.staff in ctx.author.roles:
            if ctx.channel.category.name in self.bot.ticket_categories:
                name = ctx.channel.name
                embed = discord.Embed(title='This ticket will be deleted in 10 seconds!', description='',
                                      color=0xDE3163)
                msg = await ctx.send(embed=embed)
                await asyncio.sleep(10)
                await discord.TextChannel.delete(ctx.channel)

                name = await hypixel.name_grabber(ctx.author)
                embed = discord.Embed(title=f'{ctx.channel.name} was deleted by {name}',
                                      description="", color=0x8368ff)
                await self.bot.logs.send(embed=embed)
                await self.bot.logs.send(file=transcript_file)

    @commands.command()
    @commands.has_any_role(538015368782807040, 522588122807271424)
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
    @commands.has_any_role(538015368782807040, 522588122807271424)
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
    @commands.has_any_role(538015368782807040, 522588122807271424)
    async def rename(self, ctx, *, channel_name):
        """Renames the channel
        """
        await ctx.message.delete()
        if ctx.channel.category.name in self.bot.ticket_categories:
            channel_name = channel_name.replace(" ", "-")
            await ctx.channel.edit(name=f"{channel_name}")

    @commands.command()
    @commands.has_any_role(538015368782807040, 522588122807271424)
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

            embed = discord.Embed(title="Transcript creation successful!",
                                  color=0x00A86B)
            await ctx.send(embed=embed)
            await ctx.send(file=transcript_file)

    @commands.command()
    @commands.has_role(522588118251995147)
    async def accept(self, ctx, member: discord.Member):
        """Used to accept staff applications. This command must be typed in the application channel. It doesn't work elsewhere.
        """
        if ctx.channel.category.name in self.bot.ticket_categories:
            embed = discord.Embed(title=f"Congratulations {member.name}, your staff application has been accepted!",
                                  description="Please view the following as they'll help you become a better staff member!",
                                  color=0x8368ff)
            embed.set_footer(text="https://bit.ly/MiscStaffGuide\n"
                                  "#staff-faq")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role(522588118251995147, 522590574734213120)
    async def deny(self, ctx, member: discord.Member, channel: discord.TextChannel):
        """Used to deny staff applications. This command can be used in any channel, provided, the syntax is met.
        """
        name = await hypixel.name_grabber(member)

        embed = discord.Embed(title=f"{name}, your application has been denied!",
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

            more = await self.bot.wait_for('message',
                                           check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            more = more.content
            more = more.capitalize()

            if more in ('Yes', 'Yeah', 'Ye', 'Yea'):
                continue
            else:
                await channel.send(embed=embed)
                break

    @commands.command()
    async def new(self, ctx):
        name = await hypixel.name_grabber(ctx.author)

        category = discord.utils.get(self.bot.misc_guild.categories, name="🎫 Ticket Section")
        ticket_channel = await self.bot.misc_guild.create_text_channel(f"ticket-{name}",
                                                                  category=category,
                                                                  topic="<:t:869239368060112906><:i:869239367942697010><:c:869239368383074414>"
                                                                        "<:k:869239367854612480><:e:869239368517287936><:t:869239368060112906>")
        creating_ticket = discord.Embed(title="Click here to go to your ticket!",
                                        url=f"https://discord.com/channels/522586672148381726/{ticket_channel.id}",
                                        color=0x00A86B)
        creating_ticket.set_author(name="Ticket successfully created!")

        await ctx.send(embed=creating_ticket)

        await ticket_channel.set_permissions(self.bot.misc_guild.get_role(self.bot.misc_guild.id), send_messages=False,
                                             read_messages=False)
        await ticket_channel.set_permissions(self.bot.staff, send_messages=True, read_messages=True,
                                             add_reactions=True, embed_links=True,
                                             attach_files=True,
                                             read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(self.bot.t_officer, send_messages=True, read_messages=True,
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
