# The following file contains: mute, unmute, kick, ban, softban, unban, forcesync, add, remove, accept, avatar

from __main__ import bot
import discord
from typing import Union

from func.utils.consts import neg_color

class Union:
    def __init__(self, user: Union[discord.Member, discord.User]):
        self.user = user

    async def mute(self, author, guild_roles, reason: str=None):
        # Default reason is responsible moderator
        if reason == None:
            reason == f"Responsible moderator: {author}"

        await self.user.add_roles(discord.utils.get(guild_roles, name="Muted"))
        return discord.Embed(title="Muted!", description=f"{self.user} was muted by {author}!", color=neg_color)

    # async def unmute():

    # async def kick(reason: str=None):

    # async def ban(reason: str=None):

    # async def softban(reason: str=None):

    # async def unban():

    # async def forcesync(new_name: str):

    # async def add():

    # async def remove():

    # async def accept():

    # async def avatar():