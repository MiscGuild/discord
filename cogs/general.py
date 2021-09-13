import chat_exporter
import discord
import aiohttp
from discord.ext import commands


class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def source(self, ctx):
        """ Check the source code!"""
        await ctx.send(
            f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/MiscGuild/MiscBot")

    @commands.command()
    async def ping(self, ctx):
        """Gives the ping of the bot
        """
        embed = discord.Embed(title='Pong',
                              description=f"{round(self.bot.latency * 1000)}ms",
                              color=0x8368ff)
        await ctx.send(embed=embed)

    @commands.command()
    async def covid(self, ctx, *, country: str):
        """Covid-19 Statistics for any countries"""
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://disease.sh/v3/covid-19/countries/{country.lower()}') as resp:
                    r = await resp.json()
                    await session.close()

            if "message" in r:
                return await ctx.send(f"The API returned an error:\n{r['message']}")

            json_data = [
                ("Total Cases", r["cases"]), ("Total Deaths", r["deaths"]),
                ("Total Recover", r["recovered"]), ("Total Active Cases", r["active"]),
                ("Total Critical Condition", r["critical"]), ("New Cases Today", r["todayCases"]),
                ("New Deaths Today", r["todayDeaths"]), ("New Recovery Today", r["todayRecovered"])
            ]

            embed = discord.Embed(
                description=f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R>",
                color=0x8368ff
            )

            for name, value in json_data:
                embed.add_field(
                    name=name, value=f"{value:,}" if isinstance(value, int) else value
                )

            await ctx.send(
                f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
                f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*",
                embed=embed
            )
def setup(bot):
    bot.add_cog(General(bot))
