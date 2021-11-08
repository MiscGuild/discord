import discord
from discord.ext import commands
from discord.ext.commands.core import command
from cogs.utils import utilities as utils

class Events(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Staff")
    async def completechallenge(self, ctx, member: discord.Member, challenge_type: str, scaled_challenge_score: float=None):
        name, uuid = await utils.get_dispnameID(await utils.name_grabber(member))
        challenge_type = challenge_type.lower()

        # Calculate points based on challenge
        if challenge_type in ["scaled", "s"]:
            if scaled_challenge_score == None:
                await ctx.send("You must enter the player's score for this challenge!")
                return
            
            # Get player data
            row = await self.get_player(uuid)
            if row != None:
                uuid, total_points, completed_challenges, scaled_challenge = row
                await self.update_value(uuid, total_points, completed_challenges, scaled_challenge_score)
            else:
                await self.insert_new(uuid, 0, 1, scaled_challenge_score)

            await ctx.send(f"{name}'s highest scaled challenge score today is {scaled_challenge_score}")
            return

        elif challenge_type in ["hard", "h"]:
            points_earned = 2
        elif challenge_type in ["easy", "e"]:
            points_earned = 1
        elif challenge_type in ["member", "m"]:
            if await utils.get_guild(name) != "Miscellaneous" and await utils.get_guild(name) not in self.bot.misc_allies:
                await ctx.send("This player is not eligible for this challenge! Only members of miscellaneous and allied guilds can participate!")
                return
            else:
                points_earned = 1
        else:
            await ctx.send("Invalid challenge! Available challenges are: **S**caled, **H**ard, **E**asy, **M**ember.")
            return

        # Update player's statistics for general challenge
        # Get data from db
        row = await self.get_player(uuid)
        if row != None:
            uuid, total_points, completed_challenges, scaled_challenge_score = row
            total_points += points_earned
            completed_challenges += 1
            await self.update_value(uuid, total_points, completed_challenges, scaled_challenge_score)
        else:
            total_points = points_earned
            completed_challenges = 1
            await self.insert_new(uuid, total_points, completed_challenges, 0)
        
        # Send player's overall stats
        embed = discord.Embed(title=f"Event statistics - {name}", description=f"**Scaled points earned:** {points_earned}\n**Total points:** {total_points}\n**Challenges completed:** {completed_challenges}", color=0x8368ff)
        await ctx.send(embed=embed)


    
    @commands.command()
    @commands.has_role("Staff")
    async def addpoints(self, ctx, member: discord.Member, points: int):
        name, uuid = await utils.get_dispnameID(await utils.name_grabber(member))
        row = await self.get_player(uuid)

        if row == None:
            await self.insert_new(uuid, points, 0, 0)
            completed_challenges = 0
        else:
            uuid, total_points, completed_challenges, scaled_challenge_score = row
            await self.update_value(uuid, total_points + points, completed_challenges)
            points = total_points

        # Send player's overall stats
        embed = discord.Embed(title=f"Event statistics - {name}", description=f"**Total points:** {points}\n**Challenges completed:** {completed_challenges}", color=0x8368ff)
        await ctx.send(embed=embed)


        
    @commands.command()
    @commands.has_role("Staff")
    async def removepoints(self, ctx, member: discord.Member, points: int):
        name, uuid = await utils.get_dispnameID(await utils.name_grabber(member))
        row = await self.get_player(uuid)

        if row != None:
            uuid, total_points, completed_challenges, scaled_challenge_score = row
            points = total_points - points
            await self.update_value(uuid, points)
        else:
            await self.insert_new(uuid, points, 0, 0)
            completed_challenges = 0

        # Send player's overall stats
        embed = discord.Embed(title=f"Event statistics - {name}", description=f"**Total points:** {points}\n**Challenges completed:** {completed_challenges}", color=0x8368ff)
        await ctx.send(embed=embed)




    async def insert_new(self, uuid, points, challenges, scaled_challenge_score):
        await self.bot.db.execute("INSERT INTO event VALUES (?, ?, ?, ?)", (uuid, points, challenges, scaled_challenge_score,))
        await self.bot.db.commit()

    async def update_value(self, uuid, points, completed=None, scaled_challenge_score=None):
        if completed == None:
            await self.bot.db.execute("UPDATE event SET points = (?) WHERE uuid = (?)", (points, uuid,))
        elif scaled_challenge_score != None:
            await self.bot.db.execute("UPDATE event SET points = (?), scaled_challenge_score = (?) WHERE uuid = (?)", (points, scaled_challenge_score, uuid,))
        else:
            await self.bot.db.execute("UPDATE event SET points = (?), completed = (?) WHERE uuid = (?)", (points, completed, uuid,))
        await self.bot.db.commit()

    async def get_player(self, uuid):
        cursor = await self.bot.db.execute("SELECT * FROM event WHERE uuid = (?)", (uuid,))
        row = await cursor.fetchone()
        await cursor.close()
        return row


def setup(bot):
    bot.add_cog(Events(bot))