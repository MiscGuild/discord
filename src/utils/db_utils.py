from __main__ import bot
from typing import Tuple

import aiosqlite


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

    # Residents table:
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS residency(
    discord_id integer PRIMARY KEY NOT NULL,
    uuid text NOT NULL,
    reason text NOT NULL,
    time_of_finish text NOT NULL,
    warnings integer,
    warnings_updated text)""")

    # Commit any changes
    await bot.db.commit()


async def base_query(query: str, values: Tuple = None):
    # Insert values into query if necessary
    if not values:
        return await bot.db.execute(query)
    return await bot.db.execute(query, values)


# Generic select one row function
async def select_one(query: str, values: Tuple = None):
    cursor = await base_query(query, values)
    row = await cursor.fetchone()
    await cursor.close()
    return row


# Generic select many rows functions
async def select_all(query: str, values: Tuple = None):
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
async def insert_new_giveaway(msg_id: int, channel_id: int, prize: str, number_winners: int, time_of_finish: str,
                              req_gexp: int, all_roles_required: bool, req_roles: str, sponsors: str):
    await bot.db.execute("INSERT INTO Giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
        msg_id, channel_id, prize, number_winners, time_of_finish, req_gexp, all_roles_required, req_roles, sponsors,
        True))
    await bot.db.commit()


async def get_giveaway_status(id: int):
    return await select_one("SELECT is_active FROM giveaways WHERE message_id = (?)", (id,))


async def set_giveaway_inactive(id: int):
    await bot.db.execute(f"Update giveaways SET is_active = 0 WHERE message_id = (?)", (id,))
    await bot.db.commit()


async def insert_new_residency(discord_id: int, uuid: str, reason: str, time_of_finish: str, warnings: int = 0,
                               warnings_updated: str = ""):
    await bot.db.execute(f"INSERT INTO residency VALUES (?, ?, ?, ?, ?, ?)",
                         (discord_id, uuid, reason, time_of_finish, warnings, warnings_updated))
    await bot.db.commit()


async def update_residency(discord_id: int, reason: str, time_of_finish: str, warnings: int, warnings_updated: str):
    await bot.db.execute(
        "UPDATE residency SET reason = (?), time_of_finish = (?), warnings = (?), warnings_updated = (?) WHERE discord_id = (?)",
        (reason, time_of_finish, warnings, warnings_updated, discord_id))
    await bot.db.commit()


async def delete_residency(discord_id: int):
    await bot.db.execute("DELETE FROM residency WHERE discord_id = (?)", (discord_id,))
    await bot.db.commit()
