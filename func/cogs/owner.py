from discord.ext import commands


class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.blacklisted = []


    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension: str):
        try:
            if extension not in self.blacklisted:
                self.bot.load_extension(f'cogs.{extension}')
                await ctx.send(f'{extension} has been loaded')
        except Exception as e:
            await ctx.send(e)


    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension: str):
        try:
            if extension not in self.blacklisted:
                self.bot.unload_extension(f'cogs.{extension}')
                await ctx.send(f'{extension} has been unloaded')
        except Exception as e:
            await ctx.send(e)


    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        try:
            if extension not in self.blacklisted:
                self.bot.reload_extension(f'cogs.{extension}')
                await ctx.send(f'{extension} has been reloaded')
        except Exception as e:
            await ctx.send(e)


def setup(bot):
    bot.add_cog(Owner(bot))