import discord
from discord.ext import commands
import random

class Fun(commands.Cog, name="Fun"):
    def __init__(self, client):
        self.client = client

    # Pizza
    @commands.command()
    async def pizza(self, ctx):
        """Gives you a pizza
        """
        links = ['https://bit.ly/3ibK6PQ', 'https://bit.ly/2EZWZ1p', 'https://bit.ly/339ul5N', 'https://bit.ly/328OOIx',
                'https://bit.ly/3ibMqGy', 'https://bit.ly/2F8hd96', 'https://bit.ly/2R5XusZ', 'https://bit.ly/35fRqX7',
                'https://bit.ly/2F9Ec3B', 'https://bit.ly/3h9T8vI', 'https://bzfd.it/2GzzLzm', 'https://bit.ly/35fyKa7',
                'https://bit.ly/3lVF24F', 'https://bit.ly/2R2Ccg1', 'https://bit.ly/3haFhVZ', 'https://bit.ly/2DDaWkW',
                'https://bit.ly/2R893Qx']
        image = random.choice(links)
        embed = discord.Embed(title="Here's the pizza you requested:", color=0xD2691e)
        embed.set_image(url=image)
        await ctx.send(embed=embed)

    # Ping
    @commands.command()
    async def ping(self, ctx):
        """Gives the bot's ping
        """
        embed = discord.Embed(title='Pong',
                            description=f"{round(self.client.latency * 1000)}ms",
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