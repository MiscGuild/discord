# This file contains all db-related functions for inserting, updating, deleting rows etc

from datetime import datetime, timedelta
from typing import Tuple

import aiosqlite
from __main__ import bot
from discord.ext import tasks
from func.utils.discord_utils import roll_giveaway


async def connect_db():
    bot.db = await aiosqlite.connect("database.db")

    # DNKL table:
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS dnkl (
        message_id integer NOT NULL,
        uuid text NOT NULL,
        username text NOT NULL)""")

    # Giveaways table
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS giveaways (
        message_id integer PRIMARY KEY NOT NULL,
        channel_id integer NOT NULL,
        prize text NOT NULL,
        number_winners integer NOT NULL,
        time_of_finish text NOT NULL,
        required_gexp integer NOT NULL,
        all_roles_required boolean NOT NULL,
        required_roles text,
        sponsors text NOT NULL,
        is_active boolean NOT NULL)""")

    # Commit any changes
    await bot.db.commit()


async def base_query(query: str, values: Tuple=None):
    # Insert values into query if necessary
    if values == None:
        return await bot.db.execute(query)
    else:
        return await bot.db.execute(query, values)


# Generic select one row function
async def select_one(query: str, values: Tuple=None):
    cursor = await base_query(query, values)
    row = await cursor.fetchone()
    await cursor.close()
    return row

# Generic select many rows functions
async def select_all(query: str, values: Tuple=None):
    cursor = await base_query(query, values)
    rows = await cursor.fetchall()
    await cursor.close()
    return rows

### DNKL
async def insert_new_dnkl(message_id: int, uuid: str, username: str):
    await bot.db.execute("INSERT INTO dnkl VALUES (?, ?, ?)", (message_id, uuid, username,))
    await bot.db.commit()

async def update_dnkl(message_id: int, uuid: str):
    await bot.db.execute("UPDATE dnkl SET message_id = (?) WHERE uuid = (?)", (message_id, uuid,))
    await bot.db.commit()

async def delete_dnkl(username: str):
    await bot.db.execute("DELETE FROM dnkl WHERE username = (?)", (username,))
    await bot.db.commit()

### Giveaways
async def insert_new_giveaway(msg_id: int, channel_id: int, prize: str, number_winners: int, time_of_finish: str, req_gexp: int, all_roles_required: bool, req_roles: str, sponsors: str):
    await bot.db.execute("INSERT INTO Giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (msg_id, channel_id, prize, number_winners, time_of_finish, req_gexp, all_roles_required, req_roles, sponsors, True))
    await bot.db.commit()

async def get_giveaway_status(id: int):
    return await select_one("SELECT is_active FROM giveaways WHERE message_id = (?)", (id,))

@tasks.loop(minutes=1)
async def check_giveaways(self):
    cursor = await self.bot.db.execute("SELECT message_id, status, time_of_finish FROM Giveaways")
    rows = await cursor.fetchall()
    await cursor.close()

    for row in rows:
        message_id, status, datetime_end_str = row
        datetime_end = datetime.strptime(datetime_end_str, "%Y-%m-%d %H:%M:%S")

        # Giveaway needs to be ended
        if status == "active" and datetime_end < datetime.utcnow():
            await roll_giveaway(message_id)

        # Giveaway ended more than 10 days ago, delete it
        elif status == "inactive" and datetime.utcnow() > datetime_end + timedelta(days=10):
            await self.bot.db.execute("DELETE FROM Giveaways WHERE message_id = (?)", (message_id,))
            await self.bot.db.commit()

@check_giveaways.before_loop
async def before_giveaway_check(self):
    await self.bot.wait_until_ready()

check_giveaways.start()
