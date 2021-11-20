from __main__ import bot

async def get_status(id: int):
    cursor = await bot.db.execute("SELECT status FROM giveaways WHERE message_id = (?)", (id,))
    row = await cursor.fetchone()
    await cursor.close()
    return row

async def roll_giveaway(reroll_target: int=None):
    return True