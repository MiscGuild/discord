from discord.ext import commands

class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension: str):
        try:
            self.bot.load_extension(f"func.cogs.{extension}")
            await ctx.send(f"{extension} has been loaded")
        except Exception as e:
            await ctx.send(e)


    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension: str):
        try:
            self.bot.unload_extension(f"func.cogs.{extension}")
            await ctx.send(f"{extension} has been unloaded")
        except Exception as e:
            await ctx.send(e)


    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        try:
            self.bot.reload_extension(f"func.cogs.{extension}")
            await ctx.send(f"{extension} has been reloaded")
        except Exception as e:
            await ctx.send(e)


def setup(bot):
    bot.add_cog(Owner(bot))
