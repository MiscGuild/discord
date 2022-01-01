# The following file contains: giveawayend, giveawayreroll, gtop, purge
from __main__ import bot
import discord

from func.utils.discord_utils import name_grabber, log_event, get_giveaway_status, roll_giveaway
from func.utils.minecraft_utils import get_hypixel_player_rank
from func.utils.request_utils import get_guild_by_name, get_name_by_uuid, get_hypixel_player, get_gtop
from func.utils.consts import invalid_guild_embed, error_color

class Integer:
    def __init__(self, integer: int):
        self.integer = integer

    async def giveawayend(self):
        # Get giveaway status
        status = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if not status:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        if status == "active":
            await roll_giveaway(self.integer)
        else:
            return "This giveaway has already ended!\n`To re-roll it use ,giveawayreroll`"

    async def giveawayreroll(self, reroll_number: int = None):
        # Get giveaway status
        status = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if not status:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        if status == "inactive":
            await roll_giveaway(self.integer, reroll_number)
        else:
            return "This giveaway hasn't ended yet!\n`To end it, use ,giveawayend`"

    async def gtop(self, ctx):
        # Check no. days requested to prevent errors
        if self.integer > 6:
            return discord.Embed(title="Invalid timestamp!", description="You cannot request data this old!", color=error_color)

        await ctx.message.delete()
        async with ctx.channel.typing():
            guild_data = await get_guild_by_name(bot.guild_name)
            if guild_data == None:
                return invalid_guild_embed

            member_gexp = {}
            date = None
            # Loop through all members to find top 10
            for member in guild_data["guild"]["members"]:
                if date == None:
                    date = list(member["expHistory"].keys())[self.integer]
                member_gexp[member["uuid"]] = list(member["expHistory"].values())[self.integer]

            # Sort member gexp
            member_gexp = sorted(member_gexp.items(), key=lambda item: item[1], reverse=True)

            # Get image data
            image_content = f"&f&lDaily Top: {date}&r%5Cn"
            for i in range(10):
                user_data = member_gexp[i]
                name = await get_name_by_uuid(user_data[0])
                rank = await get_hypixel_player_rank(await get_hypixel_player(name))

                # Add new entry to image content
                image_content += f"&6{i + 1}. {rank} {name} &2{format(user_data[1], ',d')} Guild Experience"
                # Add new line
                if i < 9:
                    image_content +="%5Cn"
        
        # Replace characters for URL
        image_content = image_content.replace("+", "%2B")
        image_content = image_content.replace("&", "%26")
        image_content = image_content.replace(" ", "%20")
        image_content = image_content.replace(",", "%2C")

        # Return image
        return await get_gtop(f"https://chat.miscguild.xyz/render.png?m=custom&d={image_content}&t=1")


    async def purge(self, ctx, reason):
        await ctx.message.delete()
        await ctx.channel.purge(limit=self.integer)
        await log_event(f"{await name_grabber(ctx.author)} purged {self.integer} message(s) in {ctx.channel.name}",
                        f"**Reason:** {reason}")