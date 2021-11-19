from discord.ext import commands

class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # @commands.has_permissions(kick_members=True)
    # async def mute(self, ctx, member: discord.Member, *, reason=None):


    # @commands.command()
    # @commands.has_permissions(kick_members=True)
    # async def unmute(self, ctx, member: discord.Member, *, reason=None):


    # @commands.command(aliases=["purge", "prune"])
    # @commands.has_permissions(manage_messages=True)
    # async def clear(self, ctx, amount: int, *, reason=None):


    # @commands.command()
    # @commands.has_permissions(kick_members=True)
    # async def kick(self, ctx, member: discord.Member, *, reason=None):


    # @commands.command()
    # @commands.has_permissions(ban_members=True)
    # async def ban(self, ctx, member: discord.Member, *, reason=None):


    # @commands.command()
    # @commands.has_permissions(ban_members=True)
    # async def unban(self, ctx, member: discord.User, *, reason=None):


    # @commands.command()
    # @commands.has_permissions(ban_members=True)
    # async def softban(self, ctx, member: discord.Member, *, reason=None):

def setup(bot):
    bot.add_cog(Moderation(bot))
