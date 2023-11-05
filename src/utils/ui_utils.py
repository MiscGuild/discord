import calendar
from __main__ import bot
from datetime import datetime, timedelta

import discord
import discord.ui as ui

from src.utils.consts import (neg_color, neutral_color)


class StartYearSelect(ui.Select):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, weekly_gexp: int, buttons: tuple):
        super().__init__(placeholder="Year")
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.weekly_gexp = weekly_gexp
        self.buttons = buttons

        self.add_option(label=str(datetime.now().year))
        if datetime.now().month == 11:
            self.add_option(label=str(datetime.now().year + 1))

    # Override default callback
    async def callback(self, interaction: discord.Interaction):
        # Set option var and delete Select so it cannot be used twice

        start_year = list(interaction.data.values())[0][0]
        MonthView = discord.ui.View()
        MonthView.add_item(StartMonthSelect(channel=self.channel, ign=self.ign, uuid=self.uuid,
                                            year=start_year, weekly_gexp=self.weekly_gexp,
                                            buttons=self.buttons))  # Month Selection Dropdown
        embed = discord.Embed(title=f"In which month of {start_year} will {self.ign}'s inactivity begin?",
                              color=neutral_color).set_footer(text=f"Start Date - ?/?/{start_year}")
        await interaction.response.send_message(embed=embed, view=MonthView)
        self.view.stop()


class StartMonthSelect(ui.Select, object):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, year: int, weekly_gexp: int, buttons: tuple):
        super().__init__(placeholder="Month")
        self.channel = channel
        self.year = year
        self.ign = ign
        self.uuid = uuid
        self.weekly_gexp = weekly_gexp
        self.buttons = buttons

        for x in range(datetime.now().month, datetime.now().month + 2):
            if x > 12:
                x = x - 12
            self.add_option(label=str(calendar.month_name[x]))

    # Override default callback
    async def callback(self, interaction: discord.Interaction):
        # Set option var and delete Select so it cannot be used twice
        start_month = list(interaction.data.values())[0][0]

        DayView = discord.ui.View()
        DayView.add_item(StartDaySelect(channel=self.channel, ign=self.ign, uuid=self.uuid, month=start_month,
                                        year=self.year, weekly_gexp=self.weekly_gexp,
                                        buttons=self.buttons))  # Day Selection Dropdown

        embed = discord.Embed(title=f"What is the closest day to the start of {self.ign}'s inactivity?",
                              color=neutral_color).set_footer(text=f"Start Date - ?/{start_month}/{self.year}")
        await interaction.response.send_message(embed=embed, view=DayView)
        self.view.stop()


class StartDaySelect(ui.Select):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, month: str, year: int, weekly_gexp: int,
                 buttons: tuple):
        super().__init__(placeholder="Day")
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.month = month
        self.year = year
        self.weekly_gexp = weekly_gexp
        self.buttons = buttons

        month_number = datetime.strptime(self.month, "%B").month
        start_date = datetime.now().day if datetime.now().month == month_number else 1
        end_date = calendar.monthrange(int(self.year), month_number)[1] + 1
        number_of_days = end_date - start_date
        step = 1 if number_of_days < 26 else 2

        for day in range(start_date, end_date, step):
            self.add_option(label=str(day))

    # Override default callback
    async def callback(self, interaction: discord.Interaction):
        start_day = list(interaction.data.values())[0][0]
        LengthView = discord.ui.View()
        LengthView.add_item(
            InactivityLenSelect(author=interaction.user, channel=self.channel, ign=self.ign, uuid=self.uuid,
                                day=start_day, month=self.month, year=self.year, weekly_gexp=self.weekly_gexp,
                                buttons=self.buttons))
        embed = discord.Embed(title=f"How long will {self.ign} be inactive?",
                              color=neutral_color).set_footer(
            text=f"Start Date - {start_day}/{self.month}/{self.year}")
        await interaction.response.send_message(embed=embed, view=LengthView)
        self.view.stop()


class InactivityLenSelect(ui.Select):
    def __init__(self, author: discord.User, channel: discord.TextChannel, ign: str, uuid: str, day: int, month: str,
                 year: int, weekly_gexp: int, buttons: tuple):
        super().__init__(placeholder="Length")
        self.author = author
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.month = month
        self.year = year
        self.day = day
        self.weekly_gexp = weekly_gexp
        self.buttons = buttons
        self.deny = buttons[1][3]

        self.add_option(label=f"1 Week", value=str(1))
        for x in range(2, 4):
            self.add_option(label=f"{x} Weeks", value=str(x))
        self.add_option(label=f"More than {x} weeks", value='?')

    async def callback(self, interaction: discord.Interaction):
        length = list(interaction.data.values())[0][0]
        if length == "?":
            embed = discord.Embed(title=f"We do not accept do-not-kick-list applications for more than 3 weeks!",
                                  description="If you think you won't be able to meet the guild requirements during your inactivity period,"
                                              " you can leave the guild and notify staff once you're back. We'll invite you back!",
                                  color=neg_color)
            await interaction.response.send_message(embed=embed)
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
                              color=neutral_color)
        embed.set_footer(text=f"Start Date - {self.day}/{self.month}/{self.year}\n"
                              f"Length - {int(length) * 7} Days")
        await interaction.response.send_message(embed=embed, view=reason_view)
        self.view.stop()


class InactivityReasonSelect(ui.Select):
    def __init__(self, author: discord.User, channel: discord.TextChannel, ign: str, uuid: str, day: int, month: str,
                 year: int, length: int, weekly_gexp: int, buttons: tuple):
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

        reasons = ["Exams", "Medical Issues", "Vacation", "Computer Problems", "Other"]
        for reason in reasons:
            self.add_option(label=reason, value=reason)

    async def callback(self, interaction: discord.Interaction):
        reason = list(interaction.data.values())[0][0]

        other_reason = ""
        if reason == "Other":
            await interaction.response.send_message("Please elaborate on the reason for your inactivity.\n" \
                                                    "This information will only be visible to staff members.\n\n" \
                                                    "*Kindly type the reason as a single message.*")
            other_reason = await bot.wait_for("message", check=lambda
                x: x.channel == self.channel and x.author == self.author)
            other_reason = other_reason.content
            await self.channel.send("**Application submitted successfully!\nPlease await staff approval.**")
        else:
            await interaction.response.send_message(
                "**Application submitted successfully!\nPlease await staff approval.**")

        date = datetime.strptime(f"{self.day}/{self.month}/{self.year}", "%d/%B/%Y") + timedelta(weeks=int(self.length))
        final_embed = discord.Embed(title=self.ign, url=f'https://plancke.io/hypixel/player/stats/{self.ign}',
                                    color=neutral_color)
        final_embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{self.uuid}')
        final_embed.add_field(name="IGN:", value=self.ign, inline=False)
        final_embed.add_field(name="Start:", value=f"{self.day} {self.month} {self.year}", inline=False)
        final_embed.add_field(name="End:", value=f"{date.day} {date.strftime('%B')} {date.year}", inline=False)
        final_embed.add_field(name="Reason:", value=reason, inline=False)

        staff_approval_embed = final_embed.copy()
        staff_approval_embed.add_field(name="Guild Experience:",
                                       value=f"{format(self.weekly_gexp, ',d')} Weekly Guild Experience", inline=False)
        if other_reason:
            staff_approval_embed.set_footer(text="Other Elaboration: \n" + other_reason)

        DNKLView = discord.ui.View(timeout=None)  # View for staff members to approve/deny the DNKL
        buttons = [["Approve", "DNKL_Approve", discord.enums.ButtonStyle.green],
                   ["Deny", "DNKL_Deny", discord.enums.ButtonStyle.red],
                   ["Error", "DNKL_Error", discord.enums.ButtonStyle.gray]]
        # Loop through the list of roles and add a new button to the view for each role.
        for button in buttons:
            # Get the role from the guild by ID.
            DNKLView.add_item(
                Dnkl_Buttons(channel=self.channel, author=self.author, ign=self.ign, uuid=self.uuid, button=button,
                             embed=final_embed))

        await self.channel.send("**Staff**, what do you wish to do with this application?", embed=staff_approval_embed,
                                view=DNKLView)
        self.view.stop()


class Dnkl_Buttons(discord.ui.Button):
    def __init__(self, channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, button: list,
                 embed: discord.Embed):
        """
        3 buttons for 3 dnkl actions. `custom_id` is needed for persistent views.
        """
        self.embed = embed
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.author = author
        super().__init__(label=button[0], custom_id=button[1], style=button[2])

    async def callback(self, interaction: discord.Interaction):
        if bot.staff not in interaction.user.roles:
            await self.channel.send(embed=missing_permissions_embed)
            return
        # if bot.staff not in interaction.user.roles and ticket.id != interaction.channel_id: return
        elif interaction.custom_id == "DNKL_Approve":
            msg = await bot.get_channel(dnkl_channel_id).send(embed=self.embed)

            # Check if user is already on DNKL
            current_message = await select_one("SELECT message_id FROM dnkl WHERE uuid = (?)",
                                               (self.uuid,))
            # User is not currently on DNKL
            if not current_message:
                await insert_new_dnkl(msg.id, self.uuid, self.ign)
                return await interaction.response.send_message("**This user has been added to the do-not-kick-list!**")

            # User is already on DNKl
            # Try to delete current message
            try:
                current_message = await bot.get_channel(dnkl_channel_id).fetch_message(
                    current_message)
                await current_message.delete()
            except Exception:
                pass

            await update_dnkl(msg.id, self.uuid)
            await  interaction.response.send_message(
                "**Since this user was already on the do-not-kick-list, their entry has been updated.**")
        elif interaction.custom_id == "DNKL_Deny":
            await interaction.response.send_message("**This user's do-not-kick-list application has been denied!.**\n"
                                                    "If you didn't mean to hit deny, you can add them using `/dnkl_add`.",
                                                    ephemeral=True)

            denial_embed = discord.Embed(title="Your do-not-kick-list application has been denied!",
                                         description=f"You do not meet the DNKL requirements of {format(dnkl_req, ',d')} weekly guild experience.",
                                         color=neg_color)
            denial_embed.set_footer(
                text="If don't you think you can meet the requirements, you may rejoin the guild once your inactivity period has ended.")
            closeView = discord.ui.View(timeout=None)  # View for staff members to approve/deny the DNKL
            button = ("Close This Ticket", discord.enums.ButtonStyle.red)
            closeView.add_item(
                CloseDNKLTicket(channel=self.channel, author=self.author, ign=self.ign, uuid=self.uuid, button=button))
            await self.channel.send(embed=denial_embed, view=closeView)
            await delete_dnkl(self.ign)

        elif interaction.custom_id == "DNKL_Error":
            await interaction.response.send_message(embed=discord.Embed(
                title="Your application has been accepted, however there was an error!",
                description="Please await staff assistance!",
                color=neutral_color))
        self.view.stop()


class CloseDNKLTicket(discord.ui.Button):
    def __init__(self, channel: discord.TextChannel, author: discord.User, ign: str, uuid: str, button: list):
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.author = author

        super().__init__(label=button[0], style=button[1])

    async def callback(self, interaction: discord.Interaction):
        if self.author != interaction.user:
            await self.channel.send(embed=missing_permissions_embed)
            return

        embed = discord.Embed(title="This ticket will be deleted in 20 seconds!", color=neg_color)

        # Send deletion warning and gather transcript
        await interaction.response.send_message(embed=embed)
        transcript = await chat_exporter.export(self.channel, limit=None)
        if transcript:
            transcript = discord.File(BytesIO(transcript.encode()), filename=f"transcript-{self.channel.name}.html")
            await bot.get_channel(log_channel_id).send(
                f"DNKL Request was denied and channel was deleted by {self.author}")
            await bot.get_channel(log_channel_id).send(file=transcript)

        # Sleep and delete channel
        await asyncio.sleep(20)
        await discord.TextChannel.delete(self.channel)

        self.view.stop()


class ModalCreator(discord.ui.Modal):
    def __init__(self, embed: discord.Embed, fields: list, title: str, ign: str, uuid: str,function = None) -> None:
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

    async def callback(self, interaction: discord.Interaction):
        count = 0
        for field in self.fields:
            self.embed.add_field(name=field[3],
                                 value=self.children[count].value,
                                 inline=False)
            if self.function:
                await self.function(self.uuid, self.children[count].value)
            count += 1

        await interaction.response.send_message(embeds=[self.embed])

