import io

import chat_exporter
import discord
from discord.ext import commands

from cogs.utils import utilities as utils


class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    # Mute
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes the mentioned user indefinately!
        """
        name = await utils.name_grabber(ctx.author)
        if reason is None:
            reason = f'Muted by: {name}'

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        embed = discord.Embed(title="User Muted!",
                              description=f"**{member}** was muted by **{name}**!",
                              color=0xff00f6)
        await ctx.send(embed=embed)
        embed = discord.Embed(title=f'{name} muted {member.name}',
                              description=f"**Reason:** {reason}", color=0x8368ff)
        await self.bot.logs.send(embed=embed)

    # Unmute
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes the mentioned user
        """
        name = await utils.name_grabber(ctx.author)
        if reason is None:
            reason = f'Unmuted by: {name}'

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(muted_role)
        embed = discord.Embed(title="User unmuted!",
                              description=f"**{member}** was unmuted by **{name}**!",
                              color=0xff00f6)
        await ctx.send(embed=embed)
        embed = discord.Embed(title=f'{name} unmuted {member.name}',
                              description=f"**Reason:** {reason}", color=0x8368ff)
        await self.bot.logs.send(embed=embed)

    # Clear
    @commands.command(aliases=["purge", "prune"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, *, reason=None):
        """Clears the chat based on the given amount!
        """
        name = await utils.name_grabber(ctx.author)
        transcript = await chat_exporter.export(ctx.channel, limit=amount)
        if transcript is None:
            pass
        else:
            transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                           filename=f"purge-{ctx.channel.name}-by-{name}.html")

        if self.bot.staff in ctx.author.roles:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
            embed = discord.Embed(title=f'{name} purged {amount} messages in {ctx.channel.name}',
                                  description=f"**Reason:** {reason}", color=0x8368ff)
            await self.bot.logs.send(embed=embed)
            '''await self.bot.logs.send(file=transcript_file)'''

    # Kick
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks the mentioned user!
        """
        name = await utils.name_grabber(ctx.author)
        if reason is None:
            reason = f'Kicked by: {name}'

        await member.kick(reason=reason)
        await ctx.send(f"{member} was kicked!")
        embed = discord.Embed(title=f'{name} kicked {member.name}',
                              description=f"**Reason:** {reason}", color=0x8368ff)
        await self.bot.logs.send(embed=embed)

    # Ban
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans the mentioned user!
        """
        name = await utils.name_grabber(ctx.author)
        if reason is None:
            reason = f'Banned by: {name}'

        await member.ban(reason=reason)
        await ctx.send(f"{member} was banned!")
        embed = discord.Embed(title=f'{name} banned {member.name}',
                              description=f"**Reason:** {reason}", color=0x8368ff)
        await self.bot.logs.send(embed=embed)

    # unban
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, *, reason=None):
        """Unbans the user!
        """
        name = await utils.name_grabber(ctx.author)
        if reason is None:
            reason = f'Unbanned by: {name}'

        await ctx.guild.unban(member)
        await ctx.send(f'{member.mention} has been unbanned')
        embed = discord.Embed(title=f'{name} unbanned {member.name}',
                              description=f"**Reason:** {reason}", color=0x8368ff)
        await self.bot.logs.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        """Softbans a user!

        Bans and then unbans a user to remove all of their messages
        """
        name = await utils.name_grabber(ctx.author)
        if reason is None:
            reason = f'Softbanned by: {name}'

        await ctx.guild.ban(member, reason=reason)
        await ctx.guild.unban(member, reason=reason)
        await ctx.send(f'{member.name} has been softbanned.')
        embed = discord.Embed(title=f'{name} softbanned {member.name}',
                              description=f"**Reason:** {reason}", color=0x8368ff)
        await self.bot.logs.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
