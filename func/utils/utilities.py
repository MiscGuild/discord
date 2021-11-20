import datetime
import math
from datetime import datetime

import aiohttp
import discord


async def get_data(name):
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/player?key={api}&name={name}") as resp:
            req = await resp.json()
    return req


async def get_data1(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.slothpixel.me/api/players/{name}") as resp:
            req = await resp.json()
    return req


async def get_guild_data(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.slothpixel.me/api/guilds/{name}") as resp:
            req = await resp.json()
    return req


async def get_leaderboards():
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/leaderboards?key={api}") as resp:
            req = await resp.json()
    if req["success"]:
        return req
    elif not req["success"]:
        return None


async def name_grabber(author):
    name = author.nick
    if name is None:
        name = author.name
    else:
        name = name.split()[0]
    return name



async def get_level(name):
    data = await get_data(name)
    if data["player"] is None:
        return None
    exp = int(data["player"]["networkExp"])  # This just gets the player experience from our data
    exp = (math.sqrt((2 * exp) + 30625) / 50) - 2.5
    return round(exp, 2)


async def get_karma(name):
    data = await get_data(name)
    if 'cause' in data:
        print(data['cause'])
    if data["player"] is None:
        return None
    karma = int(data["player"]["karma"])
    return (f"{karma:,d}")


async def get_ap(name):
    request = await get_data1(name)
    if 'cause' in request:
        print(request['cause'])
    if "achievement_points" in request:
        ap = int(request["achievement_points"])
        return (f"{ap:,d}")
    else:
        return ("-")


async def get_rank(name):
    if len(name) < 20 and name.isascii() is True:
        api = get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.hypixel.net/player?key={api}&name={name}") as resp:
                data = await resp.json()
                await session.close()
    else:
        data = await get_data(name)
    if 'cause' in data:
        print(data['cause'])
    if data["player"] is None:
        return None
    if "prefix" in data["player"]:
        player_prefix = (data["player"]["prefix"])
        if player_prefix == "§d[PIG§b+++§d]":
            return (f"[PIG+++]")
        elif player_prefix == "§c[SLOTH]":
            return ("[SLOTH]")
        elif player_prefix == "§c[OWNER]":
            return ("[OWNER]")
    if "newPackageRank" in data["player"]:
        if "rank" in data["player"]:
            rank = (data["player"]["rank"])
            if rank == 'YOUTUBER':
                return ('[YOUTUBE]')
            if rank == 'ADMIN':
                return ('[ADMIN]')
            if rank == 'MODERATOR':
                return ('[MOD]')
            if rank == 'HELPER':
                return ('[HELPER]')
        else:
            rank = (data["player"]["newPackageRank"])
            if rank == 'MVP_PLUS':
                if "monthlyPackageRank" in data["player"]:
                    mvp_plus_plus = (data["player"]["monthlyPackageRank"])
                    if mvp_plus_plus == "NONE":
                        return ('[MVP+]')
                    else:
                        return ("[MVP++]")
                else:
                    return ("[MVP+]")
            elif rank == 'MVP':
                return ('[MVP]')
            elif rank == 'VIP_PLUS':
                return ('[VIP+]')
            elif rank == 'VIP':
                return ('[VIP]')
    else:
        return ('')


async def get_guild(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
            request = resp

            if resp.status != 200:
                await session.close()
                return None

            request = await request.json()
            uuid = request['id']
            api = get_api()
            async with session.get(f"https://api.hypixel.net/guild?key={api}&player={uuid}") as resp:
                req = await resp.json()
                await session.close()
    if 'cause' in req:
        print(req['cause'], api)
    elif req['guild'] is not None:
        gname = req["guild"]['name']
        return (f"{gname}")
    else:
        return None


async def get_gtag(name):
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.hypixel.net/guild?key={api}&name={name}') as resp:
            req = await resp.json()
            await session.close()
    if len(req['guild']) < 2:
        return (" ")
    if req["guild"]["tag"] is None:
        return (" ")
    else:
        gtag = req["guild"]["tag"]
        return (f"[{gtag}]")



async def get_flogin(name):
    data = await get_data(name)
    if data["player"] is None:
        return None
    first_login = data["player"]["firstLogin"]
    time = datetime.fromtimestamp(int(str(first_login)[:-3]))
    return time


async def get_llogin(name):
    data = await get_data(name)
    if data["player"] is None:
        return None
    if "lastLogin" in data["player"]:
        Last_login = data["player"]["lastLogin"]
        time = datetime.fromtimestamp(int(str(Last_login)[:-3]))
        return time
    else:
        return ('Unknown')


async def get_guild_level(exp):
    EXP_NEEDED = [
        100000,
        150000,
        250000,
        500000,
        750000,
        1000000,
        1250000,
        1500000,
        2000000,
        2500000,
        2500000,
        2500000,
        2500000,
        2500000,
        3000000, ]

    level = 0

    for i in range(0, 1000):
        need = 0
        if i >= len(EXP_NEEDED):
            need = EXP_NEEDED[len(EXP_NEEDED) - 1]
        else:
            need = EXP_NEEDED[i]
        i += 1

        if (exp - need) < 0:
            return round((level + (exp / need)) * 100) / 100
        level += 1
        exp -= need


async def get_challenges_completed(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
            request = resp

            if request.status != 200:
                return None
    data = await get_data(name)
    if data["player"] is None:
        return None
    if "general_challenger" in data["player"]["achievements"]:
        cp = int(data["player"]["achievements"]['general_challenger'])
        return (f"{cp:,d}")
    else:
        return ("0")


async def get_completed_quests(name):
    request = await get_data1(name)
    if "quests_completed" in request:
        cq = int(request["quests_completed"])
        return (f"{cq:,d}")
    else:
        return ("-")


async def get_online_status(name):
    request = await get_data1(name)
    if request["online"] is True:
        return True
    else:
        return False


async def get_guild_members(gname):
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.hypixel.net/guild?key={api}&name={gname}') as resp:
            req = await resp.json()
            await session.close()
    uuids = []
    for i in range(len(req['guild']['members'])):
        uuid = req['guild']['members'][i]['uuid']
        uuids.append(uuid)
    return uuids


async def get_misc_members(gname):
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.hypixel.net/guild?key={api}&name={gname}') as resp:
            req = await resp.json()
            await session.close()
    gmemberdata = []
    for i in range(len(req['guild']['members'])):
        uuid = req['guild']['members'][i]['uuid']
        expHistory = sum(req['guild']['members'][i]['expHistory'].values())
        gmemberdata.append([uuid, expHistory])
    return gmemberdata


def fetch(session, individual_uuid):
    base_url = "https://sessionserver.mojang.com/session/minecraft/profile/"
    with session.get(base_url + individual_uuid) as response:
        data = response.json()

        if response.status_code != 200:
            return None
        name = data['name']
        return name


def discord_member_check(session, member):
    invalid_members = []
    base_url = "https://api.mojang.com/users/profiles/minecraft/"

    name = member.nick  # Obtaining their nick
    if name is None:  # If they don't have a nick, it uses their name.
        name = member.name

    with session.get(base_url + name) as mojang:
        data = mojang.json()

        if mojang.status != 200:  # If the IGN is invalid
            invalid_members.append(member)
        return invalid_members


async def get_color(color, gexp, requirement):
    if color == "res_met":
        if gexp > requirement * 2:
            return 0x64ffdc, 'rgba(100, 255, 220,0.3)', 'rgba(100, 255, 220,0.3)'
        elif gexp > requirement:
            return 0x64ffb4, 'rgba(100, 255, 180,0.3)', 'rgba(100, 255, 180,0.3)'

    elif color == "res_not_met":
        if gexp * 2 < requirement:
            return 0xff6464, 'rgba(255, 100, 100,0.3)', 'rgba(255, 100, 100,0.3)'
        elif gexp * 2 > requirement:
            return 0xff8764, 'rgba(255, 135, 100,0.3)', 'rgba(255, 135, 100,0.3)'
        else:
            return 0xffb464, 'rgba(255, 180, 100,0.3)', 'rgba(255, 180, 100,0.3)'

    elif color == "active":
        if gexp * 2 < requirement:
            return 0xa064ff, 'rgba(160, 100, 255,0.3)', 'rgba(160, 100, 255,0.3)'
        elif gexp * 2 > requirement:
            return 0x6464ff, 'rgba(100, 100, 255,0.3)', 'rgba(100, 100, 255,0.3)'
        else:
            return 0x64b4ff, 'rgba(100, 180, 255,0.3)', 'rgba(100, 180, 255,0.3)'

    elif color == "member":
        if gexp * 2 < requirement:
            return 0x64c8ff, 'rgba(100, 200, 255,0.3)', 'rgba(100, 200, 255,0.3)'
        elif gexp * 2 > requirement:
            return 0x64e1ff, 'rgba(100, 225, 255,0.3)', 'rgba(100, 225, 255,0.3)'
        else:
            return 0x64ffff, 'rgba(100, 255, 255,0.3)', 'rgba(100, 255, 255,0.3)'

    elif color == "inactive":
        return 0xff6464, 'rgba(255, 100, 100,0.3)', 'rgba(255, 100, 100,0.3)'


def discord_verification(name, member: discord.Member):
    req = get_data1(name)
    if member.name == req['player']['socialMedia']['links']['DISCORD']:
        return True
    else:
        return False

async def check_tag(tag):
    tag = tag.lower()
    with open('badwords.txt', 'r') as f:
        badwords = f.read()

    if tag in badwords.split('\n'):
        return False, "The tag may not include profanity."
    elif tag.isascii() is False:
        return False, "Your tag may not include special characters unless it's the tag of an ally guild."
    elif len(tag) > 6:
        return False, "Your tag may not be longer than 6 characters."
    else:
        return True, None

async def get_tag_message():
    embed = discord.Embed(title="What would you like your tag to be? ",
                                url="https://media.discordapp.net/attachments/420572640172834816/867506975884181554/unknown.png",
                                description="**Rules:**"
                                            "\n• Tags can have a maximum length of 6 characters."
                                            " \n• Tags cannot include special characters."
                                            " \n• Tags cannot include profane language. ",
                                color=0x8368ff)
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/420572640172834816/867506975884181554/unknown.png")
    embed.set_footer(text="If you don't want a tag, type: None")
    return embed
