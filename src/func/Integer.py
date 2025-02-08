# The following file contains: giveawayend, giveawayreroll, gtop, purge

import discord
import discord.ext.commands.context as Context

from src.utils.calculation_utils import generate_lb_text
from src.utils.consts import error_color, invalid_guild_embed, guild_handle, log_channel_id, neutral_color
from src.utils.db_utils import get_giveaway_status
from src.utils.discord_utils import name_grabber
from src.utils.giveaway_utils import roll_giveaway
from src.utils.request_utils import (get_guild_by_name)
from src.utils.ticket_utils.tickets import create_transcript


class Integer:
    def __init__(self, integer: int):
        self.integer = integer

    async def giveawayend(self) -> str | None:
        # Get giveaway status
        status, = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if not status:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        if not status:
            return "This giveaway has already ended!\n`To re-roll it use ,giveawayreroll`"
        await roll_giveaway(self.integer)

    async def giveawayreroll(self, reroll_number: int = None) -> str | None:
        # Get giveaway status
        status = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if status is None:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        elif status[0]:
            return "This giveaway hasn't ended yet!\n`To end it, use ,giveawayend`"
        await roll_giveaway(self.integer, reroll_number)

    async def gtop(self, ctx, is_automatic=False) -> discord.Embed | str:
        # Check no. days requested to prevent errors
        if self.integer > 6:
            return discord.Embed(title="Invalid timestamp!", description="You cannot request data this old!",
                                 color=error_color)

        guild_data = await get_guild_by_name(guild_handle)
        member_gexp = {}
        date = None

        if not guild_data:
            return invalid_guild_embed

        # Loop through all members to find top 10
        for member in guild_data["members"]:
            date = list(member["expHistory"].keys())[self.integer]
            member_gexp[member["uuid"]] = list(member["expHistory"].values())[self.integer]

        # Sort member gexp
        member_gexp = sorted(member_gexp.items(),
                             key=lambda item: item[1],
                             reverse=True)

        # Get image data
        # text = f"&f&lDaily Top: {date}&r%5Cn"
        text = f"**Daily Top: {date}**\n"
        text = await generate_lb_text(member_gexp, text, is_automatic)

        return text

    async def purge(self, ctx: Context, reason: str = None) -> None:
        transcript = await create_transcript(ctx.channel, self.integer)
        await ctx.channel.purge(limit=self.integer)
        await ctx.guild.get_channel(log_channel_id).send(embed=discord.Embed(
            title=f"{await name_grabber(ctx.author)} purged {self.integer} message(s) in {ctx.channel.name}",
            description=f"**Reason:** {reason}",
            color=neutral_color).set_footer(text="Following is the transcript of the deleted messages"),
                                                         file=transcript)
