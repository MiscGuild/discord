import random

import aiohttp
import discord
import asyncio
import secrets
from discord.ext import commands

from cogs.utils import utilities as utils
from typing import Union


class Fun(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot = bot


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


    @commands.command(name='8ball', aliases=['eightball'])
    async def _8ball(self, ctx, *, question):
        """Play with the magic 8ball
        """
        user_name = await utils.name_grabber(ctx.author)

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

    @commands.command(aliases=["urbandict", "urbandictionary"])
    async def urban(self, ctx, *, word):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://api.urbandictionary.com/v0/define?term={word}") as resp:
                        req = await resp.json()
            except Exception:
                return await ctx.send("Urban API returned invalid data... might be down atm.")

            if not req:
                return await ctx.send("I think the API broke...")

            if not len(req["list"]):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(req["list"], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result["definition"]
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            await ctx.send(f"📚 Definition for **{result['word']}**```fix\n{definition}```")

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """ !ffuts sesreveR
        Everything you type after reverse will be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command()
    async def password(self, ctx, nbytes: int = 18):
        """ Generates a random password string for you
        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if nbytes not in range(3, 1401):
            return await ctx.send("I only accept any numbers between 3-1400")
        if hasattr(ctx, "guild") and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with your random generated password **{ctx.author.name}**")
        await ctx.author.send(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}")

    @commands.command()
    async def beer(self, ctx, user: Union[discord.Member, discord.User] = None, *, reason: commands.clean_content = ""):
        """ Give someone a beer! 🍻 """
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.name}**: paaaarty!🎉🍺")
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you* 🍻")
        if user.bot:
            return await ctx.send(
                f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
        beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for("raw_reaction_add", timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command(aliases=["howhot", "hot", "hotness"])
    async def hotcalc(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        """ Returns a random percent for how hot is a discord user """
        user = user or ctx.author

        random.seed(user.id)            
        r = random.randint(1, 100)
        hot = r / 1.17

        
        if user.id == 484411714637529088:
            hot = 420

        if hot > 75:
            emoji = "💞"
        elif hot > 50:
            emoji = "💖"
        elif hot > 25:
            emoji = "❤"
        else:
            emoji = "💔"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")


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
    async def pat(self, ctx, user: Union[discord.Member, discord.User] = None):
        """Pat the specified user!
        """
        author = await utils.name_grabber(ctx.author)
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animu/pat') as resp:
                req = await resp.json()
                await session.close()
        if user is None or ctx.author == user:
            embed = discord.Embed(title=f"{author} pats themselves.", color=0x8368ff)
        else:
            user = await utils.name_grabber(user)
            embed = discord.Embed(title=f"{author} pats {user}.", color=0x8368ff)
        embed.set_image(url=req['link'])
        await ctx.send(embed=embed)

    @commands.command()
    async def hug(self, ctx, user: Union[discord.Member, discord.User] = None):
        """hug the specified user!
        """
        author = await utils.name_grabber(ctx.author)
        async with aiohttp.ClientSession() as session:
            async with session.get('https://some-random-api.ml/animu/hug') as resp:
                req = await resp.json()
                await session.close()
        if user is None or ctx.author == user:
            embed = discord.Embed(title=f"{author} hugs themself.", color=0x8368ff)
        else:
            user = await utils.name_grabber(user)
            embed = discord.Embed(title=f"{author} hugs {user}.", color=0x8368ff)
        embed.set_image(url=req['link'])
        await ctx.send(embed=embed)

    @commands.command()
    async def horny(self, ctx, member: Union[discord.Member, discord.User] = None):
        """Gives the mentioned member a horny card"""
        member = member or ctx.author
        await ctx.send(f"https://some-random-api.ml/canvas/horny?avatar={member.avatar_url_as(format="png")}")

    @commands.command(aliases=['simp'])
    async def simpcard(self, ctx, member: Union[discord.Member, discord.User] = None):
        """Gives the mentioned member a simpcard"""
        member = member or ctx.author
        await ctx.send(f"https://some-random-api.ml/canvas/simpcard?avatar={member.avatar_url_as(format="png")}")


    @commands.command()
    async def userinfo(self, ctx, member: Union[discord.Member, discord.User]):
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
