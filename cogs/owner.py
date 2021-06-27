import discord
from discord.ext import commands

class owner(commands.Cog):
    def __init__(self, client):
        self.client=client

    #load extension
    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension):
        try:
            self.client.load_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} has been loaded')
        except Exception as e:
            await ctx.send(e)

    #unload extension
    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        try:
            self.client.unload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} has been unloaded')
        except Exception as e:
            await ctx.send(e)

    #reload extensions command
    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            self.client.reload_extension(f'cogs.{extension}')
            await ctx.send(f'{extension} has been reloaded')
        except Exception as e:
            await ctx.send(e)

    #super secret owner-only shutdown:
    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        embed=discord.Embed(description="Yes, master Rowdies, I'll shut down now.", color=0xFFFAFA)
        await ctx.send(embed=embed)
        await self.client.close()

#Add cog to main client
def setup(client):
    client.add_cog(owner(client))