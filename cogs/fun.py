import discord
from discord.ext import commands
import random
import aiohttp

class Fun(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot = bot

    # Pizza
    @commands.command()
    async def pizza(self, ctx):
        """Gives you a pizza
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://foodish-api.herokuapp.com/api/images/pizza') as resp:
                req = await resp.json()
        embed = discord.Embed(title="Here's the pizza you requested:", color=0xD2691e)
        embed.set_image(url=req['image'])
        await ctx.send(embed=embed)

    @commands.command()
    async def chester(self, ctx):
        """Sends a random image of chester
        """
        links = ['https://bit.ly/3zVao27', 'https://bit.ly/3wTpNOK', 'https://bit.ly/3wTpNOK', 'https://bit.ly/2T2gXiX',
                'https://bit.ly/3qjLS6F', 'https://bit.ly/3h1zJyH', 'https://bit.ly/2SYlQcN', 'https://bit.ly/3xN3vy5',
                'https://bit.ly/3j3sZDj', 'https://bit.ly/35Lu9v8', 'https://bit.ly/35Lu9v8', 'https://bit.ly/2Usk2Jn',
                'https://bit.ly/3wSxTXS', 'https://bit.ly/3qnEYNO', 'https://bit.ly/3gOwJa3', 'https://bit.ly/3zVSVXE',
                'https://bit.ly/3zKYDv8', 'https://bit.ly/3xNHn6U', 'https://bit.ly/35MdUOz', 'https://bit.ly/35MHfIJ']
        image = links[random.randint(0, len(links) + 1)]
        embed = discord.Embed(title="Here's the furry you requested:", color=0xD2691e)
        embed.set_image(url=image)
        await ctx.send(embed=embed)

    # Ping
    @commands.command()
    async def ping(self, ctx):
        """Gives the bot's ping
        """
        embed = discord.Embed(title='Pong',
                            description=f"{round(self.bot.latency * 1000)}ms",
                            color=0x8368ff)
        await ctx.send(embed=embed)

    # 8ball
    @commands.command(name='8ball', aliases=['eightball'])
    async def _8ball(self, ctx, *, question):
        """Play with the magic 8ball
        """
        author = ctx.author
        user_name = author.nick
        if user_name is None:
            user_name = ctx.author.name
        responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.",
                    "Concentrate and ask again.", "Don’t count on it.", "It is certain.", "It is decidedly so.",
                    "Most likely", "My reply is no.", "My sources say no.", "Outlook not so good.", "Outlook good.",
                    "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Yes.",
                    "Yes – definitely.", "You may rely on it."]
        embed = discord.Embed(title=f'{random.choice(responses)}', color=0x0ffff)
        embed.set_author(name=f"{question}")
        embed.set_footer(text=f'{user_name}')
        await ctx.send(embed=embed)

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="You're supposed to ask me a question ._.", description="8ball `question`",
                                color=0xff0000)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))