from __main__ import bot
from typing import Tuple

import aiosqlite


async def connect_db():
    bot.db = await aiosqlite.connect("database.db")
    # Discord Member Table:
    await bot.db.execute("""CREATE TABLE IF NOT EXISTS members (
        discord_id integer PRIMARY KEY NOT NULL,
        uuid text NOT NULL, 
        username text,
        do_pings integer DEFAULT 1)""")

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

    await bot.db.execute("""CREATE TABLE IF NOT EXISTS invites(
        inviter_uuid text NOT NULL,
        current_invitee_uuids text,
        total_invites integer,
        total_valid_invites integer)""")

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


async def delete_dnkl(uuid: str):
    await bot.db.execute("DELETE FROM dnkl WHERE uuid = (?)", (uuid,))
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


async def insert_new_inviter(inviter_uuid: str, invitee_uuid: str):
    await bot.db.execute("INSERT INTO invites VALUES (?, ?, 0, 0)",
                         (inviter_uuid, invitee_uuid))
    await bot.db.commit()


async def add_invitee(inviter_uuid, invitee_uuid):
    invitees = (await select_one("SELECT current_invitee_uuids FROM invites WHERE inviter_uuid = (?)",
                                 (inviter_uuid,)))[0].split(" ")
    if invitee_uuid in invitees:
        return None

    invitees.append(invitee_uuid)
    count = len(invitees)
    invitees = " ".join([str(invitee) for invitee in invitees])
    await bot.db.execute("UPDATE invites SET current_invitee_uuids = (?) WHERE inviter_uuid = (?)",
                         (invitees, inviter_uuid))
    await bot.db.commit()

    return count


async def get_invites(inviter_uuid):
    return (await select_one(
        "SELECT current_invitee_uuids, total_invites, total_valid_invites FROM invites WHERE inviter_uuid = (?)",
        (inviter_uuid,)))


async def get_db_uuid_username_from_discord_id(discord_id: int):
    res = await select_one("SELECT uuid, username from members WHERE discord_id = (?)", (discord_id,))
    return (res[0], res[1]) if res else (None, None)

async def get_db_username_from_uuid(uuid: str):
    username = await select_one("SELECT username from members WHERE uuid = (?)", (uuid,))
    return username[0] if username else username

async def insert_new_member(discord_id: int, uuid: str, username: str):
    await bot.db.execute("INSERT INTO members VALUES (?, ?, ?)", (discord_id, uuid, username))
    await bot.db.commit()


async def update_member(discord_id: int, uuid: str, username: str):
    discord_idExists = await select_one("SELECT uuid from members WHERE discord_id = (?)", (discord_id,))
    if discord_idExists:
        await bot.db.execute("UPDATE members SET uuid = ?, username = ? WHERE discord_id = ?",
                             (uuid, username, discord_id))
        await bot.db.commit()
    else:
        await insert_new_member(discord_id, uuid, username)


async def check_uuid_in_db(uuid: str):
    discord_id = (await select_one("SELECT discord_id from members WHERE uuid=(?)", (uuid,)))
    return discord_id[0] if discord_id else 0

async def update_db_username(uuid: str, username: str):
    await bot.db.execute("UPDATE members SET username = ? WHERE uuid = ?", (username, uuid,))
    await bot.db.commit()

async def get_discordid_doping_db(uuid: str) -> Tuple[int, bool]:
    res = await select_one("SELECT discord_id, do_pings from members WHERE uuid = (?)", (uuid,))
    return (res[0], res[1]) if res else (0, 0)

async def set_do_ping_db(discord_id: int, do_pings: int) -> str:
    await bot.db.execute("UPDATE members set do_pings = ? WHERE discord_id = ?", (do_pings, discord_id))
    await bot.db.commit()
    
    return (await get_db_uuid_username_from_discord_id(discord_id))[0]