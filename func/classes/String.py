# The following file contains: source, ginfo, grank, gmember, sync, info, dnkladd, dnklremove, dnkllist, dnklcheck

from __main__ import bot
import inspect
import os

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


    # async def dnklcheck():
