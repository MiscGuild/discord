# This file contains all db-related functions for inserting, updating, deleting rows etc

from __main__ import bot
from typing import Tuple

async def create_tables():
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
        role_requirement_type text NOT NULL,
        required_roles text,
        required_gexp integer NOT NULL,
        sponsors text NOT NULL,
        status text NOT NULL)""")

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


### DNKL
async def insert_new_dnkl(message_id: int, uuid: str, username: str):
    await bot.db.execute("INSERT INTO dnkl VALUES (?, ?, ?)", (message_id, uuid, username,))

async def update_dnkl(message_id: int, uuid: str):
    await bot.db.execute("UPDATE dnkl SET message_id = (?) WHERE uuid = (?)", (message_id, uuid,))
    await bot.db.commit()

### Giveaways
