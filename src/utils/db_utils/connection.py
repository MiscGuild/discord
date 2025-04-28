from __main__ import bot
from typing import Tuple

import aiosqlite


async def connect_db():
    bot.db = await aiosqlite.connect("database.db")

    await bot.db.execute("""CREATE TABLE IF NOT EXISTS users (
        uuid TEXT PRIMARY KEY NOT NULL,
        username TEXT NOT NULL);""")

    # Discord Member Table:
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS members (
        discord_id integer PRIMARY KEY NOT NULL,
        uuid text NOT NULL, 
        username text,
        do_pings integer DEFAULT 1,
        FOREIGN KEY (uuid) REFERENCES users(uuid) ON DELETE CASCADE);""")

    # DNKL table:
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS dnkl (
    message_id INTEGER PRIMARY KEY NOT NULL,
    uuid TEXT NOT NULL,
    FOREIGN KEY (uuid) REFERENCES users(uuid) ON DELETE CASCADE
);""")

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

    # Invites table
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS invites(
            inviter_uuid          text NOT NULL,
            current_invitee_uuids text,
            total_invites         integer,
            total_valid_invites   integer,
            foreign key (inviter_uuid) references users (uuid)
        );""")

    # Guild Members table
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS guild_member_data_temp (
            uuid text NOT NULL,
            gexp_history text,
            foreign key (uuid) references users (uuid),
            primary key (uuid)
        );""")

    await bot.db.execute("""CREATE TABLE IF NOT EXISTS elite_members(
        uuid text NOT NULL,
        is_booster boolean NOT NULL DEFAULT 0,
        is_sponsor boolean NOT NULL DEFAULT 0,
        is_gvg boolean NOT NULL DEFAULT 0,
        is_creator boolean NOT NULL DEFAULT 0,
        is_indefinite boolean NOT NULL,
        expiry text,
        FOREIGN KEY (uuid) REFERENCES users(uuid) ON DELETE CASCADE)""")

    # Commit any changes
    await bot.db.commit()


async def base_query(query: str, values: Tuple = None) -> aiosqlite.Cursor:
    # Insert values into query if necessary
    if not values:
        return await bot.db.execute(query)
    return await bot.db.execute(query, values)


# Generic select one row function
async def select_one(query: str, values: Tuple = None) -> Tuple | None:
    cursor = await base_query(query, values)
    row = await cursor.fetchone()
    await cursor.close()
    return row


# Generic select many rows functions
async def select_all(query: str, values: Tuple = None) -> list:
    cursor = await base_query(query, values)
    rows = await cursor.fetchall()
    await cursor.close()
    return list(rows)
