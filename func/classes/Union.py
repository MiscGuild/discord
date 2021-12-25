# The following file contains: mute, unmute, kick, ban, softban, unban, forcesync, add, remove, accept, avatar

from __main__ import bot
import discord
from typing import Union
from discord.errors import Forbidden, NotFound

from discord.ext.commands.errors import MissingPermissions

from func.utils.consts import neg_color, neutral_color, err_404_embed, bot_missing_perms_embed

class Union:
    def __init__(self, user: Union[discord.Member, discord.User]):
        self.user = user

    async def mute(self, author, guild_roles, reason: str=None):
        # Default reason is responsible moderator
        if reason == None:
            reason == f"Responsible moderator: {author}"

        await self.user.add_roles(discord.utils.get(guild_roles, name="Muted"))
        return discord.Embed(title="Muted!", description=f"{self.user} was muted by {author}!", color=neg_color)


    async def unmute(self, guild_roles):
        await self.user.remove_roles(discord.utils.get(guild_roles, name="Muted"))
        embed = discord.Embed(title="Unmuted!",
                            description=f"{self.user} has been unmuted!",
                            color=neutral_color)
        return embed


    async def kick(self, author, reason: str=None):
        # Default reason is responsible moderator
        if reason == None:
            reason = f"Responsible moderator: {author}"

        await self.user.kick(reason=reason)
        return discord.Embed(title="Kicked!",
                            description=f"{self.user} was kicked by {author}",
                            color=neg_color)


    async def ban(self, guild, author, reason: str=None):
        # Default reason is responsible moderator
        if reason == None:
            reason = f"Responsible moderator: {author}"

        # Catch MissingPermissions error
        try:
            await guild.ban(self.user, reason=reason)
            return discord.Embed(title="Banned!",
                                description=f"{self.user} was banned by {author}",
                                color=neg_color)
        except Forbidden:
            return bot_missing_perms_embed


    async def softban(self, guild, author, reason: str=None):
        # Default reason is responsible moderator
        if reason == None:
            reason = f"Responsible moderator: {author}"

        # Catch MissingPermissions error
        try:
            await guild.ban(self.user, reason=reason)
            await guild.unban(self.user, reason=reason)
            return discord.Embed(title="Softbanned!",
                                description=f"{self.user} was softbanned by {author}",
                                color=neg_color)
        except Forbidden:
            return bot_missing_perms_embed


    async def unban(self, guild, author, reason: str=None):
        # Default reason is responsible moderator
        if reason == None:
            reason = f"Responsible moderator: {author}"

        # Catch Unkown Ban error
        try:
            await guild.unban(self.user, reason=reason)
            return discord.Embed(title="Unbanned!",
                                description=f"{self.user} was unbanned by {author}",
                                color=neg_color)
        except NotFound:
            return err_404_embed

    # async def forcesync(new_name: str):

    # async def add():

    # async def remove():

    # async def accept():

    async def avatar(self):
        embed = discord.Embed(title=f"{self.user}'s avatar:", color=neutral_color)
        return embed.set_image(url=self.user.avatar_url)