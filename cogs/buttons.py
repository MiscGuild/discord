from io import BytesIO

import aiohttp
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption

from cogs.utils import utilities as utils


class Roles(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reaction_roles(self, ctx):
        reaction_roles = discord.Embed(title="To get your desired role, click its respective button!",
                                       description="<:sb:732824932177805405> __**SkyBlock**__\n*Gives you the access to the SkyBlock category!*\n\n"
                                                   "<:minigames:732825420235407400> __**Discord Minigames**__\n*Allows you to play some Discord minigames!*\n\n"
                                                   "👨‍👩‍👧‍👦 __**SMP Server Access**__\n*This role allows you to visit our SMP!*\n\n"
                                                   "🎉 __**Giveaways/Events**__\n*React so you don't miss any giveaway or event*\n\n"
                                                   "📖 __**Storytimes**__\n*Get pinged whenever a storytime happens* ",
                                       color=0x8368ff)
        pronoun_embed = discord.Embed(title="Please select your pronouns", description=":man: He/Him"
                                                                                       "\n:woman: She/Her"
                                                                                       "\n:rainbow_flag: They/Them"
                                                                                       "\n:question: Other",
                                      color=0x8368ff)
        await ctx.send(
            embed=reaction_roles,
            components=[
                [
                    Button(style=ButtonStyle.grey, label="Skyblock", emoji=self.bot.get_emoji(732824932177805405),
                           id="732279654261588048"),
                    Button(style=ButtonStyle.grey, label="Discord Minigames",
                           emoji=self.bot.get_emoji(732825420235407400), id="732824611175006239"),
                    Button(style=ButtonStyle.grey, label="SMP Server Access", emoji="👨‍👩‍👧‍👦",
                           id="763704865297268776"),
                    Button(style=ButtonStyle.grey, label="Giveaways/Events", emoji="🎉", id="780717935140012052"),
                    Button(style=ButtonStyle.grey, label="Storytimes", emoji="📖", id="855657894518325258"),
                ]
            ],
        )
        await ctx.send(
            embed=pronoun_embed,
            components=[
                [
                    Select(placeholder="Select max 1!", options=[
                        SelectOption(label="He/Him", value="849830869036040212", emoji="👨"),
                        SelectOption(label="She/Her", value="849830936434704404", emoji="👩"),
                        SelectOption(label="They/Them", value="849831004310077441", emoji="🏳️‍🌈"),
                        SelectOption(label="Other", value="855598846843551744", emoji="❓")
                    ], max_values=1, min_values=0)
                ]
            ]
        )

    @commands.command()
    @commands.is_owner()
    async def ticket_embed(self, ctx):
        embed = discord.Embed(title="Tickets", description="Tickets can be created for any of the following reasons:-"
                                                           "\n> Do Not Kick List"
                                                           "\n> Discord Nick/Role Change"
                                                           "\n> Problems/Queries/Complaint"
                                                           "\n> Player Report"
                                                           "\n> Milestone"
                                                           "\n> Staff Application"
                                                           "\n> Event"
                                                           "\n> Other"
                                                           "\nOnce you have created a ticket by clicking the button, you will be linked to a ticket in the \":ticket: Ticket Section\" category.\n"
                                                           "When you open the ticket, you will be greeted by a message from the Miscellaneous Bot. "
                                                           "The bot will ask you to choose the reason behind the creation of your ticket from a given list. Choose the appropriate reason and then proceed!\n"
                                                           "Once you have created your ticket, staff will respond within 24 hours.",
                              color=0x8368ff)
        embed.add_field(name="Do Not Kick List",
                        value="Once you create  the ticket you  will see <@736266884147576903>'s prompts. "
                              "Respond to the prompts appropriately.\n"
                              "You  must have a valid reason for applying and also meet the DNKL requiremnets.\n"
                              "Accepted Reasons:\n"
                              "> School\n"
                              "> Medical Reasons\n"
                              "> Situations out of your control\n"
                              "> Vacation\n\n"
                              "If your account is banned for more than 30 days, then it will be temporarily kicked until it's unbanned. We reserve the right to do this for any bans under 30 days as well.",
                        inline=False)
        embed.add_field(name="Discord Nick/Role/Tag Change",
                        value="Once you create  the ticket you  will see <@736266884147576903>'s prompts. "
                              "Respond to the prompts appropriately.\n"
                              "*If you aren't able to change your tag, it's because you don't meet the tag requirements.",
                        inline=False)
        embed.add_field(name="Problems/Queries/Complaints",
                        value="If you face difficulty in anything, create a ticket! The Miscellaneous Staff Team will gladly help you!",
                        inline=False)
        embed.add_field(name="Player Report",
                        value="When reporting a player, you're expected to explain the situation in maximum detail. Providing the following is considered the bare minimum:-\n"
                              "> Username of the accused\n"
                              "> Explanantion of the offense\n"
                              "> Time of offense\n"
                              "> Proof of offense\n"
                              "If you wish to report a staff member, DM <@!326399363943497728>",
                        inline=False)
        embed.add_field(name="Milestone",
                        value="Upon selection of this category, you'll be prompted by the bot and be asked to give the milestone that you achieved along with proof of its feat. "
                              "Once that's done, staff will review your milestone and if it is accepted, it will be included in the following Sunday's milestone post!",
                        inline=False)
        embed.add_field(name="Staff Application",
                        value="Upon creation, you will be prompted by the bot. After you're done with your application, the Miscellaneous Staff Team will respond within 48 hours.",
                        inline=False)
        embed.set_footer(text="Hit the following button create a ticket!")
        embed.set_thumbnail(
            url=f"https://images-ext-1.discordapp.net/external/ziYSZZe7dPyKDYLxA1s2jqpKi-kdCvPFpPaz3zft-wo/%3Fwidth%3D671%26height%3D671/https/media.discordapp.net/attachments/523227151240134664/803843877999607818/misc.png")
        await ctx.channel.purge(limit=1)

        url = f"https://media.discordapp.net/attachments/650248396480970782/873866686049189898/tickets.jpg"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                image_data = BytesIO(await resp.read())
                await session.close()

        # await ctx.send(file=discord.File(image_data, 'tickets.jpg'))

        ticket_creation = Button(style=ButtonStyle.blue, label="✉️Create Ticket", id="ticketer")

        await ctx.channel.send(embed=embed, components=[ticket_creation])

    @commands.Cog.listener()
    async def on_button_click(self, res):
        role_ids = ["732279654261588048",
                    "732824611175006239",
                    "763704865297268776",
                    "780717935140012052",
                    "855657894518325258"]
        if res.component.id in role_ids:
            member = self.bot.misc_guild.get_member(int(res.user.id))
            role = self.bot.misc_guild.get_role(int(res.component.id))
            if role in member.roles:
                await member.remove_roles(role, reason="Pressed Button, removed role")
                await res.respond(content=f"Removed {res.component.label} role from you.")
            elif role not in member.roles:
                await member.add_roles(role, reason="Pressed Button, added role")
                await res.respond(content=f"Added {res.component.label} role to you.")
        elif res.component.id == "ticketer":
            member = self.bot.misc_guild.get_member(int(res.user.id))

            name = await utils.name_grabber(member)

            category = discord.utils.get(self.bot.misc_guild.categories, name="🎫 Ticket Section")
            ticket_channel = await self.bot.misc_guild.create_text_channel(f"ticket-{name}",
                                                                           category=category,
                                                                           topic="<:t:869239368060112906><:i:869239367942697010><:c:869239368383074414>"
                                                                                 "<:k:869239367854612480><:e:869239368517287936><:t:869239368060112906>")
            creating_ticket = discord.Embed(title="Click here to go to your ticket!",
                                            url=f"https://discord.com/channels/522586672148381726/{ticket_channel.id}",
                                            color=0x00A86B)
            creating_ticket.set_author(name="Ticket successfully created!")

            await res.respond(embed=creating_ticket)

            await ticket_channel.set_permissions(self.bot.misc_guild.get_role(self.bot.misc_guild.id),
                                                 send_messages=False,
                                                 read_messages=False)
            await ticket_channel.set_permissions(self.bot.staff, send_messages=True, read_messages=True,
                                                 add_reactions=True, embed_links=True,
                                                 attach_files=True,
                                                 read_message_history=True, external_emojis=True)
            await ticket_channel.set_permissions(self.bot.t_officer, send_messages=True, read_messages=True,
                                                 add_reactions=True, embed_links=True,
                                                 attach_files=True,
                                                 read_message_history=True, external_emojis=True)
            await ticket_channel.set_permissions(member, send_messages=True, read_messages=True,
                                                 add_reactions=True, embed_links=True,
                                                 attach_files=True,
                                                 read_message_history=True, external_emojis=True)
            await ticket_channel.set_permissions(self.bot.new_member_role, send_messages=False,
                                                 read_messages=False,
                                                 add_reactions=True, embed_links=True,
                                                 attach_files=True,
                                                 read_message_history=True, external_emojis=True)
            await ticket_channel.send(f"{member.mention}")

    @commands.Cog.listener()
    async def on_select_option(self, res):
        role_ids = [849830869036040212,
                    849830936434704404,
                    849831004310077441,
                    855598846843551744]
        if type(res.component) == list:
            member = self.bot.misc_guild.get_member(int(res.user.id))
            for role in res.component:
                if int(role.value) in role_ids:
                    cached_role = self.bot.misc_guild.get_role(int(role.value))
                    if cached_role in member.roles:
                        await member.remove_roles(cached_role, reason=f"Pronoun role: {role.label} Removed")
                        await res.respond(content=f"Removed {role.label}")
                    elif cached_role not in member.roles:
                        for x in role_ids:
                            await member.remove_roles(self.bot.misc_guild.get_role(x),
                                                      reason="Pronouns Duplicate Prevention")
                        await member.add_roles(cached_role, reason=f"Pronoun role: {role.label} Given")
                        await res.respond(content=f"Added {role.label}")


        else:
            pass


def setup(bot):
    DiscordComponents(bot)
    bot.add_cog(Roles(bot))
