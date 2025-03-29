from __main__ import bot

import discord

from src.utils.consts import neutral_color, ticket_categories, neg_color, positive_responses, \
    staff_application_questions


async def staff_application(ticket: discord.TextChannel, interaction: discord.Interaction, ign: str):
    # Edit category and send info embed with requirements
    await ticket.edit(name=f"staff-application-{ign}", topic=f"{interaction.user.id}|",
                      category=discord.utils.get(interaction.guild.categories,
                                                 name=ticket_categories["generic"]))
    await ticket.send(embed=discord.Embed(title=f"{ign} wishes to apply for staff!",
                                          description="Please respond to the bot's prompts appropriately!",
                                          color=neutral_color).add_field(
        name="Do you meet the following requirements? (y/n)",
        value="• You must be older than 13 years.\n"
              "• You must have sufficient knowledge of the bots in this Discord.\n"
              "• You must be active both on Hypixel and in the guild Discord.\n"
              "• You must have a good reputation amongst guild members.",
        inline=False))

    meets_requirements = await bot.wait_for("message", check=lambda
        x: x.channel == ticket and x.author == interaction.user)

    # If user doesn't meet requirements, deny application
    if meets_requirements.content.lower() not in positive_responses:
        return await ticket.send(embed=discord.Embed(title="Your staff application has been denied!",
                                                     description="Since you do not meet the requirements, "
                                                                 "your staff application has been denied.",
                                                     color=neg_color))

    # Loop for all questions to gather info
    answers = {}
    for number, question in staff_application_questions.items():
        # Ask question and wait for answer
        await ticket.send(embed=discord.Embed(title=f"{number}. {question}",
                                              description="You must answer in one message.",
                                              color=neutral_color))
        answer = await bot.wait_for("message",
                                    check=lambda
                                        x: x.channel == ticket and x.author == interaction.user)

        # Place answer into array with question number
        answers[number] = answer.content

    # Send completion message
    await ticket.send(
        "Your staff application has been completed! Please wait while your answers are compiled.")

    # Create overview embed
    review_embed = discord.Embed(title=f"{ign}'s Staff Application", color=neutral_color)
    review_embed.set_footer(text="If you made a mistake, please notify a staff member.")
    for number, answer in answers.items():
        review_embed.add_field(name=f"{number}. {staff_application_questions[number]}", value=answer,
                               inline=False)

    # Send embed
    message = await ticket.send(embed=review_embed)
    await ticket.edit(topic=f"{interaction.user.id}|{message.id}")
