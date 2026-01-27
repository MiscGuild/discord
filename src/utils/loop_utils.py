import asyncio
from __main__ import bot
from datetime import datetime, timezone, timedelta

import pytz
from discord.ext import tasks

from src.func.General import General
from src.func.Integer import Integer
from src.utils.calculation_utils import get_guild_gexp_data
from src.utils.consts import WEEKLY_LB_CHANNEL_ID, DAILY_LB_CHANNEL_ID, GUILD_HANDLE
from src.utils.db_utils import (select_all, set_member_gexp_history, get_all_guild_members, get_all_elite_members,
                                delete_elite_member)
from src.utils.discord_utils import update_recruiter_role
from src.utils.giveaway_utils import roll_giveaway
from src.utils.referral_utils import check_invitation_validity, generate_rank_upgrade
from src.utils.request_utils import get_guild_by_name


@tasks.loop(minutes=1)
async def check_giveaways() -> None:
    # Get all giveaway data
    all_giveaways = await select_all(
        "SELECT message_id, time_of_finish, is_active FROM giveaways"
    )

    now = datetime.now(timezone.utc)
    deletes = []

    for message_id, time_of_finish, is_active in all_giveaways:
        # Parse as naive, then mark it as UTC-aware
        finish_at = datetime.strptime(time_of_finish, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

        if is_active and finish_at < now:
            await roll_giveaway(message_id)

        elif (not is_active) and (now > finish_at + timedelta(days=10)):
            deletes.append((message_id,))

    if deletes:
        await bot.db.executemany("DELETE FROM giveaways WHERE message_id = (?)", deletes)
        await bot.db.commit()


async def scheduler() -> None:
    while True:
        now = datetime.now(pytz.utc)
        est = pytz.timezone("America/New_York")
        now_est = now.astimezone(est)

        # Run immediately
        await update_gexp()
        await update_elite_members()

        # Get next 12 AM EST
        next_run_est = now_est.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        next_run_utc = next_run_est.astimezone(pytz.utc)

        # Sleep until 11:59 PM EST
        sleep_time_invites = (next_run_utc - datetime.now(pytz.utc)).total_seconds() - 60
        if sleep_time_invites > 0:
            await asyncio.sleep(sleep_time_invites)

        await update_invites()

        # Sleep until 12:05 AM EST
        now = datetime.now(pytz.utc)
        remaining_sleep_time = (next_run_utc - now).total_seconds() + 300
        if remaining_sleep_time > 0:
            await asyncio.sleep(remaining_sleep_time)

        await send_gexp_lb()


async def before_scheduler() -> None:
    """Ensures the bot is ready before starting the scheduler."""
    await bot.wait_until_ready()
    await asyncio.sleep(5)
    asyncio.create_task(scheduler())  # Start the scheduler loop


async def send_gexp_lb() -> None:
    file = await Integer(integer=1).gtop(is_automatic=True)
    await bot.get_channel(DAILY_LB_CHANNEL_ID).send(file)

    # If it's Monday (UTC), send weekly leaderboard
    if datetime.now(timezone.utc).weekday() == 0:
        start_date = datetime.strptime('14/08/2022', '%d/%m/%Y').replace(tzinfo=timezone.utc)
        current_date = datetime.now(timezone.utc)
        week_number = int(80 + round((current_date - start_date).days / 7))

        week_message = (
            f"__Week {week_number}__\n"
            f"**{(current_date - timedelta(days=7)).strftime('%d %b %Y')} "
            f"- {current_date.strftime('%d %B %Y')}**"
        )

        await bot.get_channel(WEEKLY_LB_CHANNEL_ID).send(week_message)
        await bot.get_channel(WEEKLY_LB_CHANNEL_ID).send(
            await General().weeklylb(is_automatic=True)
        )


async def update_invites() -> None:
    if datetime.now(timezone.utc).weekday() != 0:
        return
    invites_data = await select_all("SELECT * FROM invites")
    weekly_invitations = []
    for inviter_uuid, current_invitee_uuids, total_invites, total_valid_invites in invites_data:
        weekly_uuids = current_invitee_uuids.split(" ")
        weekly_count = len(weekly_uuids)
        total_invites = total_invites + weekly_count
        valid_invites = await check_invitation_validity(weekly_uuids)
        weekly_invitations.append((inviter_uuid, valid_invites))
        total_valid_invites = total_valid_invites + len(valid_invites)
        await update_recruiter_role(inviter_uuid, len(valid_invites))
        await bot.db.execute(
            "UPDATE invites SET total_invites = (?), total_valid_invites = (?), current_invitee_uuids = '' WHERE inviter_uuid = (?)",
            (total_invites, total_valid_invites, inviter_uuid))
    await bot.db.commit()

    await generate_rank_upgrade(weekly_invitations)


async def update_gexp() -> None:
    guild_data = await get_guild_by_name(GUILD_HANDLE)
    if not guild_data:
        return

    gexp_data = await get_guild_gexp_data(guild_data)

    for uuid, exp_history in gexp_data.items():
        await set_member_gexp_history(uuid, exp_history)

    all_members_in_db = await get_all_guild_members()

    for uuid in all_members_in_db:
        uuid = uuid[0]
        if uuid not in gexp_data:
            continue


async def update_elite_members() -> None:
    elite_members = await get_all_elite_members()

    if not elite_members:
        return

    for uuid, is_booster, is_sponsor, is_gvg, is_creator, is_indefinite, expiry in elite_members:
        if is_indefinite:
            continue

        if expiry and datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) < datetime.now(
                timezone.utc):
            await delete_elite_member(uuid)
