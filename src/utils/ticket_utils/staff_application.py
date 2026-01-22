from __main__ import bot

import discord

from src.utils.consts import NEUTRAL_COLOR, TICKET_CATEGORIES, NEG_COLOR, POSITIVE_RESPONSES, \
    STAFF_APPLICATION_QUESTIONS


async def staff_application(ticket: discord.TextChannel, interaction: discord.Interaction, user: discord.Member,
                            ign: str):
    # Edit category and send info embed with requirements
    await ticket.edit(name=f"staff-application-{ign}", topic=f"{interaction.user.id if interaction else user.id}|",
                      category=discord.utils.get((interaction.guild if interaction else ticket.guild).categories,
                                                 name=TICKET_CATEGORIES["generic"]))
    await ticket.send("**Staff Applications are currently CLOSED!**")
    return
    await ticket.send(embed=discord.Embed(title=f"{ign} wishes to apply for staff!",
                                          description="Please respond to the bot's prompts appropriately!",
                                          color=NEUTRAL_COLOR).add_field(
        name="Do you meet the following requirements? (y/n)",
        value="• You must be older than 13 years.\n"
              "• You must have sufficient knowledge of the bots in this Discord.\n"
              "• You must be active both on Hypixel and in the guild Discord.\n"
              "• You must have a good reputation amongst guild members.",
        inline=False))

    meets_requirements = await bot.wait_for("message", check=lambda
        x: x.channel == ticket and (x.author == interaction.user or x.author == user))

    # If user doesn't meet requirements, deny application
    if meets_requirements.content.lower() not in POSITIVE_RESPONSES:
        return await ticket.send(embed=discord.Embed(title="Your staff application has been denied!",
                                                     description="Since you do not meet the requirements, "
                                                                 "your staff application has been denied.",
                                                     color=NEG_COLOR))

    # Loop for all questions to gather info
    answers = {}
    for number, question in STAFF_APPLICATION_QUESTIONS.items():
        # Ask question and wait for answer
        await ticket.send(embed=discord.Embed(title=f"{number}. {question}",
                                              description="You must answer in one message.",
                                              color=NEUTRAL_COLOR))
        answer = await bot.wait_for("message",
                                    check=lambda
                                        x: x.channel == ticket and (x.author == interaction.user or x.author == user))

        # Place answer into array with question number
        answers[number] = answer.content

    # Send completion message
    await ticket.send(
        "Your staff application has been completed! Please wait while your answers are compiled.")

    # Create overview embed
    review_embed = discord.Embed(title=f"{ign}'s Staff Application", color=NEUTRAL_COLOR)
    review_embed.set_footer(text="If you made a mistake, please notify a staff member.")
    for number, answer in answers.items():
        review_embed.add_field(name=f"{number}. {STAFF_APPLICATION_QUESTIONS[number]}", value=answer,
                               inline=False)

    # Send embed
    message = await ticket.send(embed=review_embed)
    await ticket.edit(topic=f"{interaction.user.id if interaction else user.id}|{message.id}")
