import aiohttp

async def m_profile(name: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
            request = await resp.json(content_type=None)
            await session.close()

    # If player and request is valid
    if request != None and "error" not in request:
        return request["name"], request["id"]
    
    # Player does not exist
    return None, None
