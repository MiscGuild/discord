# The following file contains: weeklylb, dnkllist

from __main__ import bot
import discord

from func.utils.minecraft_utils import get_hypixel_player_rank
from func.utils.request_utils import get_guild_by_name, get_name_by_uuid, get_hypixel_player, get_gtop
from func.utils.db_utils import select_all
from func.utils.consts import neg_color, neutral_color, invalid_guild_embed


class Func:
    async def weeklylb(ctx):
        async with ctx.channel.typing():
            # Get guild data
            guild_data = await get_guild_by_name(bot.guild_name)

            if guild_data == None:
                return invalid_guild_embed

            member_gexp = {}

            # Loop through all guild members' gexp, adding it to dict
            for member in guild_data["members"]:
                member_gexp[member["uuid"]] = sum(member["expHistory"].values())

            # Sort member gexp
            member_gexp = sorted(member_gexp.items(), key=lambda item: item[1], reverse=True)

            # Create url
            url = "&f&lWeekly Top&r%5Cn"
            for i in range(10):
                user_data = member_gexp[i]
                name = await get_name_by_uuid(user_data[0])
                rank, _ = await get_hypixel_player_rank(await get_hypixel_player(name))

                # Add new entry to image content
                url += f"&6{i + 1}. {rank} {name} &2{format(user_data[1], ',d')} Guild Experience"
                # Add new line
                if i < 9:
                    url +="%5Cn"

            # Replace characters for URL
            url = url.replace("+", "%2B")
            url = url.replace("&", "%26")
            url = url.replace(" ", "%20")
            url = url.replace(",", "%2C")

            # Return image
            return await get_gtop(f"https://chat.miscguild.xyz/render.png?m=custom&d={url}&t=1")

    async def dnkllist():
        # Fetch all rows
        rows = await select_all("SELECT * FROM dnkl")

        if not rows:
            return discord.Embed(title="No entries!", description="There are no users on the do-not-kick-list!", color=neg_color)

        # Create embed
        content = ""
        for _set in rows:
            _, _, username = _set
            content += f"{username}\n"

        return discord.Embed(title="The people on the do-not-kick-list are as follows:", description=content, color=neutral_color).set_footer(text=f"Total: {len(content.split())}")
