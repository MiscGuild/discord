import discord
from discord.ext import commands
import asyncio
import aiohttp
from cogs.utils import hypixel

class Tickets(commands.Cog, name="Tickets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['reg', 'verify'])
    async def register(self, ctx, name):
        try:
            async with ctx.channel.typing():
                author = ctx.author
                if str(ctx.channel) == "register":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                            request = await resp.json(content_type=None)

                        if resp.status != 200:
                            await ctx.send('Please enter a valid ign!')
                        else:
                            ign = request['name']
                            uuid = request['id']

                            guild_name = await hypixel.get_guild(name)
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
                                embed = discord.Embed(title="Registration successful!")
                                embed.add_field(name=ign,
                                                value="Member of Miscellaneous")

                                embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                await ctx.send(embed=embed)
                                await ctx.author.add_roles(member)

                            elif guild_name == "XL":
                                await ctx.author.remove_roles(newmember)
                                await ctx.author.add_roles(guest, xl_ally)


                                await ctx.channel.purge(limit=1)
                                embed = discord.Embed(title="Registration successful!")
                                embed.set_thumbnail(url=f'https://visage.surgeplay.com/full/832/{uuid}')
                                embed.add_field(name=ign, value="Member of XL")
                                await ctx.send(embed=embed)

                            elif guild_name not in ("Miscellaneous", "XL"):
                                await ctx.author.remove_roles(newmember)
                                await ctx.author.add_roles(awaiting_app)
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
                                                value=f"•  {format(self.bot.active,',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="DNKL Eligibility",
                                                value=f"•  {format(self.bot.dnkl,',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="Resident",
                                                value=f"•  {format(self.bot.resident_req,',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="Member",
                                                value=f"•  {format(self.bot.inactive,',d')} Weekly Guild Experience",
                                                inline=False)
                                embed.add_field(name="New Member",
                                                value=f"•  {format(self.bot.new_member,',d')} Daily Guild Experience",
                                                inline=False)
                                embed.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                                                    "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
                                await ctx.author.send(embed=embed)
                        await session.close()

                else:
                    await ctx.send('This command can only be used in the registration channel!')
        except Exception as e:
            print(e)
            await self.bot.error_channel.send(f"Error in {ctx.channel.name} while trying to use `register`\n{e}\n<@!326399363943497728>")

    @commands.command(aliases=['del'])
    async def delete(self, ctx):
        """Deletes the ticket channel the command is used in.
        """
        try:
            logs = self.bot.get_channel(714821811832881222)
            Staff = discord.utils.get(ctx.guild.roles, name="Staff")
            if Staff in ctx.author.roles:
                if ctx.channel.category.name in ('RTickets',  '🎫 Ticket Section', 'OTHER', 'REPORTS', 'MILESTONES', 'DNKL','EVENT'):
                    name = ctx.channel.name
                    embed = discord.Embed(title='This ticket will be deleted in 10 seconds!', description='', color=0xDE3163)
                    msg = await ctx.send(embed=embed)
                    await asyncio.sleep(10)
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
            print(e)
            await self.bot.error_channel.send(f"Error in {ctx.channel.name}\n{e}\n<@!326399363943497728>")

    @commands.command()
    @commands.has_role(522588118251995147)
    async def accept(self, ctx,  member: discord.Member):
        """Used to accept staff applications. This command must be typed in the application channel. It doesn't work anywhere else.
        """
        try:
            if ctx.channel.category.name in ('RTickets', '🎫 Ticket Section', 'OTHER', 'REPORTS', 'MILESTONES', 'DNKL'):
                embed = discord.Embed(title=f"Congratulations {member.name}, your staff application has been accepted!", description="Please view the following as they'll help you become a better staff member!", color=0x8368ff)
                embed.set_footer(text="https://bit.ly/MiscStaffGuide\n"
                                    "#staff-faq")
                await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await self.bot.error_channel.send(f"Error in {ctx.channel.name} while running `deny`\n{e}\n<@!326399363943497728>")
    @accept.error
    async def accept_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='Please specify the player to be accepted! The syntax is as follows',
                                description="accept `Discord @`", color=0xff0000)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role(522588118251995147, 522590574734213120)
    async def deny(self, ctx, member: discord.Member, channel: discord.TextChannel):
        """Used to deny staff applications. This command can be used in any channel, provided, the syntax is met.
        """
        try:
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
                    question = await self.bot.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                    question = question.content
                    if str(question) in ("1","2","3","4","5","6","7","8","9","10","11","12","13","14"):
                        question = question_number.get(int(question), 'None')
                        break
                    else:
                        await ctx.send("Please respond with a valid number. (1-14)")

                await ctx.send(f"`{question}`"
                            "\n**What was the issue that you found with their reply?**")
                critique = await self.bot.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
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


                more = await self.bot.wait_for('message', check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                more = more.content
                more = more.capitalize()

                if more in ('Yes', 'Yeah', 'Ye', 'Yea'):
                    continue
                else:
                    await channel.send(embed=embed)
                    break
        except Exception as e:
            print(e)
            await self.bot.error_channel.send(f"Error in {ctx.channel.name} while running `deny`\n{e}\n<@!326399363943497728>")
    @deny.error
    async def deny_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='Please specify the player to be denied! The syntax is as follows',
                                description="deny `Discord @` `Discord Channel #`", color=0xff0000)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def ticketss(self, ctx):
        embed = discord.Embed(title='Tickets',
                            description="Tickets can be created for any of the following reasons:-\n"
                                        "> Do Not Kick List\n"
                                        "> Discord Nick/Role Change\n"
                                        "> Problems/Queries/Complaint/Suggestion\n"
                                        "> Reporting a player\n"
                                        "> Milestone\n"
                                        "> Staff Application\n"
                                        "> Event\n"
                                        "> Other\n"
                                        "The ticket reasons have been explained in detail towards the end of this message.\n"
                                        " Once you have created a ticket by reacting to the bot's message, you will see that there is a new ticket in the \"🎫 Ticket Section\" category.\n"
                                        " When you open the ticket, you will be greeted by a message from the Miscellaneous Bot.\n"
                                        " The bot will ask you to choose the reason behind the creation of your ticket from a given list."
                                        " Choose the appropriate reason and then proceed!\n"
                                        "Once you have created your ticket, staff will respond within 24 hours.\n",color= 0x8368ff)
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/650248396480970782/727875702187229234/Tickets.png?width=1440&height=360')
        embed2 = discord.Embed(title='', description="**Do Not Kick List**:-"
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
                                                    "> Explanation about the offense\n"
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

def setup(bot):
    bot.add_cog(Tickets(bot))
