import toml
import random

api_keys = toml.load("config.toml")["hypixel"]["api_keys"]

async def get_hyapi_key():
    return random.choice(api_keys)