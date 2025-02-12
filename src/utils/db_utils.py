import json
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
        reason text NOT NULL,
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


async def check_and_update_username(uuid: str, username: str = None) -> None:
    cursor = await bot.db.execute(
        "UPDATE users SET username = (?) WHERE uuid = (?) AND (username IS NOT (?) OR username IS NULL)",
        (username, uuid, username)
    )

    if cursor.rowcount == 0:
        await bot.db.execute(
            "INSERT INTO users (uuid, username) VALUES (?, ?)",
            (uuid, username)
        )

    await bot.db.commit()


### DNKL
async def insert_new_dnkl(message_id: int, uuid: str, username: str) -> None:
    await bot.db.execute("INSERT INTO dnkl VALUES (?, ?)", (message_id, uuid))
    await bot.db.commit()
    await check_and_update_username(uuid, username)


async def update_dnkl(message_id: int, uuid: str) -> None:
    await bot.db.execute("UPDATE dnkl SET message_id = (?) WHERE uuid = (?)", (message_id, uuid,))
    await bot.db.commit()


async def delete_dnkl(uuid: str) -> None:
    await bot.db.execute("DELETE FROM dnkl WHERE uuid = (?)", (uuid,))
    await bot.db.commit()


### Giveaways
async def insert_new_giveaway(msg_id: int, channel_id: int, prize: str, number_winners: int, time_of_finish: str,
                              req_gexp: int, all_roles_required: bool, req_roles: str, sponsors: str) -> None:
    await bot.db.execute("INSERT INTO Giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
        msg_id, channel_id, prize, number_winners, time_of_finish, req_gexp, all_roles_required, req_roles, sponsors,
        True))
    await bot.db.commit()


async def get_giveaway_status(id: int) -> Tuple[bool] | None:
    return await select_one("SELECT is_active FROM giveaways WHERE message_id = (?)", (id,))


async def set_giveaway_inactive(id: int) -> None:
    await bot.db.execute(f"Update giveaways SET is_active = 0 WHERE message_id = (?)", (id,))
    await bot.db.commit()


async def insert_new_inviter(inviter_uuid: str, invitee_uuid: str) -> None:
    await bot.db.execute("INSERT INTO invites VALUES (?, ?, 0, 0)",
                         (inviter_uuid, invitee_uuid))
    await bot.db.commit()

    await check_and_update_username(inviter_uuid)
    await check_and_update_username(invitee_uuid)


async def add_invitee(inviter_uuid, invitee_uuid) -> int | None:
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

    await check_and_update_username(invitee_uuid)
    return count


async def get_invites(inviter_uuid) -> Tuple[str, int, int] | None:
    return (await select_one(
        "SELECT current_invitee_uuids, total_invites, total_valid_invites FROM invites WHERE inviter_uuid = (?)",
        (inviter_uuid,)))


async def get_db_uuid_username(discord_id: int = None, username: str = None, uuid: str = None,
                               get_discord_id: bool = False) -> Tuple[
                                                                    str, str] | Tuple[str, str, int] | Tuple[
                                                                    None, None]:
    if discord_id:
        uuid = await get_uuid_from_discord_id(discord_id)
        return await get_username_from_uuid(uuid)
    if username:
        username, uuid = await get_uuid_from_username(username)
        if not uuid:
            return None, None
        if get_discord_id:
            discord_id = await get_discord_id_from_uuid(uuid)
            return username, uuid, discord_id
    if uuid:
        username, uuid = await get_username_from_uuid(uuid)
        if not username:
            return None, None
        if get_discord_id:
            discord_id = await get_discord_id_from_uuid(uuid)
            return username, uuid, discord_id

    return None, None

async def get_username_from_uuid(uuid: str) -> Tuple[str, str] | None:
    res = await select_one("SELECT username from users WHERE uuid = (?)", (uuid,))
    return res[0], uuid if res else None


async def get_uuid_from_username(username: str) -> Tuple[str, str] | None:
    res = await select_one("SELECT uuid from users WHERE username = (?)", (username,))
    return username, res[0] if res else None


async def get_uuid_from_discord_id(discord_id: int) -> str:
    res = await select_one("SELECT uuid from members WHERE discord_id = (?)", (discord_id,))
    return res[0] if res else None


async def get_discord_id_from_uuid(uuid: str) -> int | None:
    res = await select_one("SELECT discord_id from members WHERE uuid = (?)", (uuid,))
    return int(res[0]) if res else None


async def insert_new_member(discord_id: int, uuid: str, username: str) -> None:
    await bot.db.execute("INSERT INTO members VALUES (?, ?, ?, ?)", (discord_id, uuid, username, 1))
    await bot.db.commit()


async def update_member(discord_id: int, uuid: str, username: str) -> None:
    discord_idExists = await select_one("SELECT uuid from members WHERE discord_id = (?)", (discord_id,))
    if discord_idExists:
        await bot.db.execute("UPDATE members SET uuid = ?, username = ? WHERE discord_id = ?",
                             (uuid, username, discord_id))
        await bot.db.commit()
    else:
        await insert_new_member(discord_id, uuid, username)


async def check_uuid_in_db(uuid: str) -> int:
    discord_id = (await select_one("SELECT discord_id from members WHERE uuid=(?)", (uuid,)))
    return discord_id[0] if discord_id else 0


async def update_db_username(uuid: str, username: str) -> None:
    await bot.db.execute("UPDATE members SET username = ? WHERE uuid = ?", (username, uuid,))
    await bot.db.commit()


async def get_discordid_doping_db(uuid: str) -> Tuple[int, bool]:
    res = await select_one("SELECT discord_id, do_pings from members WHERE uuid = (?)", (uuid,))
    return (res[0], res[1]) if res else (0, 0)


async def set_do_ping_db(discord_id: int, do_pings: int) -> str:
    await bot.db.execute("UPDATE members set do_pings = ? WHERE discord_id = ?", (do_pings, discord_id))
    await bot.db.commit()

    return (await get_db_uuid_username(discord_id=discord_id))[0]


async def get_all_guild_members() -> list:
    return await select_all("SELECT uuid from guild_member_data")


async def remove_guild_member(uuid: str) -> None:
    await bot.db.execute("DELETE FROM guild_member_data WHERE uuid = (?)", (uuid,))
    await bot.db.commit()


async def get_member_gexp_history(uuid: str) -> dict:
    history = await select_one("SELECT gexp_history from guild_member_data WHERE uuid = (?)", (uuid,))
    return json.loads(history[0]) if history else None


async def set_member_gexp_history(uuid: str, gexp_history: dict) -> dict:
    current_history: dict = await get_member_gexp_history(uuid)

    if not current_history:
        # Direct insert if no existing history
        await bot.db.execute("INSERT INTO guild_member_data VALUES (?, ?)", (uuid, json.dumps(gexp_history)))
        await bot.db.commit()
        return gexp_history

    current_history.update(gexp_history)

    sorted_history = dict(sorted(current_history.items(), reverse=True))

    limited_history = dict(list(sorted_history.items())[:365])  # Keeps the 365 most recent entries

    await bot.db.execute("UPDATE guild_member_data SET gexp_history = ? WHERE uuid = ?",
                         (json.dumps(limited_history), uuid))
    await bot.db.commit()

    return limited_history


async def get_elite_member(uuid: str) -> Tuple[str, str] | None:
    return await select_one("SELECT reason, expiry from elite_members WHERE uuid = (?)", (uuid,))


async def insert_elite_member(uuid: str, reason: str, expiry: str = None) -> None:
    await bot.db.execute("INSERT INTO elite_members VALUES (?, ?, ?)", (uuid, reason, expiry))
    await bot.db.commit()
