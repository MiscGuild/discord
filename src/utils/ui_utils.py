import calendar
from __main__ import bot
from datetime import datetime, timedelta

import discord
import discord.ui as ui
from discord.ui import Button, View

from src.utils.consts import (NEG_COLOR, NEUTRAL_COLOR, TICKETS_MESSAGES)
from src.utils.db_utils import get_member_gexp_history
from src.utils.request_utils import get_jpg_file


class StartYearSelect(ui.Select):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, weekly_gexp: int, days_in_guild: int,
                 buttons: tuple) -> None:
        super().__init__(placeholder="Year")
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.weekly_gexp = weekly_gexp
        self.days_in_guild = days_in_guild
        self.buttons = buttons

        self.add_option(label=str(datetime.now().year))
        if datetime.now().month >= 11:
            self.add_option(label=str(datetime.now().year + 1))

    # Override default callback
    async def callback(self, interaction: discord.Interaction) -> None:
        # Set option var and delete Select so it cannot be used twice

        start_year = list(interaction.data.values())[0][0]
        MonthView = discord.ui.View()
        MonthView.add_item(StartMonthSelect(channel=self.channel, ign=self.ign, uuid=self.uuid,
                                            year=start_year, weekly_gexp=self.weekly_gexp,
                                            days_in_guild=self.days_in_guild,
                                            buttons=self.buttons))  # Month Selection Dropdown
        embed = discord.Embed(title=f"In which month of {start_year} will {self.ign}'s inactivity begin?",
                              color=NEUTRAL_COLOR).set_footer(text=f"Start Date - ?/?/{start_year}")
        await interaction.response.send_message(embed=embed, view=MonthView)
        self.view.stop()


class StartMonthSelect(ui.Select, object):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, year: int, weekly_gexp: int,
                 days_in_guild: int,
                 buttons: tuple) -> None:
        super().__init__(placeholder="Month")
        self.channel = channel
        self.year = year
        self.ign = ign
        self.uuid = uuid
        self.weekly_gexp = weekly_gexp
        self.days_in_guild = days_in_guild
        self.buttons = buttons

        for x in range(datetime.now().month, datetime.now().month + 2):
            if x > 12:
                x = x - 12
            self.add_option(label=str(calendar.month_name[x]))

    # Override default callback
    async def callback(self, interaction: discord.Interaction) -> None:
        # Set option var and delete Select so it cannot be used twice
        start_month = list(interaction.data.values())[0][0]

        DayView = discord.ui.View()
        DayView.add_item(StartDaySelect(channel=self.channel, ign=self.ign, uuid=self.uuid, month=start_month,
                                        year=self.year, weekly_gexp=self.weekly_gexp, days_in_guild=self.days_in_guild,
                                        buttons=self.buttons))  # Day Selection Dropdown

        embed = discord.Embed(title=f"What is the closest day to the start of {self.ign}'s inactivity?",
                              color=NEUTRAL_COLOR).set_footer(text=f"Start Date - ?/{start_month}/{self.year}")
        await interaction.response.send_message(embed=embed, view=DayView)
        self.view.stop()


class StartDaySelect(ui.Select):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, month: str, year: int, weekly_gexp: int,
                 days_in_guild: int,
                 buttons: tuple) -> None:
        super().__init__(placeholder="Day")
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.month = month
        self.year = year
        self.weekly_gexp = weekly_gexp
        self.days_in_guild = days_in_guild
        self.buttons = buttons

        month_number = datetime.strptime(self.month, "%B").month
        start_date = datetime.now().day if datetime.now().month == month_number else 1
        end_date = calendar.monthrange(int(self.year), month_number)[1] + 1
        number_of_days = end_date - start_date
        step = 1 if number_of_days < 26 else 2

        for day in range(start_date, end_date, step):
            self.add_option(label=str(day))

    # Override default callback
    async def callback(self, interaction: discord.Interaction) -> None:
        start_day = list(interaction.data.values())[0][0]
        LengthView = discord.ui.View()
        LengthView.add_item(
            InactivityLenSelect(author=interaction.user, channel=self.channel, ign=self.ign, uuid=self.uuid,
                                day=start_day, month=self.month, year=self.year, weekly_gexp=self.weekly_gexp,
                                days_in_guild=self.days_in_guild, buttons=self.buttons))
        embed = discord.Embed(title=f"How long will {self.ign} be inactive?",
                              color=NEUTRAL_COLOR).set_footer(
            text=f"Start Date - {start_day}/{self.month}/{self.year}")
        await interaction.response.send_message(embed=embed, view=LengthView)
        self.view.stop()


class InactivityLenSelect(ui.Select):
    def __init__(self, author: discord.User, channel: discord.TextChannel, ign: str, uuid: str, day: int, month: str,
                 year: int, weekly_gexp: int, days_in_guild: int, buttons: tuple) -> None:
        super().__init__(placeholder="Length")
        self.author = author
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.month = month
        self.year = year
        self.day = day
        self.weekly_gexp = weekly_gexp
        self.days_in_guild = days_in_guild
        self.buttons = buttons
        self.deny = buttons[1][3]

        for i in range(1, 8):
            self.add_option(label=f"{i} Day{'s' if i > 1 else ''}", value=str(i))

        for i in range(2, 4):
            self.add_option(label=f"{i} Week{'s' if i > 1 else ''}", value=str(i * 7))
        self.add_option(label="More than 3 weeks", value="?")

    async def callback(self, interaction: discord.Interaction) -> None:
        length = list(interaction.data.values())[0][0]
        if length == "?" and bot.staff not in interaction.user.roles:
            embed = discord.Embed(title=f"We do not accept do-not-kick-list applications that are longer than 3 weeks!",
                                  description="If you think you will be unable to meet the guild requirements during your inactivity period,"
                                              " you can leave the guild and notify staff once you're back. We'll gladly invite you back!",
                                  color=NEG_COLOR)
            await self.deny(channel=self.channel, author=self.author, ign=self.ign, uuid=self.uuid, embed=embed,
                            interaction=interaction, self_denial=True)

            await interaction.response.send_message("**If you missclicked, kindly create a new ticket!**\n"
                                                    "You will be punished if you lie and abuse the DNKL system.",
                                                    ephemeral=True)
            self.view.stop()
            return
        elif int(length) > 7 and self.days_in_guild < 30 and bot.staff not in interaction.user.roles:
            embed = discord.Embed(
                title=f"You cannot apply for a do-not-kick-list longer than 7 days since you joined the guild less than a month ago!",
                description="If you think you will be unable to meet the guild requirements during your inactivity period,"
                            " you can leave the guild and notify staff once you're back. We'll gladly invite you back!",
                color=NEG_COLOR)
            await self.deny(channel=self.channel, author=self.author, ign=self.ign, uuid=self.uuid, embed=embed,
                            interaction=interaction, self_denial=True)

            await interaction.response.send_message("**If you misclicked, kindly create a new ticket!**\n"
                                                    "You will be punished if you lie and abuse the DNKL system.",
                                                    ephemeral=True)
            self.view.stop()
            return

        reason_view = discord.ui.View()
        reason_view.add_item(InactivityReasonSelect(author=self.author,
                                                    channel=self.channel,
                                                    ign=self.ign,
                                                    uuid=self.uuid,
                                                    day=self.day,
                                                    month=self.month,
                                                    year=self.year,
                                                    length=length,
                                                    weekly_gexp=self.weekly_gexp,
                                                    buttons=self.buttons))

        embed = discord.Embed(title=f"What is the reason behind {self.ign}'s inactivity?",
                              color=NEUTRAL_COLOR)
        embed.set_footer(text=f"Start Date - {self.day}/{self.month}/{self.year}\n"
                              f"Length - {int(length)} Days")
        await interaction.response.send_message(embed=embed, view=reason_view)
        self.view.stop()


class InactivityReasonSelect(ui.Select):
    def __init__(self, author: discord.User, channel: discord.TextChannel, ign: str, uuid: str, day: int, month: str,
                 year: int, length: int, weekly_gexp: int, buttons: tuple) -> None:
        super().__init__(placeholder="Reason")
        self.author = author
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.month = month
        self.year = year
        self.day = day
        self.length = length
        self.weekly_gexp = weekly_gexp
        self.buttons = buttons

        reasons = ["Exams", "Medical Issues", "Vacation", "Computer Problems", "Banned on Hypixel", "Other"]
        for reason in reasons:
            self.add_option(label=reason, value=reason)

    async def callback(self, interaction: discord.Interaction) -> None:
        reason = list(interaction.data.values())[0][0]

        other_reason = ""

        if reason == "Banned on Hypixel":
            embed = discord.Embed(title="You cannot use the DNKL system if you are banned from the Hypixel!",
                                  description="If you are banned, you will be removed from the guild.\n"
                                              "You may rejoin once your ban is over.",
                                  color=NEG_COLOR)
            await interaction.response.send_message(embed=embed)
            return

        if reason == "Other":
            await interaction.response.send_message("Please elaborate on the reason for your inactivity.\n"
                                                    "This information will only be visible to staff members.\n\n"
                                                    "*Kindly type the reason as a single message.*")
            other_reason = await bot.wait_for("message", check=lambda
                x: x.channel == self.channel and x.author == self.author)
            other_reason = other_reason.content
            await self.channel.send("**Application submitted successfully!\nPlease await staff approval.**")
        else:
            await interaction.response.send_message(
                "**Application submitted successfully!\nPlease await staff approval.**")

        historical_gexp_data = await get_member_gexp_history(self.uuid)
        monthly_gexp = 0
        yearly_gexp = 0

        if historical_gexp_data:
            monthly_gexp = sum(
                dict(sorted(historical_gexp_data.items(), key=lambda x: x[0], reverse=True)).values())
            yearly_gexp = sum(historical_gexp_data.values())

        date = datetime.strptime(f"{self.day}/{self.month}/{self.year}", "%d/%B/%Y") + timedelta(days=int(self.length))
        final_embed = discord.Embed(title=self.ign, url=f'https://plancke.io/hypixel/player/stats/{self.ign}',
                                    color=NEUTRAL_COLOR)
        final_embed.set_thumbnail(url=f"https://visage.surgeplay.com/full/{self.uuid}.png")
        final_embed.add_field(name="IGN:", value=self.ign, inline=False)
        final_embed.add_field(name="Start:", value=f"{self.day} {self.month} {self.year}", inline=False)
        final_embed.add_field(name="End:", value=f"{date.day} {date.strftime('%B')} {date.year}", inline=False)
        final_embed.add_field(name="Reason:", value=reason, inline=False)
        final_embed.set_author(name="Do-not-kick-list")

        staff_approval_embed = final_embed.copy()

        staff_approval_embed.add_field(
            name="Guild Experience Summary:",
            value=f"```"
                  f"{'Category':<10} | {'GEXP':>12}\n"
                  f"{'-' * 25}\n"
                  f"{'Weekly':<10} | {format(self.weekly_gexp, ',d'):>12}\n"
                  f"{'Monthly':<10} | {format(monthly_gexp, ',d'):>12}\n"
                  f"{'Yearly':<10} | {format(yearly_gexp, ',d'):>12}\n"
                  f"```",
            inline=False
        )

        if other_reason:
            staff_approval_embed.set_footer(text="Other Elaboration: \n" + other_reason)

        DNKLView = discord.ui.View(timeout=None)  # View for staff members to approve/deny the DNKL

        # Loop through the list of roles and add a new button to the view for each role.
        for button in self.buttons:
            # Get the role from the guild by ID.
            DNKLView.add_item(
                Button_Creator(channel=self.channel, author=self.author, ign=self.ign, uuid=self.uuid, button=button,
                               embed=final_embed, function=button[3]))

        await self.channel.send("**Staff**, what do you wish to do with this application?", embed=staff_approval_embed,
                                view=DNKLView)
        self.view.stop()


class Button_Creator(discord.ui.Button):
    def __init__(self, channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, button: list,
                 embed: discord.Embed = None, function=None) -> None:
        # button = ["LABEL", "CUSTOM_ID", STYLE]
        self.embed = embed
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.author = author
        self.function = function

        super().__init__(label=button[0], custom_id=button[1], style=button[2])

    async def callback(self, interaction: discord.Interaction) -> None:
        meets_req = await self.function(channel=self.channel, author=self.author, ign=self.ign, uuid=self.uuid,
                                        embed=self.embed,
                                        interaction=interaction)
        if not meets_req:
            return
        self.view.stop()


class ModalCreator(discord.ui.Modal):
    def __init__(self, embed: discord.Embed, fields: list, title: str, ign: str, uuid: str, function=None) -> None:
        #   fields = ["LABEL", "PLACEHOLDER", STYLE]
        super().__init__(title=title)
        self.embed = embed
        self.ign = ign
        self.uuid = uuid
        self.fields = fields
        self.title = title
        self.function = function
        for field in fields:
            self.add_item(discord.ui.InputText(label=field[0],
                                               placeholder=field[1],
                                               style=field[2]))

    async def callback(self, interaction: discord.Interaction) -> None:
        count = 0
        for field in self.fields:
            self.embed.add_field(name=field[3],
                                 value=self.children[count].value,
                                 inline=False)
            if self.function:
                await self.function(self.uuid, self.children[count].value)
            count += 1

        await interaction.response.send_message(embeds=[self.embed])


async def tickets() -> tuple[discord.File, list, any]:
    image = await get_jpg_file(
        "https://media.discordapp.net/attachments/650248396480970782/873866686049189898/tickets.jpg")

    class TicketView(View):
        def __init__(self):
            super().__init__()
            self.add_item(Button(label="Create Ticket", custom_id="tickets",
                                 style=discord.ButtonStyle.blurple, emoji="✉️"))

    return image, TICKETS_MESSAGES, TicketView()
