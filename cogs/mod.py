import discord
from discord.ext import commands

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    # Mute
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes the mentioned user indefinately!
        """
        if reason is None:
            reason = f'Muted by: {ctx.author.name}'

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        embed = discord.Embed(title="User Muted!",
                            description=f"**{member}** was muted by **{ctx.message.author}**!",
                            color=0xff00f6)
        await ctx.send(embed=embed)


    # Unmute
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes the mentioned user
        """
        if reason is None:
            reason = f'Unmuted by: {ctx.author.name}'

        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        embed = discord.Embed(title="User unmuted!",
                            description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author),
                            color=0xff00f6)
        await ctx.send(embed=embed)


    # Clear
    @commands.command(aliases=["purge", "prune"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, *, reason=None):
        """Clears the chat based on the given amount!
        """
        if reason is None:
            reason = f'Cleared by: {ctx.author.name}'

        await ctx.channel.purge(limit=amount)


    # Kick
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks the mentioned user!
        """
        if reason is None:
            reason = f'Kicked by: {ctx.author.name}'

        await member.kick(reason=reason)
        await ctx.send(f"{member} was kicked!")

    # Ban
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans the mentioned user!
        """
        if reason is None:
            reason = f'Banned by: {ctx.author.name}'

        await member.ban(reason=reason)
        await ctx.send(f"{member} was banned!")

    # unban
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason=None):
        """Unbans the user!
        """
        if reason is None:
            reason = f'Unbanned by: {ctx.author.name}'

        await ctx.guild.unban(user)
        await ctx.send(f'{user.mention} has been unbanned')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, user: discord.Member, *, reason = None):
        """Softbans a user!

        Bans and then unbans a user to remove all of their messages
        """
        if reason is None:
            reason = f'Softbanned by: {ctx.author.name}'

        await ctx.guild.ban(user, reason=reason)
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f'{user.name} has been softbanned.')

def setup(bot):
    bot.add_cog(Moderation(bot))