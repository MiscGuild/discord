# This command was used in conjuction with misc coin to reward players for completing challenges.

@commands.command()
@commands.has_role("Staff")
async def challenge(self, ctx, x):
    channel = self.bot.get_channel(753103243659444286)
    if x == "e":
        msg = await ctx.send(
            content="**What would you like the first challenge under the easy category to be (name)?**")
        challenge1 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge1 = challenge1.content

        await msg.edit(content="**What is the prize for completing this challenge?**")
        challenge1_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge1_prize = challenge1_prize.content

        await msg.edit(
            content="**What would you like the second challenge under the easy category to be?"
                    "\nIf you don't want one, type None**")
        challenge2 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge2 = challenge2.content
        if challenge2 == "None":
            embed = discord.Embed(title="Easy", color=0x90ee90)
            embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
        else:
            await msg.edit(content="What is the prize for completing this challenge?")
            challenge2_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2_prize = challenge2_prize.content

            embed = discord.Embed(title="Easy", color=0x90ee90)
            embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
        await channel.send(f'*Complete the following challenges to get prizes*\nTo view the store, use `!shop`')
        await channel.send(embed=embed)

    if x == "m":
        msg = await ctx.send("**What would you like the first challenge under the medium category to be (name)?**")
        challenge1 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge1 = challenge1.content

        await msg.edit(content="**What is the prize for completing this challenge?**")
        challenge1_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge1_prize = challenge1_prize.content

        await msg.edit(
            content="**What would you like the second challenge under the medium category to be?"
                    "\nIf you don't want one, type None**")
        challenge2 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge2 = challenge2.content
        if challenge2 == "None":
            embed = discord.Embed(title="Medium", color=0xffa500)
            embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
        else:
            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge2_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2_prize = challenge2_prize.content

            embed = discord.Embed(title="Medium", color=0xffa500)
            embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
        await channel.send(embed=embed)

    if x == "h":
        msg = await ctx.send("**What would you like the challenge under the hard category to be (name)?**")
        challenge1 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge1 = challenge1.content

        await msg.edit(content="**What is the prize for completing this challenge?**")
        challenge1_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge1_prize = challenge1_prize.content

        await msg.edit(
            content="**What would you like the second challenge under the hard category to be?"
                    "\nIf you don't want one, type None**")
        challenge2 = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
        challenge2 = challenge2.content
        if challenge2 == "None":
            embed = discord.Embed(title="Hard", color=0xcd5c5c)
            embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
        else:
            await msg.edit(content="**What is the prize for completing this challenge?**")
            challenge2_prize = await self.bot.wait_for('message', check=lambda x: x.author == ctx.message.author)
            challenge2_prize = challenge2_prize.content

            embed = discord.Embed(title="Hard", color=0xcd5c5c)
            embed.add_field(name=challenge1, value=challenge1_prize, inline=False)
            embed.add_field(name=challenge2, value=challenge2_prize, inline=False)
            embed.set_footer(text="You can only do one challenge once.")
        await channel.send(embed=embed)
