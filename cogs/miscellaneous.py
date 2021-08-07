import discord
from discord import role
from discord.ext import commands, tasks
from cogs.utils import hypixel
from datetime import datetime, timedelta
import json
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import asyncio
import requests
import re

class miscellaneous(commands.Cog, name="Miscellaneous"):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()


    @commands.command()
    @commands.has_role("Giveaway Creator")
    async def giveaway(self, ctx, action, message_ID=None):
        # TODO: make a task that runs on startup to check all current giveaways. (end giveaway if past time). 
        # Make a `,giveaway (create/end/reroll/list - start for quick setup) (messageID)` command

        # TODO: Add datetime addition for giveaway duration. Keep the var seperate from the user's entry for later use in the announcement embed.

        # ,giveaway create <channel> <prize> <no.winners> <duration> <role requirements> <gexp requirements> <sponsors>
        
        if action.lower() in ["create", "make", "start", "add"]: # Create new giveaway
            while True:
                await ctx.send("What is the channel you would want the giveaway to be held in?\n\n`Please enter the name of a channel in this server.` \n`Alternatively, you can enter the channel ID.` \n\n**At any time, you can cancel the giveaway by replying with `cancel` to one of the upcoming prompts.**")
                destination = await self.bot.wait_for('message',
                                                    check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                destination = destination.content.lower()

                if destination == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif destination[0] == "<": # Channel shortcut was passed
                    destination = int(re.sub(r'[\W_]+', '', destination))
                    destination_channel = self.bot.get_channel(destination)
                elif destination.isnumeric() == True: # Channel ID was passed
                    destination_channel = self.bot.get_channel(int(destination))
                else: # Channel name was passed
                    destination = re.sub(r"\s+", "-", destination)
                    destination_channel = discord.utils.get(ctx.guild.channels, name=destination)
                
                if destination_channel != None: # Channel exists
                    break
                else: # Channel is non-existent - Redo step.
                    await ctx.send(f"The channel {destination} is invalid!")
                    

            # Channel entered correctly
            await ctx.send(f"Sweet! The giveaway is going to be held in <#{destination_channel.id}>. Next, what is the prize going to be?\n\n`Please enter a small description of the prize.`")
            prize = await self.bot.wait_for('message',
                                                check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            prize = prize.content

            if prize.lower() == "cancel":
                await ctx.send("Giveaway cancelled!")
                return
                

            # Prize entered correctly    
            while True:
                await ctx.send(f"Ok great! The prize of the giveaway will be '{prize}'. How many winners should the giveaway have?\n\n`Please enter a number from 1-20.`")
                number_winners = await self.bot.wait_for('message',
                                                    check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                number_winners = number_winners.content.lower()

                if number_winners == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif number_winners.isnumeric() == False: # Did not enter an integer
                    await ctx.send(f"The input {number_winners} is not valid! Please enter a number.")
                    
                else: # Entered an number
                    number_winners = round(int(number_winners)) 
                    if number_winners > 20 or number_winners < 1: # Too many/too few winners
                        await ctx.send(f"The input {number_winners} is not valid! It must be greater than 1 and less than 20.")
                    else:
                        break
                        
            
            # No. winners entered correctly
            while True:
                await ctx.send(f"Neat! There will be {number_winners} winner(s). Also, how long should the giveaway last for?\n\n`Please enter a duration. Use an 's' at the end for seconds, 'M' for minutes, 'D' for days, etc.`")
                duration = await self.bot.wait_for('message',
                                                    check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                duration = duration.content.lower()

                if duration == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return

                seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
                try:
                    if int(duration[:-1]) <= 0:
                        await ctx.send(f"The duration {duration} is not valid!")
                    else:
                        seconds_end = timedelta(seconds=int(duration[:-1]) * seconds_per_unit[duration[-1]])
                        # Force giveaway time (s) to formatted datetime
                        datetime_end = datetime.now() + seconds_end
                        break   
                except Exception:
                    await ctx.send(f"The duration {duration} is not valid!")
                    

            # Duration entered correctly
            while True:
                for_broken = False
                await ctx.send(f"Alright. The giveaway will last for {duration}. Should there be any role requirements for the giveaway?\n\n`Please enter role names or role IDs.`\n`If you don't want any role requirements, reply with 'None'`. \n`If entrants only need ONE of the required roles, use ',' between role names/IDs.` \n`If entrants must have ALL required roles, use '&' between role names/IDs`")
                required_roles = await self.bot.wait_for('message',
                                                    check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                required_roles = required_roles.content.lower()
                required_roles = re.sub(r"\s+", "", required_roles)
                
                if required_roles == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif required_roles == "none":
                    required_roles = []
                    role_requirement_type = "none"
                    break
                else:
                    # Convert string to list of all required roles
                    if "," in required_roles:
                        role_requirement_type = "optional"
                        required_roles = required_roles.split(",")
                    elif "&" in required_roles:
                        role_requirement_type = "required"
                        required_roles = required_roles.split("&")
                    else: # Still turn string into list
                        role_requirement_type = "optional"
                        required_roles = required_roles = [required_roles]

                    r_requirements = []
                    for required_role in required_roles:
                        required_role = required_role.title()
                        if re.search("[a-zA-Z]", required_role) != None: # Role name was passed
                            req_role = discord.utils.get(ctx.guild.roles, name=required_role)
                            if req_role != None:
                                r_requirements.append(req_role.id)
                            else: 
                                await ctx.send(f"The role {required_role} does not exist!")
                                for_broken = True
                                break

                        else: # Role ID was passed
                            # Force to integer
                            required_role = int(required_role)
                            req_role = ctx.guild.get_role(required_role)
                            if req_role != None:
                                r_requirements.append(req_role.id)
                            
                            else: 
                                await ctx.send(f"The role {required_role} does not exist!")
                                for_broken = True
                                break
                            
                    if for_broken: 
                        continue
                    else:
                        required_roles = r_requirements
                        break 
                
                

            # Role requirements entered correctly
            while True: 
                await ctx.send(f"Ok then, there will be {len(required_roles)} required role(s). Should there be a weekly gexp requirement for the giveaway?\n\n`If you don't want any gexp requirements, reply with 'None'.`\n`Otherwise, enter a required amount of weekly gexp. Add 'k' at the end to multiply it by one thousand, or 'm' for a million.`")

                required_gexp = await self.bot.wait_for('message',
                                                    check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                required_gexp = required_gexp.content.lower()
                
                if required_gexp == "cancel":
                    await ctx.send("Giveaway cancelled!")
                    return
                elif required_gexp != "none":
                    multiplier_per_unit = {"k": 1000, "m": 1000000}
                    if required_gexp.isnumeric(): # No multiplier attached
                        raw_required_gexp = int(required_gexp)
                        break
                    else:
                        try:
                            raw_required_gexp = int(required_gexp[:-1]) * multiplier_per_unit[required_gexp[-1]]
                            break
                        except Exception:
                            await ctx.send(f"The duration {duration} is not valid!")
                else:
                    required_gexp = 0
                    break


            # Gexp requirements entered correctly
            await ctx.send(f"Excellent! There will be a weekly gexp requirement of {required_gexp}. Finally, who has sponsored this giveaway?\n\n`Please reply with the tag(s) of the sponsors of this giveaway.` \n`Alternatively, if you sponsored this giveaway, you can reply with 'None'.`")
            sponsors = await self.bot.wait_for('message',
                                                    check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
            sponsors = sponsors.content

            if sponsors.lower() == "cancel":
                await ctx.send("Giveaway Cancelled!")
                return
            elif sponsors.lower() == "none":
                sponsors = ctx.author

            # Sponsors entered correctly
            while True:
                # Check if user needs one, all, or none of the required roles. Formulate message accordingly
                if role_requirement_type == "optional":
                    role_requirement_type_message = "You must have at least ONE of the following roles:"
                    for required_role in required_roles:
                        role_requirement_type_message = role_requirement_type_message + f"\n- <@&{required_role}>"
                elif role_requirement_type == "none":
                    role_requirement_type_message = "There are no required roles."
                else:
                    role_requirement_type_message = "You must have ALL of the following roles:"
                    for required_role in required_roles:
                        role_requirement_type_message = role_requirement_type_message + f"\n- <@&{required_role}>"

                # Confirmation message
                embed = discord.Embed(title="Giveaway Confirmation!", description="Please reply with `confirm` to start the giveaway.\nOtherwise, please reply with `cancel` to cancel the giveaway.", color=0x8368ff).set_footer(text="This is your last opportunity to cancel this giveaway, to cancel it, say `cancel`.")
                embed.add_field(name="[-] Giveaway information", value=f"**Prize:** {prize}\n**No. Winners:** {number_winners}\n**Duration:** {duration}", inline=False)
                embed.add_field(name="[-] Requirements", value=f"**Role Requirements** - {role_requirement_type_message}\n**Weekly Gexp Requirement** - {required_gexp}", inline=False)
                await ctx.send(embed=embed)
                confirmation = await self.bot.wait_for('message',
                                                        check=lambda x: x.channel == ctx.channel and x.author == ctx.author)
                confirmation = confirmation.content.lower()

                if confirmation in ["no", "cancel", "stop", "exit"]:
                    await ctx.send("Giveaway Cancelled!")
                    return
                elif confirmation not in ["yes", "confirm", "go", "create"]:
                    await ctx.send(f"The input {confirmation} is not valid!")
                else:
                    # Send giveaway message
                    embed=discord.Embed(title=f"{prize}", color=0x8368ff).set_footer(text=f"{number_winners} Winner(s), Ends at INSERTTIEMHEREJEJEDONTBEDUMB")
                    embed.add_field(name="[-] Information:" ,value=f"Sponsored by: {sponsors}", inline=False)
                    embed.add_field(name="[-] Requirements:", value=f"{role_requirement_type_message} \n\nYou must have at least {required_gexp} weekly gexp.", inline=False)
                    giveaway_msg = await destination_channel.send(f"{self.bot.giveaways_events.mention} React with :tada: to enter!\n", embed=embed)
                    await giveaway_msg.add_reaction("\U0001F389")
                    await destination_channel.send(f"This giveaway was generously sponsored by **{sponsors}**.\nIf you win this giveaway, make a ticket to claim it!", color=0x8368ff)
                    

                    giveaway_data = {
                        "channelID" : f"{destination_channel.id}",
                        "messageID" : f"{giveaway_msg.id}",
                        "prize" : f"{prize}", 
                        "number_winners" : f"{number_winners}",
                        "time_of_finish" : f"{datetime_end}",
                        "role_requirement_type" : f"{role_requirement_type}", 
                        "required_roles" : f"{required_roles}", 
                        "required_gexp" : f"{required_gexp}",
                        "sponsors" : f"{sponsors}", 
                        "giveaway_author" : f"{ctx.message.author}",
                        "status" : "active"
                    }
                
                    with open("giveaways.json", "r+") as f:
                        json_data = json.load(f)
                        json_data[giveaway_msg.id] = giveaway_data
                        f.seek(0)
                        json.dump(json_data, f)  

                    await ctx.send(f"Ok! The giveaway has been set up in <#{destination_channel.id}>.")
                    break

        elif action.lower() in ["end", "finish"]: # End existing giveaway
            if message_ID == None:
                await ctx.send("You must provide the message ID of a giveaway to end!")


        elif action.lower() == "reroll": # Reroll existent giveaway
            await ctx.send("NOT CODED YET")


        elif action.lower() == "list": # List all current giveaways
            await ctx.send("NOT CODED YET")
    


    async def roll_giveaway(self, giveaway_info):
        print("THIS IS THE ROLL GIVEAWAY FUNCTION")

    
    @tasks.loop(minutes=2)
    async def check_giveaways(self):
        with open("giveaways.json", "r+") as f:
            json_data = json.load(f)

        for entry in json_data:
            entry = json_data[entry]
            datetime_end = datetime.strptime(entry['time_of_finish'], "%Y-%m-%d %H:%M:%S.%f") 
            
            if entry['status'] == "active" and datetime_end < datetime.now(): # Giveaway needs to be ended
                await self.roll_giveaway(self, entry)
                continue

            elif entry['status'] == "inactive": # If giveaway ended more than 10 days ago, delete it
                if datetime.timedelta(days=10) < datetime_end:
                    del json_data[entry]['messageID']
                    json.dump(json_data, f)

    @check_giveaways.before_loop
    async def before_giveaway_check(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(miscellaneous(bot))