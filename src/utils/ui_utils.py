from __main__ import bot
from datetime import datetime, timedelta

import discord
import discord.ui as ui

from src.utils.consts import (dnkl_channel_id, dnkl_req,
                              missing_permissions_embed,
                              neg_color, neutral_color)
from src.utils.db_utils import insert_new_dnkl, select_one, update_dnkl, delete_dnkl


class StartYearSelect(ui.Select):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str):
        super().__init__(placeholder="Year")
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.add_option(label=str(datetime.now().year))
        self.add_option(label=str(datetime.now().year + 1))

    # Override default callback
    async def callback(self, interaction: discord.Interaction):
        # Set option var and delete Select so it cannot be used twice

        start_year = list(interaction.data.values())[0][0]
        MonthView = discord.ui.View()
        MonthView.add_item(StartMonthSelect(channel=self.channel, ign=self.ign, uuid=self.uuid,
                                            year=start_year))  # Month Selection Dropdown
        embed = discord.Embed(title=f"In which month of {start_year} will {self.ign}'s inactivity begin?",
                              color=neutral_color).set_footer(text=f"Start Date - ?/?/{start_year}")
        await interaction.response.send_message(embed=embed, view=MonthView)
        self.view.stop()


class StartMonthSelect(ui.Select, object):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, year):
        super().__init__(placeholder="Month")
        self.channel = channel
        self.year = year
        self.ign = ign
        self.uuid = uuid
        import calendar
        for x in range(1, 13):
            self.add_option(label=str(calendar.month_name[x]))

    # Override default callback
    async def callback(self, interaction: discord.Interaction):
        # Set option var and delete Select so it cannot be used twice
        start_month = list(interaction.data.values())[0][0]
        DayView = discord.ui.View()

        DayView.add_item(StartDaySelect(channel=self.channel, ign=self.ign, uuid=self.uuid, month=start_month,
                                        year=self.year))  # Day Selection Dropdown
        embed = discord.Embed(title=f"What is the closest day to the start of {self.ign}'s inactivity?",
                              color=neutral_color).set_footer(text=f"Start Date - ?/{start_month}/{self.year}")
        await interaction.response.send_message(embed=embed, view=DayView)
        self.view.stop()


class StartDaySelect(ui.Select):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, month, year):
        super().__init__(placeholder="Day")
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.month = month
        self.year = year
        for x in range(1, 32, 2):
            self.add_option(label=str(x))

    # Override default callback
    async def callback(self, interaction: discord.Interaction):
        start_day = list(interaction.data.values())[0][0]
        LengthView = discord.ui.View()
        LengthView.add_item(
            InactivityLenSelect(author=interaction.user, channel=self.channel, ign=self.ign, uuid=self.uuid,
                                day=start_day, month=self.month, year=self.year))  # Length Selection Dropdown
        embed = discord.Embed(title=f"How long will {self.ign} be inactive?",
                              color=neutral_color).set_footer(
            text=f"Start Date - {start_day}/{self.month}/{self.year}")
        await interaction.response.send_message(embed=embed, view=LengthView)
        self.view.stop()


class InactivityLenSelect(ui.Select):
    def __init__(self, author: discord.User, channel: discord.TextChannel, ign: str, uuid: str, day, month, year):
        super().__init__(placeholder="Length")
        self.author = author
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
        self.month = month
        self.year = year
        self.day = day

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
        await interaction.response.send_message(
            embed=discord.Embed(title=f"What is the reason behind {self.ign}'s inactivity?",
                                description="Kindly type the reason as a single message",
                                color=neutral_color).set_footer(
                text=f"Start Date - {self.day}/{self.month}/{self.year}\n"
                     f"Length - {int(length) * 7} Days"))
        reason = await bot.wait_for("message", check=lambda
            x: x.channel == self.channel and x.author == self.author)  # getting the reason
        reason = reason.content
        date = datetime.strptime(f"{self.day}/{self.month}/{self.year}", "%d/%B/%Y") + timedelta(weeks=int(length))
        embed = discord.Embed(title=self.ign, url=f'https://plancke.io/hypixel/player/stats/{self.ign}',
                              color=neutral_color)
        embed.set_thumbnail(url=f'https://crafatar.com/renders/body/{self.uuid}')
        embed.add_field(name="IGN:", value=self.ign, inline=False)
        embed.add_field(name="Start:", value=f"{self.day} {self.month} {self.year}", inline=False)
        embed.add_field(name="End:", value=f"{date.day} {date.strftime('%B')} {date.year}", inline=False)
        embed.add_field(name="Reason:", value=reason, inline=False)

        DNKLView = discord.ui.View(timeout=None)  # View for staff members to approve/deny the DNKL
        buttons = [["Approve", "DNKL_Approve", discord.enums.ButtonStyle.green],
                   ["Deny", "DNKL_Deny", discord.enums.ButtonStyle.red],
                   ["Error", "DNKL_Error", discord.enums.ButtonStyle.gray]]
        # Loop through the list of roles and add a new button to the view for each role.
        for button in buttons:
            # Get the role from the guild by ID.
            DNKLView.add_item(
                Dnkl_Buttons(channel=self.channel, ign=self.ign, uuid=self.uuid, button=button, embed=embed))

        await self.channel.send("Staff, what do you wish to do with this application?", embed=embed, view=DNKLView)
        self.view.stop()


class Dnkl_Buttons(discord.ui.Button):
    def __init__(self, channel: discord.TextChannel, ign: str, uuid: str, button: list, embed: discord.Embed):
        """
        3 buttons for 3 dnkl actions. `custom_id` is needed for persistent views.
        """
        self.embed = embed
        self.channel = channel
        self.ign = ign
        self.uuid = uuid
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
                return await self.channel.send("**This user has been added to the do-not-kick-list!**")

            # User is already on DNKl
            # Try to delete current message
            try:
                current_message = await bot.get_channel(dnkl_channel_id).fetch_message(
                    current_message)
                await current_message.delete()
            except Exception:
                pass

            await update_dnkl(msg.id, self.uuid)
            await self.channel.send(
                "**Since this user was already on the do-not-kick-list, their entry has been updated.**")
        elif interaction.custom_id == "DNKL_Deny":
            await self.channel.send(
                embed=discord.Embed(title="Your do-not-kick-list application has been denied!",
                                    description=f"You do not meet the DNKL requirements of {format(dnkl_req, ',d')} weekly guild experience.",
                                    color=neg_color).set_footer(
                    text="If don't you think you can meet the requirements, you may rejoin the guild once your inactivity period has finished."))
            await delete_dnkl(self.ign)
            await interaction.response.send_message(
                "If you wish to reverse your decision, add them to the DNKL using `,dnkladd`",
                ephemeral=True)
        elif interaction.custom_id == "DNKL_Error":
            await self.channel.send(embed=discord.Embed(
                title="Your application has been accepted, however there was an error!",
                description="Please await staff assistance!",
                color=neutral_color))
        self.view.stop()


class GvGButtons(discord.ui.Button):
    def __init__(self, channel: discord.TextChannel,member: discord.Member, ign: str, button: list):
        super().__init__(label=button[0], custom_id=button[1], style=button[2])
        self.channel = channel
        self.member = member
        self.ign = ign

    async def callback(self, interaction: discord.Interaction):
        if bot.staff not in interaction.user.roles:
            await self.channel.send(embed=missing_permissions_embed)
            return
        # if bot.staff not in interaction.user.roles and ticket.id != interaction.channel_id: return
        elif interaction.custom_id == "GvG_Approve":
            await self.member.add_roles(bot.gvg)
            print(self.channel, self.channel.name)
            await self.channel.send(embed=discord.Embed(title=f"Welcome to the GvG team, {self.ign}!",
                                color=neutral_color))
        elif interaction.custom_id == "GvG_Deny":
            await self.channel.send(embed=discord.Embed(title=f"Your GvG Application was denied because you didn't meet the requirements",
                                                        color=neg_color))

        self.view.stop()

class ModalCreator(discord.ui.Modal):
    def __init__(self,embed: discord.Embed, fields: list, title: str, ign: str) -> None:
        #   fields = ["LABEL", "PLACEHOLDER", STYLE]
        super().__init__(title=title)
        self.embed = embed
        self.ign = ign
        self.fields = fields
        self.title = title
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
            count+=1


        await interaction.response.send_message(embeds=[self.embed])