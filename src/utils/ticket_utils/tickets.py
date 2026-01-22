from __main__ import bot
from asyncio import sleep
from io import BytesIO

import chat_exporter
import discord

from src.utils.consts import MISSING_PERMS_EMBED, NEG_COLOR, LOG_CHANNEL_ID


async def create_transcript(channel: discord.TextChannel, limit: int = None):
    transcript = await chat_exporter.export(channel, limit=limit)
    if not transcript:
        return None

    # Create and return file
    return discord.File(BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.html")


async def get_ticket_properties(channel: discord.TextChannel):
    topic = channel.topic
    if not topic or '|' not in topic:
        return None
    return topic.split('|')


async def close_ticket(channel: discord.TextChannel, author: discord.User, ign: str, uuid: str,
                       embed: discord.Embed, interaction: discord.Interaction):
    if author != interaction.user:
        await channel.send(embed=MISSING_PERMS_EMBED)
        return None

    embed = discord.Embed(title="This ticket will be deleted in 20 seconds!", color=NEG_COLOR)

    # Send deletion warning and gather transcript
    await interaction.response.send_message(embed=embed)
    transcript = await chat_exporter.export(channel, limit=None)
    if transcript:
        transcript = discord.File(BytesIO(transcript.encode()),
                                  filename=f"transcript-{channel.name}.html")
        await bot.get_channel(LOG_CHANNEL_ID).send(
            f"DNKL Request was denied and channel was deleted by {author}")
        await bot.get_channel(LOG_CHANNEL_ID).send(file=transcript)

    # Sleep and delete channel
    await sleep(20)
    await discord.TextChannel.delete(channel)


async def get_ticket_creator(channel: discord.TextChannel):
    return bot.guild.get_member(int(channel.topic.split("|")[0]))


async def name_grabber(author: discord.Member) -> str:
    if not author.nick:
        return author.name
    return author.nick.split()[0]
