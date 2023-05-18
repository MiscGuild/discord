from __main__ import bot
from datetime import datetime, timedelta

from discord.ext import tasks

from src.func.General import General
from src.func.Integer import Integer
from src.utils.consts import weekly_lb_channel, daily_lb_channel
from src.utils.db_utils import (connect_db, select_all)
from src.utils.giveaway_utils import roll_giveaway


@tasks.loop(minutes=1)
async def check_giveaways():
    # Get all giveaway data
    all_giveaways = await select_all("SELECT message_id, time_of_finish, is_active FROM giveaways")

    for message_id, time_of_finish, is_active in all_giveaways:
        time_of_finish = datetime.strptime(time_of_finish, "%Y-%m-%d %H:%M:%S")

        # Giveaway needs to be ended
        if is_active and time_of_finish < datetime.utcnow():
            await roll_giveaway(message_id)

        # Giveaway ended more than 10 days ago, delete it
        elif not is_active and datetime.utcnow() > time_of_finish + timedelta(days=10):
            await bot.db.execute("DELETE FROM Giveaways WHERE message_id = (?)", (message_id,))
            await bot.db.commit()


@check_giveaways.before_loop
async def before_giveaway_check():
    await bot.wait_until_ready()
    await connect_db()


@tasks.loop(hours=24)
async def send_gexp_lb():
    import asyncio
    await asyncio.sleep(1)
    file = await Integer(integer=1).gtop(bot.get_channel(daily_lb_channel))
    await bot.get_channel(daily_lb_channel).send(file=file)
    if datetime.utcnow().weekday() == 0:
        await bot.get_channel(weekly_lb_channel).send(
            f"__Week {int(80 + round((datetime.utcnow() - datetime.strptime('14/08/2022', '%d/%m/%Y')).days / 7))}__\n"
            f"**{(datetime.utcnow() - timedelta(days=7)).strftime('%d %b %Y')} "
            f"-"
            f" {datetime.utcnow().strftime('%d %B %Y')}**")
        await bot.get_channel(weekly_lb_channel).send(file=await General.weeklylb(bot.get_channel(weekly_lb_channel)))


@send_gexp_lb.before_loop
async def before_gexp_lb():
    await bot.wait_until_ready()
