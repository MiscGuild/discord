# The following file contains: giveawayend, giveawayreroll, dailylb, purge

from func.utils.discord_utils import name_grabber, log_event, get_giveaway_status, roll_giveaway

class Integer:
    def __init__(self, integer: int):
        self.integer = integer

    async def giveawayend(self):
        # Get giveaway status
        status = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if status == None:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"

        # Giveaway exists
        if status == "active":
            await roll_giveaway(self.integer)
        else:
            return "This giveaway has already ended!\n`To re-roll it use ,giveawayreroll`"

    
    async def giveawayreroll(self, reroll_number: int=None):
        # Get giveaway status
        status = await get_giveaway_status(self.integer)

        # Giveaway does not exist
        if status == None:
            return "This giveaway doesn't seem to exist!\n`Either it never existed, or its data was deleted after 10 days of disuse.`"
        
        # Giveaway exists
        if status == "inactive":
            await roll_giveaway(self.integer, reroll_number)
        else:
            return "This giveaway hasn't ended yet!\n`To end it, use ,giveawayend`"

    # async def dailylb(msg):

    async def purge(self, ctx, reason):
        await ctx.message.delete()
        await ctx.channel.purge(limit=self.integer)
        await log_event(f"{await name_grabber(ctx.author)} purged {self.integer} messages in {ctx.channel.name}", f"**Reason:** {reason}")
