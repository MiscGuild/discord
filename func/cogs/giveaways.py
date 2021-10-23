from discord.ext import commands, tasks
from datetime import datetime, timedelta

class Giveaways(commands.Cog, name="Giveaways"):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    # @commands.command(aliases=["gcreate"])
    # @commands.has_role("Giveaway Creator")
    # async def giveawaycreate(self, ctx):


    # @commands.command(aliases=["giveawayfinish", "gend", "gfinish"])
    # @commands.has_role("Giveaway Creator")
    # async def giveawayend(self, ctx, message_ID):


    # @commands.command(aliases=["greroll", "reroll"])
    # @commands.has_role("Giveaway Creator")
    # async def giveawayreroll(self, ctx, message_ID, reroll_number=None):


    # @commands.command(aliases=["glist"])
    # async def giveawaylist(self, ctx):

    @tasks.loop(minutes=1)
    async def check_giveaways(self):
        cursor = await self.bot.db.execute("SELECT message_id, status, time_of_finish FROM Giveaways")
        rows = await cursor.fetchall()
        await cursor.close()

        for row in rows:
            message_id, status, datetime_end_str = row
            datetime_end = datetime.strptime(datetime_end_str, "%Y-%m-%d %H:%M:%S")

            if status == "active" and datetime_end < datetime.utcnow():  # Giveaway needs to be ended
                await self.roll_giveaway(message_id)
            elif status == "inactive" and datetime.utcnow() > datetime_end + timedelta(days=10):  # If giveaway ended more than 10 days ago, delete it
                await self.bot.db.execute("DELETE FROM Giveaways WHERE message_id = (?)", (message_id,))
                await self.bot.db.commit()

    @check_giveaways.before_loop
    async def before_giveaway_check(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Giveaways(bot))