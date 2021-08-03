# hypixel.py
import aiohttp
import datetime
import math
import random
import toml
from datetime import datetime

configFile = toml.load('config.toml')


def get_api():
    API_KEY = configFile['hypixel']['api_keys']

    api = random.choice(API_KEY)
    return api


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
    print('Level acquired')
    return round(exp, 2)


async def get_karma(name):
    data = await get_data(name)
    if data["player"] is None:
        return None
    karma = int(data["player"]["karma"])
    print('Karma acquired')
    return (f"{karma:,d}")


async def get_ap(name):
    request = await get_data1(name)
    if "achievement_points" in request:
        ap = int(request["achievement_points"])
        print('AP acquired')
        return (f"{ap:,d}")
    else:
        return ("-")


async def get_rank(name):
    if len(name) > 20:
        api = get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.hypixel.net/player?key={api}&name={name}") as resp:
                data = await resp.json()
                await session.close()
    else:
        data = await get_data(name)
    if data["player"] is None:
        return None
    if "prefix" in data["player"]:
        player_prefix = (data["player"]["prefix"])
        if player_prefix == "§d[PIG§b+++§d]":
            print('Rank acquired- PIG')
            return (f"[PIG+++]")
        elif player_prefix == "§c[SLOTH]":
            print('Rank acquired- Sloth')
            return ("[SLOTH]")
        elif player_prefix == "§c[OWNER]":
            print('Rank acquired- Owner')
            return ("[OWNER]")
    if "newPackageRank" in data["player"]:
        if "rank" in data["player"]:
            rank = (data["player"]["rank"])
            if rank == 'YOUTUBER':
                return ('[YOUTUBE]')
            if rank == 'ADMIN':
                print('Rank acquired- Admin')
                return ('[ADMIN]')
            if rank == 'MODERATOR':
                print('Rank acquired- Moderator')
                return ('[MOD]')
            if rank == 'HELPER':
                print('Rank acquired- Helper')
                return ('[HELPER]')
        else:
            rank = (data["player"]["newPackageRank"])
            if rank == 'MVP_PLUS':
                if "monthlyPackageRank" in data["player"]:
                    mvp_plus_plus = (data["player"]["monthlyPackageRank"])
                    if mvp_plus_plus == "NONE":
                        print('Rank acquired- MVP+')
                        return ('[MVP+]')
                    else:
                        print('Rank acquired- MVP+')
                        return ("[MVP++]")
                else:
                    print('Rank acquired- MVP+')
                    return ("[MVP+]")
            elif rank == 'MVP':
                print('Rank acquired- MVP')
                return ('[MVP]')
            elif rank == 'VIP_PLUS':
                print('Rank acquired- VIP+')
                return ('[VIP+]')
            elif rank == 'VIP':
                print('Rank acquired- VIP')
                return ('[VIP]')
    else:
        print('Rank acquired- Non')
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
    if req['guild'] is not None:
        gname = req["guild"]['name']
        return (f"{gname}")
    else:
        return None


async def get_gtag(name):
    req = await get_guild_data(name)
    if len(req) < 2:
        return (" ")
    if req["tag"] is None:
        return (" ")
    else:
        gtag = req["tag"]
        return (f"[{gtag}]")


async def get_dispnameID(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
            request = await resp.json()
            await session.close()
    if 'error' not in request:
        ign = request["name"]
        id = request["id"]
        return ign, id
    else:
        return None, None


async def get_flogin(name):
    data = await get_data(name)
    if data["player"] is None:
        return None
    first_login = data["player"]["firstLogin"]
    time = datetime.fromtimestamp(int(str(first_login)[:-3]))
    print('First login acquired')
    return time


async def get_llogin(name):
    data = await get_data(name)
    if data["player"] is None:
        return None
    if "lastLogin" in data["player"]:
        Last_login = data["player"]["lastLogin"]
        time = datetime.fromtimestamp(int(str(Last_login)[:-3]))
        print('Last login acquired')
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
        3000000,
    ]
    level = 0

    for i in range(0, 1000):
        need = 0
        if i >= len(EXP_NEEDED):
            need = EXP_NEEDED[len(EXP_NEEDED) - 1]
        else:
            need = EXP_NEEDED[i]

        if ((exp - need) < 0):
            return round((((level + (exp / need)) * 100) / 100), 2)


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
        print('CP acquired')
        return (f"{cp:,d}")
    else:
        return ("0")


async def get_completed_quests(name):
    request = await get_data1(name)
    if "quests_completed" in request:
        cq = int(request["quests_completed"])
        print("CQ acquired")
        return (f"{cq:,d}")
    else:
        return ("-")


async def get_online_status(name):
    request = await get_data1(name)
    if request["online"] is True:
        print("The user is online")
        return True
    else:
        print("The user is offline")
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
        print(invalid_members)
        return invalid_members


async def get_color(color):
    if color == "res_met":
        l1 = [0x2c7354, 0x07AB99, 0x1b456b]
        l2 = ['rgba(44, 115, 84,0.3)', 'rgba(7, 171, 144,0.3)', 'rgba(6, 144, 87,0.3)']
        l3 = ['rgba(44, 115, 84,0.1)', 'rgba(7, 171, 144,0.1)', 'rgba(6, 144, 87,0.1)']

        index = random.randint(0, 2)

        return l1[index], l2[index], l3[index]

    elif color == "res_not_met":
        l1 = [0xf04747, 0xAD1B13, 0x620B06, 0xFF0000, 0xFF4C6E, 0xF068AA]
        l2 = ['rgba(240, 71, 71,0.3)',
              'rgba(173, 27, 19,0.3)',
              'rgba(98, 11, 6,0.3)',
              'rgba(255, 0, 0,0.3)',
              'rgba(255, 76, 110,0.3)',
              'rgba(240, 104, 170,0.3)']
        l3 = ['rgba(240, 71, 71,0.1)',
              'rgba(173, 27, 19,0.1)',
              'rgba(98, 11, 6,0.1)',
              'rgba(255, 0, 0,0.1)',
              'rgba(255, 76, 110,0.1)',
              'rgba(240, 104, 170,0.1)']

        index = random.randint(0, 5)

        return l1[index], l2[index], l3[index]

    elif color == "active":
        l1 = [0x96ADFF, 0x32AAF9, 0x0073BF, 0x07DFFF, 0x0731FF]
        l2 = ['rgba(150, 173, 255,0.3)',
              'rgba(50, 170, 249,0.3)',
              'rgba(0, 115, 191,0.3)',
              'rgba(7, 223, 255,0.3)',
              'rgba(0, 49, 255,0.3)']
        l3 = ['rgba(150, 173, 255,0.1)',
              'rgba(50, 170, 249,0.1)',
              'rgba(0, 115, 191,0.1)',
              'rgba(7, 223, 255,0.1)',
              'rgba(0, 49, 255,0.1)']

        index = random.randint(0, 4)

        return l1[index], l2[index], l3[index]

    elif color == "member":
        l1 = [0xA5FF4F, 0x4DFF00, 0x15FF63, 0x00FFAB]
        l2 = ['rgba(165, 255, 79,0.3)',
              'rgba(77, 255, 0,0.3)',
              'rgba(21, 255, 99,0.3)',
              'rgba(0, 255, 170,0.3)']
        l3 = ['rgba(165, 255, 79,0.1)',
              'rgba(77, 255, 0,0.1)',
              'rgba(21, 255, 99,0.1)',
              'rgba(0, 255, 170,0.1)']

        index = random.randint(0, 3)

        return l1[index], l2[index], l3[index]

    elif color == "inactive":
        l1 = [0xf04747, 0xAD1B13, 0x620B06, 0xFF0000, 0xFF4C6E, 0xF068AA]
        l2 = ['rgba(240, 71, 71,0.3)',
              'rgba(173, 27, 19,0.3)',
              'rgba(98, 11, 6,0.3)',
              'rgba(255, 0, 0,0.3)',
              'rgba(255, 76, 110,0.3)',
              'rgba(240, 104, 170,0.3)']
        l3 = ['rgba(240, 71, 71,0.1)',
              'rgba(173, 27, 19,0.1)',
              'rgba(98, 11, 6,0.1)',
              'rgba(255, 0, 0,0.1)',
              'rgba(255, 76, 110,0.1)',
              'rgba(240, 104, 170,0.1)']

        index = random.randint(0, 5)

        return l1[index], l2[index], l3[index]


