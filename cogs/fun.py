import aiohttp
import random

import discord
import datetime
from discord.ext import commands
from io import BytesIO

from cogs.utils import hypixel


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
                await session.close()
        embed = discord.Embed(title="Here's the pizza you requested:", color=0x8368ff)
        embed.set_image(url=req['image'])
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
        user_name = await hypixel.name_grabber(ctx.author)

        responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.",
                     "Concentrate and ask again.", "Don’t count on it.", "It is certain.", "It is decidedly so.",
                     "Most likely", "My reply is no.", "My sources say no.", "Outlook not so good.", "Outlook good.",
                     "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Yes.",
                     "Yes – definitely.", "You may rely on it."]
        embed = discord.Embed(title=f'{random.choice(responses)}', color=0x8368ff)
        embed.set_author(name=f"{question}")
        embed.set_footer(text=f'{user_name}')
        await ctx.send(embed=embed)

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="You're supposed to ask me a question ._.", description="8ball `question`",
                                  color=0xff0000)
            await ctx.send(embed=embed)

    @commands.command()
    async def dog(self, ctx):
        """Sends an image of a dog
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animal/dog') as resp:
                req = await resp.json()
                await session.close()
        embed = discord.Embed(title="Here's the dog you requested:", color=0x8368ff)
        embed.set_footer(text=f"Fun Fact:\n{req['fact']}")
        embed.set_image(url=req['image'])
        await ctx.send(embed=embed)

    @commands.command()
    async def cat(self, ctx):
        """Sends an image of a cat
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animal/cat') as resp:
                req = await resp.json()
                await session.close()
        embed = discord.Embed(title="Here's the cat you requested:", color=0x8368ff)
        embed.set_footer(text=f"Fun Fact:\n{req['fact']}")
        embed.set_image(url=req['image'])
        await ctx.send(embed=embed)

    @commands.command(aliases=['bird'])
    async def birb(self, ctx):
        """Sends an image of a birb
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animal/birb') as resp:
                req = await resp.json()
                await session.close()
        embed = discord.Embed(title="Here's the bird you requested:", color=0x8368ff)
        embed.set_footer(text=f"Fun Fact:\n{req['fact']}")
        embed.set_image(url=req['image'])
        await ctx.send(embed=embed)

    @commands.command()
    async def panda(self, ctx):
        """Sends an image of a panda
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animal/panda') as resp:
                req = await resp.json()
                await session.close()
        embed = discord.Embed(title="Here's the panda you requested:", color=0x8368ff)
        embed.set_footer(text=f"Fun Fact:\n{req['fact']}")
        embed.set_image(url=req['image'])
        await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx):
        """Sends a joke
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/joke') as resp:
                req = await resp.json()
                await session.close()
        embed = discord.Embed(title=req['joke'], color=0x8368ff)
        await ctx.send(embed=embed)

    @commands.command()
    async def pat(self, ctx, user: discord.User = None):
        """Pat the specified user!
        """
        author = await hypixel.name_grabber(ctx.author)
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animu/pat') as resp:
                req = await resp.json()
                await session.close()
        if user is None or ctx.author == user:
            embed = discord.Embed(title=f"{author} pats themselves.", color=0x8368ff)
        else:
            user = await hypixel.name_grabber(user)
            embed = discord.Embed(title=f"{author} pats {user}.", color=0x8368ff)
        embed.set_image(url=req['link'])
        await ctx.send(embed=embed)

    @commands.command()
    async def hug(self, ctx, user: discord.User = None):
        """hug the specified user!
        """
        author = await hypixel.name_grabber(ctx.author)
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animu/hug') as resp:
                req = await resp.json()
                await session.close()
        if user is None or ctx.author == user:
            embed = discord.Embed(title=f"{author} hugs themselves.", color=0x8368ff)
        else:
            user = await hypixel.name_grabber(user)
            embed = discord.Embed(title=f"{author} hugs {user}.", color=0x8368ff)
        embed.set_image(url=req['link'])
        await ctx.send(embed=embed)

    @commands.command()
    async def horny(self, ctx, member: discord.User = None):
        """Gives the mentioned member a horny card"""
        member = member or ctx.author
        await ctx.send(f"https://some-random-api.ml/canvas/horny?avatar={member.avatar_url}")

    @commands.command(aliases=['simp'])
    async def simpcard(self, ctx, member: discord.User = None):
        """Gives the mentioned member a simpcard"""
        member = member or ctx.author
        await ctx.send(f"https://some-random-api.ml/canvas/simpcard?avatar={member.avatar_url}")

    @commands.command()
    async def avatar(self, ctx, member: discord.User):
        """Sends the member's discord avatar
        """
        embed = discord.Embed(title=f"{member.name}'s avatar:", color=0x8368ff)
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member):
        """Sends an embed with the discord member's info
        """
        embed = discord.Embed(title=f"{member.name}", description=member.nick, color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Account created:", value=str(member.created_at)[:-7], inline=False)
        embed.add_field(name="Joined this discord on:", value=str(member.joined_at)[:-7], inline=False)
        if member.premium_since is not None:
            embed.add_field(name="Server booster since:", value=str(member.premium_since)[:-7], inline=False)
        else:
            embed.add_field(name="Server booster:", value="False", inline=False)
        total_roles = ""
        for role in member.roles:
            total_roles = total_roles + f"{role}\n"
        embed.add_field(name="Roles:", value=total_roles, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['lyrc', 'lrc', 'lyr'])
    async def lyrics(self, ctx, *, search=None):
        """A command to find lyrics easily!"""

        if search is None:
            embed = discord.Embed(title="No search argument!",
                                  description="You have not entered a song name!", color=0xDE3163)
            await ctx.reply(embed=embed)

        song = search.replace(' ', '%20')

        async with aiohttp.ClientSession() as lyricsSession:
            async with lyricsSession.get(
                    f'https://some-random-api.ml/lyrics?title={song}') as jsondata:
                if not (300 > jsondata.status >= 200):
                    await ctx.send(f'Recieved Poor Status code of {jsondata.status}.')
                else:
                    lyricsData = await jsondata.json()  # load json data
                    songLyrics = lyricsData['lyrics']  # the lyrics
                    songArtist = lyricsData['author']  # the authors name
                    songTitle = lyricsData['title']  # the songs title

            try:
                for chunk in [songLyrics[i:i + 2000] for i in range(0, len(songLyrics),
                                                                    2000)]:  # if the lyrics extend the discord character limit (2000): split the embed
                    embed = discord.Embed(title=f'{songTitle} by {songArtist}', description=chunk,
                                          color=0x8368ff)
                    await lyricsSession.close()
                    await ctx.reply(embed=embed, mention_author=False)

            except discord.HTTPException:
                embed = discord.Embed(title=f'{songTitle} by {songArtist}', description=chunk,
                                      color=0x8368ff)
                await lyricsSession.close()  # closing the session

                await ctx.reply(embed=embed, mention_author=False)


def setup(bot):
    bot.add_cog(Fun(bot))
