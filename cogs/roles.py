import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption, InteractionType

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send(
            "<:sb:860044532963737601> __SkyBlock__\n*Gives you the access to the SkyBlock category!*\n\n<:minigames:860044554300031006> __Discord Minigames__\n*Allows you to play some Discord minigames!*\n\n👨‍👩‍👧‍👦 __SMP Server Access__\n*This role allows you to visit our SMP!*\n\n🎉 __Giveaways/Events__\n*React so you don't miss any giveaway or event*\n\n📖 __Storytimes__\n*Get pinged whenever a storytime happens* ",
            components=[
                [
                    Button(style=ButtonStyle.grey, label="Skyblock", emoji=self.bot.get_emoji(860044532963737601), id="860050068458307634"),
                    Button(style=ButtonStyle.grey, label="Discord Minigames", emoji=self.bot.get_emoji(860044554300031006), id="860050093872775179"),
                    Button(style=ButtonStyle.grey, label="SMP Server Access", emoji="👨‍👩‍👧‍👦", id="860050133226618901"),
                    Button(style=ButtonStyle.grey, label="Giveaways/Events", emoji="🎉", id="860050159429484585"),
                    Button(style=ButtonStyle.grey, label="Storytimes", emoji="📖", id="860050193482645504"),
                ]
            ],
        )
        await ctx.send(
            "Pronoun Roles:\n:black_large_square: He/Him\n:white_large_square: She/Her\n:white_circle: They/Them\n:grey_question: Other",
            components=[
                [
                    Select(placeholder="Select max 2!", options=[
                        SelectOption(label="He/Him", value="860050216854093854", emoji="⬛"),
                        SelectOption(label="She/Her", value="860050247027523584", emoji="⬜"),
                        SelectOption(label="They/Them", value="860050273862287390", emoji="⚪"),
                        SelectOption(label="Other", value="860050305168965643", emoji="❔")
                    ], max_values=2, min_values=1)
                ]
            ]
        )

    @commands.Cog.listener()
    async def on_button_click(self, res):
        role_ids = [860050068458307634,
        860050093872775179,
        860050133226618901,
        860050159429484585,
        860050193482645504]
        print(res.component.id)
        if int(res.component.id) in role_ids:
            guild = self.bot.get_guild(700419839092850698)
            member = guild.get_member(int(res.user.id))
            role = guild.get_role(int(res.component.id))
            if role in member.roles:
                await member.remove_roles(role, reason="Pressed Button, removed role")
                await res.respond(type=InteractionType.ChannelMessageWithSource, content=f"Removed {res.component.label} role from you.", flags=64)
            elif role not in member.roles:
                await member.add_roles(role, reason="Pressed Button, added role")
                await res.respond(type=InteractionType.ChannelMessageWithSource, content=f"Added {res.component.label} role from you.", flags=64)

    @commands.Cog.listener()
    async def on_select_option(self, res):
        role_ids = [860050216854093854,
        860050247027523584,
        860050273862287390,
        860050305168965643]
        if type(res.component) == list:
            guild = self.bot.get_guild(700419839092850698)
            member = guild.get_member(int(res.user.id))
            for role in res.component:
                if int(role.value) in role_ids:
                    print("yes")
        else:
            print('h')



def setup(bot):
    DiscordComponents(bot)
    bot.add_cog(Roles(bot))