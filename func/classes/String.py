# The following file contains: source, ginfo, grank, gmember, sync, info, dnkladd, dnklremove, dnkllist, dnklcheck

from __main__ import bot
import discord
import inspect
import os

from func.utils.requests.m_profile import m_profile
from func.utils.minecraft.get_player_gexp import get_player_gexp

from func.utils.consts import pos_color, neg_color

class String:
    def __init__(self, string: str):
        self.string = string

    # Command from https://github.com/Rapptz/RoboDanny
    async def source(self):
        """
        Displays the source code for the given command!
        """
        source_url = "https://github.com/MiscGuild/MiscBot"
        branch = "main"

        if self.string == None:
            return source_url

        if self.string == "help":
            src = type(bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = bot.get_command(self.string.replace(",", " "))
            if obj == None:
                return "Could not find command."

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            # not a built-in command
            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = "https://github.com/MiscGuild/MiscBot"
            branch = "main"

        final_url = f"<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        return f"Following is the source code for {self.string}\n{final_url}"


    # async def ginfo():

    
    # async def gexp():


    # async def grank(msg):


    # async def gmember():


    # async def sync(tag=None):


    # async def info():


    # async def dnkladd(start: str, end: str, *, reason: str):


    # async def dnklremove():


    # async def dnkllist():


    async def dnklcheck(self):
        _, weeklygexp = await get_player_gexp(self.string)

        # Player is not in a guild
        if weeklygexp == None:
            return discord.Embed(title="Guildless!", description="This player is not in a guild!", color=neg_color)

        _, uuid = await m_profile(self.string)
        # Player is eligible
        if weeklygexp > bot.dnkl:
            embed = discord.Embed(title=self.string, color=pos_color)
            embed.add_field(name="You are eligible to apply for the do-not-kick-list.",
                            value="You have {;,}/{:,} weekly guild experience.".format(weeklygexp, bot.dnkl),
                            inline=True)


        # Player is not eligible
        else:
            embed = discord.Embed(title=self.string, color=neg_color)
            print(format(bot.dnkl, ',d'))
            embed.add_field(name="You are not eligible to apply for the do-not-kick-list.",
                            value="You have {:,}/{:,} weekly guild experience to be eligible.".format(weeklygexp, bot.dnkl),
                            inline=True)

        embed.set_thumbnail(url=f"https://minotar.net/helm/{uuid}/512.png")
        embed.set_author(name="Do-not-kick-list: Eligibility Check")
        return embed
