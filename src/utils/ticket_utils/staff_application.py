from __main__ import bot

import discord

from src.utils.consts import POSITIVE_RESPONSES, \
    STAFF_APPLICATION_QUESTIONS

MESSAGE_LIMIT = 2000
SAFE_MESSAGE_LIMIT = 1900

RATING_EMOJIS = [
    "⬇️", "➖", "⬆️"
]


async def add_rating_reactions(message: discord.Message) -> None:
    """
    Adds 1-10 rating reactions to a message.
    Fails safely if the bot lacks reaction permissions.
    """
    for emoji in RATING_EMOJIS:
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            continue


def split_message(text: str, limit: int = SAFE_MESSAGE_LIMIT) -> list[str]:
    """
    Split a Markdown message into Discord-safe chunks.
    Prefers paragraph/newline/space boundaries before hard-splitting.
    """
    text = text.strip()
    chunks = []

    while len(text) > limit:
        split_at = text.rfind("\n\n", 0, limit)

        if split_at == -1:
            split_at = text.rfind("\n", 0, limit)

        if split_at == -1:
            split_at = text.rfind(" ", 0, limit)

        if split_at == -1:
            split_at = limit

        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()

    if text:
        chunks.append(text)

    return chunks


async def send_markdown_chunks(
        channel: discord.TextChannel,
        text: str,
        *,
        prefix_parts: bool = False,
        title: str = "Message",
) -> discord.Message:
    """
    Sends Markdown text safely, splitting into multiple Discord messages if needed.
    Returns the first sent message.
    """
    chunks = split_message(text)
    first_message = None

    for index, chunk in enumerate(chunks, start=1):
        if prefix_parts and len(chunks) > 1:
            chunk = f"**{title} — Part {index}/{len(chunks)}**\n\n{chunk}"

        message = await channel.send(
            chunk,
            allowed_mentions=discord.AllowedMentions.none(),
        )

        if first_message is None:
            first_message = message

    return first_message


async def staff_application(
        ticket: discord.TextChannel,
        interaction: discord.Interaction,
        user: discord.Member,
        ign: str,
):
    await ticket.edit(name=f"staff-application-{ign}")

    requirements_message = (
        f"# {ign} wishes to apply for staff!\n\n"
        "Please respond to the bot's prompts appropriately.\n\n"
        "## Do you meet the following requirements? `(y/n)`\n\n"
        "• You must be older than 13 years.\n"
        "• You must have sufficient knowledge of the bots in this Discord.\n"
        "• You must be active both on Hypixel and in the guild Discord.\n"
        "• You must have a good reputation amongst guild members."
    )

    await ticket.send(
        requirements_message,
        allowed_mentions=discord.AllowedMentions.none(),
    )

    meets_requirements = await bot.wait_for(
        "message",
        check=lambda x: (
                x.channel == ticket
                and (x.author == interaction.user or x.author == user)
        ),
    )

    if meets_requirements.content.lower() not in POSITIVE_RESPONSES:
        return await ticket.send(
            "# Your staff application has been denied.\n\n"
            "Since you do not meet the requirements, your staff application has been denied.",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    answers = {}

    for number, question in STAFF_APPLICATION_QUESTIONS.items():
        question_message = (
            f"## {number}. {question}\n\n"
            "You must answer in one message."
        )

        await ticket.send(
            question_message,
            allowed_mentions=discord.AllowedMentions.none(),
        )

        answer = await bot.wait_for(
            "message",
            check=lambda x: (
                    x.channel == ticket
                    and (x.author == interaction.user or x.author == user)
            ),
        )

        answers[number] = answer.content

    await ticket.send(
        "Your staff application has been completed! Please wait while your answers are compiled.",
        allowed_mentions=discord.AllowedMentions.none(),
    )

    header_message = await ticket.send(
        f"# {ign}'s Staff Application\n\n"
        "_If you made a mistake, please notify a staff member._",
        allowed_mentions=discord.AllowedMentions.none(),
    )

    first_review_message = None

    for number, answer in answers.items():
        question = STAFF_APPLICATION_QUESTIONS[number]
        clean_answer = answer.strip() or "*No answer provided.*"

        review_markdown = (
            f"## {number}. {question}\n\n"
            f"{clean_answer}"
        )

        message = await send_markdown_chunks(
            ticket,
            review_markdown,
            prefix_parts=True,
            title=f"Question {number}",
        )

        if first_review_message is None:
            first_review_message = message

        await add_rating_reactions(message)

    await ticket.send(
        "---\n"
        "**Staff team:** Please rate each application answer message using the reactions above.",
        allowed_mentions=discord.AllowedMentions.none(),
    )

    topic_message = first_review_message or header_message

    await ticket.edit(
        topic=f"{interaction.user.id if interaction else user.id}|{topic_message.id}"
    )
