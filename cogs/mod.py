import discord
from discord.ext import commands

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    # Mute
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member):
        """Mutes the mentioned user indefinately!
        """
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)
        embed = discord.Embed(title="User Muted!",
                            description=f"**{member}** was muted by **{ctx.message.author}**!",
                            color=0xff00f6)
        await ctx.send(embed=embed)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                                description="Your role lacks permissions to mute a user", color=0xff0000)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=embed)

    # Unmute
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member):
        """Mutes the mentioned user
        """
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        embed = discord.Embed(title="User unmuted!",
                            description="**{0}** was unmuted by **{1}**!".format(member, ctx.message.author),
                            color=0xff00f6)
        await ctx.send(embed=embed)

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                                description="Your role lacks permissions to unmute a user", color=0xff0000)
            await ctx.channel.purge(limit=1)
            await ctx.send(embed=embed)

    # Clear
    @commands.command(aliases=["purge", "prune"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clears the chat based on the given amount!
        """
        await ctx.channel.purge(limit=amount)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title='Please specify the number of messages to be deleted',
                                description='clear `amount of messages`', color=0xff0000)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title='Your soul lacks the strength to utilize this command!',
                                description="Your role lacks permissions to clear chat", color=0xff0000)
            await ctx.send(embed=embed)

    # Kick
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks the mentioned user!
        """
        await member.kick(reason=reason)
        await ctx.send(f"{member} was kicked!")

    @kick.error
    async def kick_error(self, ctx, error):
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

    # Ban
    @commands.command()
    @commands.has_permissions(ban_members=True, kick_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans the mentioned user!
        """
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member} was banned!")
        except Exception as e:
            print(e)
            await self.bot.error_channel.send(f"Error in {ctx.channel.name} while trying to use `ban`\n{e}\n<@!326399363943497728>")

    @ban.error
    async def ban_error(self, ctx, error):
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
    @commands.command()
    @commands.has_permissions(ban_members=True, kick_members=True)
    async def unban(self, ctx, *, member):
        """Unbans the user!
        """
        banned_users = await ctx.guild.bans()
        member_name, member_discrimitator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.member_discrimitator) == (member_name, member_discrimitator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned')
                return
                
    @unban.error
    async def unban_error(self, ctx, error):
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

def setup(bot):
    bot.add_cog(Moderation(bot))