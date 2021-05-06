import discord

guild_ids = [765588555010670654, 738965773531217972]

def is_owner(func):
    async def check(*args): # COGS: self, ctx, *args || MAIN: ctx, *args
        ctx = args[1] if hasattr(args[1], "author") else args[0]

        if not await ctx.bot.is_owner(ctx.author):
            embed = discord.Embed(description="This command is owner-only.",
                                  color=discord.Color.from_rgb(255, 74, 74))
            embed.set_author(name="Error")
            return await ctx.send(embed=embed)

        return await func(*args)

    return check
