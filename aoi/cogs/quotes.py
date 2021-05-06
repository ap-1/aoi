import os
import sys
import json
import random

import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from datetime import datetime as time

# if database handler stored in a higher directory, this is required before import:
# sys.path.insert(1, os.path.realpath(os.path.pardir))

guild_ids = [765588555010670654, 738965773531217972]
quote_file = "quotes.json"
quote_data = None

with open(quote_file) as quotes:
    quote_data = json.load(quotes)

class Quotes(commands.Cog, name="Quote Commands"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="quote_user",
                       description="Create a quote for the given user.",
                       guild_ids=guild_ids,
                       options=[
                           create_option(
                               name="user",
                               description="the person you are quoting",
                               option_type=6,
                               required=True
                           ),
                           create_option(
                               name="quote",
                               description="the quote you are saving",
                               option_type=3,
                               required=True
                           )
                       ])
    async def quote_user(self, ctx, user: discord.Member, quote: str):
        await ctx.respond()

        timestamp = time.utcnow()
        user_id = str(user.id)

        current = quote_data.get(user_id, [])
        current.append({
            "timestamp": timestamp.isoformat(),
            "by": ctx.author.id,
            "message": quote
        })

        quote_data[user_id] = current
        with open(quote_file, "w") as quotes:
            json.dump(quote_data, quotes, indent=4, sort_keys=True)
        
        embed = discord.Embed(title="",
                              description=f"- {user.name}",
                              timestamp=timestamp,
                              color=discord.Color.from_rgb(46, 204, 113))
        embed.set_author(name=quote)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"Quoted by {ctx.author.name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
    
    @cog_ext.cog_slash(name="quote",
                       description="Retrieve a random quote by the given user.",
                       guild_ids=guild_ids,
                       options=[
                           create_option(
                               name="user",
                               description="the user to retrieve a quote from",
                               option_type=6,
                               required=True
                           )
                       ])
    async def quote(self, ctx, user: discord.Member):
        await ctx.respond()

        quote_list = quote_data.get(str(user.id), False)
        if not quote_list:
            embed = discord.Embed(title="No Quotes",
                                  description="The requested user does not have any saved quotes.",
                                  timestamp=time.utcnow(),
                                  color=discord.Color.from_rgb(255, 74, 74))
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)

        quote = random.choice(quote_list)
        quoter = None

        try:
            quoter = await ctx.guild.fetch_member(quote["by"])
        except:
            quoter = ctx.author

        embed = discord.Embed(title="",
                              description=f"- {user.name}",
                              timestamp=time.fromisoformat(quote["timestamp"]),
                              color=discord.Color.random())
        embed.set_author(name=quote["message"])
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(
            text=f"{'Quoted by ' if quoter.id == quote['by'] else ''}{quoter.name}",
            icon_url=quoter.avatar_url
        )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Quotes(bot))
