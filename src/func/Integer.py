# The following file contains: giveawayend, giveawayreroll, gtop, purge

import discord

from src.utils.consts import error_color, invalid_guild_embed, guild_handle
from src.utils.db_utils import get_giveaway_status
from src.utils.discord_utils import log_event, name_grabber
from src.utils.giveaway_utils import roll_giveaway
from src.utils.minecraft_utils import get_hypixel_player_rank
from src.utils.request_utils import (get_guild_by_name, get_hypixel_player,
                                     get_jpg_file, get_name_by_uuid)


class Integer:
    def __init__(self, integer: int):
        self.integer = integer

    async def giveawayend(self):
        # Get giveaway status
        status, = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if not status:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        if not status:
            return "This giveaway has already ended!\n`To re-roll it use ,giveawayreroll`"
        await roll_giveaway(self.integer)

    async def giveawayreroll(self, reroll_number: int = None):
        # Get giveaway status
        status, = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if not status:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        if status:
            return "This giveaway hasn't ended yet!\n`To end it, use ,giveawayend`"
        await roll_giveaway(self.integer, reroll_number)

    async def gtop(self, ctx):
        # Check no. days requested to prevent errors
        if self.integer > 6:
            return discord.Embed(title="Invalid timestamp!", description="You cannot request data this old!",
                                 color=error_color)

        await ctx.message.delete()
        async with ctx.channel.typing():
            guild_data = await get_guild_by_name(guild_handle)
            if not guild_data:
                return invalid_guild_embed

            member_gexp = {}
            date = None
            # Loop through all members to find top 10
            for member in guild_data["members"]:
                if not date:
                    date = list(member["expHistory"].keys())[self.integer]
                member_gexp[member["uuid"]] = list(
                    member["expHistory"].values())[self.integer]

            # Sort member gexp
            member_gexp = sorted(member_gexp.items(),
                                 key=lambda item: item[1], reverse=True)

            # Get image data
            image_content = f"&f&lDaily Top: {date}&r%5Cn"
            count = 0
            for i in member_gexp[:10]:
                count += 1
                user_data = i
                name = await get_name_by_uuid(user_data[0])
                rank, _ = await get_hypixel_player_rank(await get_hypixel_player(uuid=user_data[0]))

                # Add new entry to image content
                image_content += f"&6{count}. {rank} {name} &2{format(user_data[1], ',d')} Guild Experience"
                # Add new line
                if count < 10:
                    image_content += "%5Cn"

        # Replace characters for URL
        image_content = image_content.replace("+", "%2B")
        image_content = image_content.replace("&", "%26")
        image_content = image_content.replace(" ", "%20")
        image_content = image_content.replace(",", "%2C")

        # Return image
        return await get_jpg_file(f"https://fake-chat.matdoes.dev/render.png?m=custom&d={image_content}&t=1")

    async def purge(self, ctx, reason):
        await ctx.message.delete()
        await ctx.channel.purge(limit=self.integer)
        await log_event(f"{await name_grabber(ctx.author)} purged {self.integer} message(s) in {ctx.channel.name}",
                        f"**Reason:** {reason}")
