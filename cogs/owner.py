import discord
from discord.ext import commands

class Owner(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client=client

    #load extension
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        try:
            self.client.load_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} has been loaded')
        except Exception as e:
            await ctx.send(e)

    #unload extension
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        try:
            self.client.unload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} has been unloaded')
        except Exception as e:
            await ctx.send(e)

    #reload extensions command
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            self.client.reload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} has been reloaded')
        except Exception as e:
            await ctx.send(e)

#Add cog to main client
def setup(client):
    client.add_cog(Owner(client))
