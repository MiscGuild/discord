import discord

# Colors
neg_color = 0xff3333
pos_color = 0x00A86B
neutral_color = 0x8368ff


# General information
staff_impersonation_embed = discord.Embed(title="Staff impersonation is a punishable offense!", color=neg_color)
guildless_embed = discord.Embed(title="Guildless!", description="This player is not in a guild!", color=neg_color)
unknown_ign_embed = discord.Embed(title="Please enter a valid Minecraft username!", color=neg_color)
unknown_ign_msg = "Unkown IGN!"


# Errors
err_404_embed = discord.Embed(title="404 - Not Found", description="The bot encountered an error 404 while performing this action!", color=neg_color)
bot_missing_perms_embed = discord.Embed(title="Missing permissions!", description="Due to the role hierarchy, the bot does not have the permission to do that!", color=neg_color)
