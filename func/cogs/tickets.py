from discord.ext import commands


class Tickets(commands.Cog, name="Tickets"):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command(aliases=['reg', 'verify'])
    # async def register(self, ctx, name: str):

    # @commands.command(aliases=['del'])
    # async def delete(self, ctx):

    # @commands.command()
    # @commands.has_role("Staff")
    # async def add(self, ctx, member: discord.Member):

    # @commands.command()
    # @commands.has_role("Staff")
    # async def remove(self, ctx, member: discord.Member):

    # @commands.command()
    # @commands.has_role("Staff")
    # async def rename(self, ctx, *, channel_name: str):

    # @commands.command()
    # @commands.has_role("Staff")
    # async def transcript(self, ctx):

    # @commands.command()
    # @commands.has_role("Admin")
    # async def accept(self, ctx, member: discord.Member):

    # @commands.command()
    # @commands.has_any_role("Admin", "Moderator")
    # async def deny(self, ctx, channel: discord.TextChannel):

    # @commands.command()
    # async def new(self, ctx):


def setup(bot):
    bot.add_cog(Tickets(bot))
