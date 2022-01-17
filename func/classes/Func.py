# The following file contains: weeklylb

from __main__ import bot

from func.utils.minecraft_utils import get_hypixel_player_rank
from func.utils.request_utils import get_guild_by_name, get_name_by_uuid, get_hypixel_player, get_gtop
from func.utils.consts import invalid_guild_embed


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