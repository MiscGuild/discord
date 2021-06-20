import discord
from discord.ext import commands
import asyncio
import aiohttp
from utils import hypixel

class Tickets(commands.Cog, name="Tickets"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['Register', 'reg', 'Reg', 'Verify', 'verify'])
    async def register(self, ctx, name):
        try:
            async with ctx.channel.typing():
                author = ctx.author
                if str(ctx.channel) == "register":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
                            request = resp
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
                                            value=f"•  {format(self.client.active,',d')} Weekly Guild Experience",
                                            inline=False)
                            embed.add_field(name="DNKL Eligibility",
                                            value=f"•  {format(self.client.dnkl,',d')} Weekly Guild Experience",
                                            inline=False)
                            embed.add_field(name="Resident",
                                            value=f"•  {format(self.client.resident_req,',d')} Weekly Guild Experience",
                                            inline=False)
                            embed.add_field(name="Member",
                                            value=f"•  {format(self.client.inactive,',d')} Weekly Guild Experience",
                                            inline=False)
                            embed.add_field(name="New Member",
                                            value=f"•  {format(self.client.new_member,',d')} Daily Guild Experience",
                                            inline=False)
                            embed.set_footer(text="You are considered a New Member for the first 7 days after joining the guild"
                                                "\nIf you fail to meet the New Member/Member requirements, you will be kicked!")
                            await ctx.author.send(embed=embed)
                else:
                    await ctx.send('This command can only be used in the registration channel!')
        except Exception as e:
            error_channel = self.client.get_channel(523743721443950612)
            print(e)
            await error_channel.send(f"Error in {ctx.channel.name} while trying to use `register`\n{e}\n<@!326399363943497728>")

def setup(bot):
    bot.add_cog(Tickets(bot))