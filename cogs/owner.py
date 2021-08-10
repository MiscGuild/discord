from discord.ext import commands


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted = []

    # load extension
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        try:
            if extension not in self.blacklisted:
                self.bot.load_extension(f'cogs.{extension}')
                await ctx.send(f'{extension} has been loaded')
        except Exception as e:
            await ctx.send(e)

    # unload extension
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        try:
            if extension not in self.blacklisted:
                self.bot.unload_extension(f'cogs.{extension}')
                await ctx.send(f'{extension} has been unloaded')
        except Exception as e:
            await ctx.send(e)

    # reload extensions command
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            if extension not in self.blacklisted:
                self.bot.reload_extension(f'cogs.{extension}')
                await ctx.send(f'{extension} has been reloaded')
        except Exception as e:
            await ctx.send(e)


# Add cog to main bot
def setup(bot):
    bot.add_cog(Owner(bot))
