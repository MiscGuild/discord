# The following file contains: giveawayend, giveawayreroll, dailylb

from func.utils.discord import giveaways as giveaway_utils
from func.utils.discord.log_event import log_event
from func.utils.discord.name_grabber import name_grabber

class Integer:
    def __init__(self, integer: int):
        self.integer = integer

    async def giveawayend(self):
        # Get giveaway status
        status = await giveaway_utils.get_status(self.integer)

        # Giveaway does not exist
        if status == None:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        if status == "active":
            await giveaway_utils.roll_giveaway(self.integer)
        else:
            return "This giveaway has already ended!\n`To re-roll it use ,giveawayreroll`"

    
    async def giveawayreroll(self, reroll_number: int=None):
        # Get giveaway status
        status = await giveaway_utils.get_status(self.integer)

        # Giveaway does not exist
        if status == None:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"
        
        # Giveaway exists
        if status == "inactive":
            await giveaway_utils.roll_giveaway(self.integer, reroll_number)
        else:
            return "This giveaway hasn't ended yet!\n`To end it, use ,giveawayend`"

    # async def dailylb(msg):

    async def clear(self, ctx, reason):
        await ctx.message.delete()
        await ctx.channel.purge(limit=self.integer)
        await log_event(f"{await name_grabber(ctx.author)} purged {self.integer} messages in {ctx.channel.name}", f"**Reason:** {reason}")
