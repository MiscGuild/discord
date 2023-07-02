from __main__ import bot
from datetime import datetime, timedelta

from discord.ext import tasks

from src.func.General import General
from src.func.Integer import Integer
from src.utils.consts import weekly_lb_channel, daily_lb_channel, guild_handle, error_channel_id
from src.utils.request_utils import get_name_by_uuid, get_guild_by_name, get_mojang_profile
from src.utils.db_utils import (connect_db, select_all)
from src.utils.giveaway_utils import roll_giveaway

import string

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
async def updategexp():
    month = "07"
    progress_message = await bot.get_channel(error_channel_id).send("Authorizing connection...")

    import pygsheets
    gc = pygsheets.authorize(client_secret='creds.json') # NEED TO FIGURE OUT
    wk = gc.open_by_key("113fOSu-4yjlK2XuwEisWhiaueL0_SnaXOITEa7IYhmg")[0]
    await progress_message.edit(content=f"Fetching all records")
    records = wk.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False)

    guild = await get_guild_by_name(guild_handle)

    for member in guild["members"]:
        uuid = member["uuid"]
        name = await get_name_by_uuid(uuid)

        if not wk.find(name) or not wk.find(uuid):
            wk.append_table([[name], [uuid]], start="A2", dimension="COLUMNS", overwrite=False)

    participant_names = [x for x in wk.get_col(1)[1:] if x != ""]
    participant_uuids = [x for x in wk.get_col(2)[1:] if x != ""]
    # Gets rid of the empty trailing strings and ignores the column header

    cell_no = 2
    dates = {}
    for i in range(1, 32):
        if i > 24:
            dates[f"2023-{month}-{i:0>2}"] = 'A' + string.ascii_uppercase[i - 25]
            continue

        dates[f"2023-{month}-{i:0>2}"] = string.ascii_uppercase[i + 1]

    for name in participant_names:
        await progress_message.edit(content=f"Updating {name}")
        if not name:
            cell_no += 1
            continue
        # Find player in guild
        for member in guild["members"]:
            if member["uuid"] == participant_uuids[participant_names.index(name)]:
                # Get player data
                gexp_history = member["expHistory"]

                for k,v in gexp_history.items():
                    if (str(k).split('-'))[1] == month:
                        wk.update_value(f'{dates[k]}{cell_no}', v)

        cell_no += 1

@updategexp.before_loop
async def before_updategexp():
    await bot.wait_until_ready()

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
