# utilities.py
import datetime
import math
import random
from datetime import datetime

import aiohttp
import discord
import toml

configFile = toml.load('config.toml')


def get_api():
    API_KEY = configFile['hypixel']['api_keys']

    api = random.choice(API_KEY)
    return api


async def get_data(name):
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/player?key={api}&name={name}") as resp:
            req = await resp.json(content_type=None)
    return req


async def get_data1(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.slothpixel.me/api/players/{name}") as resp:
            req = await resp.json(content_type=None)
    return req


async def get_guild_data(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.slothpixel.me/api/guilds/{name}") as resp:
            req = await resp.json(content_type=None)
    return req


async def get_leaderboards():
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.hypixel.net/leaderboards?key={api}") as resp:
            req = await resp.json(content_type=None)
    if req["success"]:
        return req
    elif not req["success"]:
        return None


async def name_grabber(author):
    name = author.nick
    if not name:
        name = author.name
    else:
        name = name.split()[0]
    return name



async def get_level(name):
    data = await get_data(name)
    if not data["player"]:
        return None
    exp = int(data["player"]["networkExp"])  # This just gets the player experience from our data
    exp = (math.sqrt((2 * exp) + 30625) / 50) - 2.5
    return round(exp, 2)


async def get_karma(name):
    data = await get_data(name)
    if 'cause' in data:
        print(data['cause'])
    if not data["player"]:
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
    if len(name) < 20 and name.isascii():
        api = get_api()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.hypixel.net/player?key={api}&name={name}") as resp:
                data = await resp.json(content_type=None)
                await session.close()
    else:
        data = await get_data(name)
    if 'cause' in data:
        print(data['cause'])
    if not data["player"]:
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

            request = await request.json(content_type=None)
            uuid = request['id']
            api = get_api()
            async with session.get(f"https://api.hypixel.net/guild?key={api}&player={uuid}") as resp:
                req = await resp.json(content_type=None)
                await session.close()
    if 'cause' in req:
        print(req['cause'], api)
    elif req['guild']:
        gname = req["guild"]['name']
        return (f"{gname}")
    else:
        return None


async def get_gtag(name):
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.hypixel.net/guild?key={api}&name={name}') as resp:
            req = await resp.json(content_type=None)
            await session.close()
    if len(req['guild']) < 2:
        return (" ")
    if not req["guild"]["tag"]:
        return (" ")
    else:
        gtag = req["guild"]["tag"]
        return (f"[{gtag}]")


async def get_dispnameID(name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
            request = await resp.json(content_type=None)
            await session.close()
    if request and 'error' not in request:
        ign = request["name"]
        id = request["id"]
        return ign, id
    else:
        return None, None


async def get_flogin(name):
    data = await get_data(name)
    if not data["player"]:
        return None
    first_login = data["player"]["firstLogin"]
    time = datetime.fromtimestamp(int(str(first_login)[:-3]))
    return time


async def get_llogin(name):
    data = await get_data(name)
    if not data["player"]:
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
    if not data["player"]:
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
    if request["online"]:
        return True
    else:
        return False


async def get_guild_members(gname):
    api = get_api()
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.hypixel.net/guild?key={api}&name={gname}') as resp:
            req = await resp.json(content_type=None)
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
            req = await resp.json(content_type=None)
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
    if not name:  # If they don't have a nick, it uses their name.
        name = member.name

    with session.get(base_url + name) as mojang:
        data = mojang.json(content_type=None)

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
    elif not tag.isascii():
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
    '''@commands.command()
    @commands.has_role("Staff")
    async def information_aa(self, ctx, send_ping=None):
        body = \'\'\'Miscellaneous is an all games Hypixel guild. Our primary goal is to be a guild that is friendly to everyone. All of our guild requirements are well thought out. Miscellaneous strives to be a good community while maintaining its position on the guild leaderboards.We are a 2014 guild which makes us one of the OG hypixel guilds. We, the miscellaneous staff team will do anything to protect the legacy of this spectacle of a guild.\'\'\'
        embed = discord.Embed(description=body,color=0x8368ff)
        embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/rey4uPv9eHzVTkM9_GVWvWiK1jyrtBy_sUQjBaE5qbE/https/images-ext-2.discordapp.net/external/oTPK3H5eQJWBw_syuTTVUJ3yP7YkvvXTb0JbMX0cdJQ/https/images-ext-1.discordapp.net/external/ziYSZZe7dPyKDYLxA1s2jqpKi-kdCvPFpPaz3zft-wo/%25253Fwidth%25253D671%252526height%25253D671/https/media.discordapp.net/attachments/523227151240134664/803843877999607818/misc.png")
        embed.set_author(name="Miscellaneous",url="https://plancke.io/hypixel/guild/name/Miscellaneous")
        partners = \'\'\'XL - https://discord.gg/XvqCvYn
                    Lucid - https://discord.gg/DDTMad2pYR
                    OUT - https://discord.gg/OUT
                    Betrayed - https://discord.gg/Betrayed
                    Cronos - https://discord.gg/DgfUSPEQ
                    Blight - https://discord.gg/dgTWpgy
                    Cubelify - https://cubelify.com/ / https://discord.gg/cubelify\'\'\'
        embed.add_field(name="Partners",value=partners,inline=False)
        links = \'\'\'Guild Website: https://miscguild.xyz/
                Guild Thread: http://bit.ly/MiscThread
                Permanent Discord Invite Link: https://discord.gg/bHFWukp\'\'\'
        embed.add_field(name="Useful Links",value=links,inline=False)
        embed.set_footer(text="This guild was founded by @Fantastic_Doge")
        await ctx.send("https://images-ext-2.discordapp.net/external/FTPm31ZbVY3GRGwU7XsrBeCEPo3U5dtkuOM55jj__qA/https/media.discordapp.net/attachments/522862347388190801/874785998498852874/information.jpg")
        await ctx.send(embed=embed)'''