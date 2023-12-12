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

    await bot.db.execute("""CREATE TABLE IF NOT EXISTS invites(
        inviter_uuid text NOT NULL,
        current_invitee_uuids text,
        total_invites integer,
        total_valid_invites integer)""")

    await bot.db.execute("""CREATE TABLE IF NOT EXISTS tournament(
        uuid text PRIMARY KEY NOT NULL,
        start_data text NOT NULL,
        week1_data text,
        week2_data text,
        week3_data text,
        week3_end_data text,
        end_data text)""")

    # Commit any changes
    await bot.db.commit()


'''

games_played_bedwars
deaths_bedwars
wins_bedwars
final_kills_bedwars
final_deaths_bedwars
challenges

SOLO
eight_one_final_kills_bedwars
eight_one_kills_bedwars
eight_one_beds_broken_bedwars
eight_one_wins_bedwars
eight_one_games_played_bedwars

DOUBLES
eight_two_final_kills_bedwars
eight_two_kills_bedwars
eight_two_beds_broken_bedwars
eight_two_wins_bedwars
eight_two_games_played_bedwars

THREES
four_three_final_kills_bedwars
four_three_kills_bedwars
four_three_beds_broken_bedwars
four_three_wins_bedwars
four_three_games_played_bedwars

FOURS
four_four_final_kills_bedwars
four_four_kills_bedwars
four_four_beds_broken_bedwars
four_four_wins_bedwars
four_four_games_played_bedwars

4v4
two_four_final_kills_bedwars
two_four_kills_bedwars
two_four_beds_broken_bedwars
two_four_wins_bedwars
two_four_games_played_bedwars

'''


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


async def new_tournament_player(uuid: str, start_data: dict, week_data: dict, week_num: int):
    await bot.db.execute("INSERT INTO tournament VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (uuid, str(start_data), None, None, None, None, None))

    await bot.db.execute(f"UPDATE tournament SET week{week_num}_data = (?) WHERE uuid = (?)",
                         (str(week_data), uuid))
    await bot.db.commit()


async def set_weekly_data(uuid: str, week_data: dict, week_num: int):
    if week_num == 4:
        await bot.db.execute(f"UPDATE tournament SET week3_end_data = (?) WHERE uuid = (?)",
                             (str(week_data), uuid))
    elif week_num == -1:
        await bot.db.execute(f"UPDATE tournament SET end_data = (?) WHERE uuid = (?)",
                             (str(week_data), uuid))
    else:
        await bot.db.execute(f"UPDATE tournament SET week{week_num}_data = (?) WHERE uuid = (?)",
                             (str(week_data), uuid))

    await bot.db.commit()
