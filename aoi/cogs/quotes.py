import json
import random

from datetime import datetime as time
from aoi.utility import whitelisted_guilds

import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

# if database handler stored in a higher directory, this is required before import:
# sys.path.insert(1, os.path.realpath(os.path.pardir))

whitelisted = ["Grunthaner", "Queenan", "Mullarkey", "Garrity", "Babbin", "Roche", "Darby", "Mccabe", "Ellsworth", "Hanas", "Bartlett", "Gross", "Chupela", "Pannapara", "Madame", "Cava", "Lag", "Mannion", "Sohayda", "Bals"]
quote_file = "quotes.json"
quote_data = None

with open(quote_file) as quotes:
    quote_data = json.load(quotes)

class Quotes(commands.Cog, name="Quote Commands"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(base="quote",
                            subcommand_group="add",
                            name="user",
                            description="Create a quote for the provided user.",
                            guild_ids=whitelisted_guilds,
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
    async def create_quote_user(self, ctx, user: discord.Member, quote: str):
        await ctx.respond()

        timestamp = time.utcnow()
        embed = discord.Embed(title="",
                              description=f"\"{quote}\"",
                              timestamp=timestamp,
                              color=discord.Color.from_rgb(46, 204, 113))
        embed.set_author(name=user.name)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"Quoted by {ctx.author.name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

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
    
    @cog_ext.cog_subcommand(base="quote",
                            subcommand_group="get",
                            name="user",
                            description="Retrieve a random quote by the provided user.",
                            guild_ids=whitelisted_guilds,
                            options=[
                                create_option(
                                    name="user",
                                    description="the user in the server to quote",
                                    option_type=6,
                                    required=True
                                )
                            ])
    async def get_quote_user(self, ctx, user: discord.Member):
        await ctx.respond()

        quote_list = quote_data.get(str(user.id), False)
        if not quote_list:
            embed = discord.Embed(title="No Quotes",
                                  description=f"{user.mention} has no saved quotes.",
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
                              description=f"\"{quote['message']}\"",
                              timestamp=time.fromisoformat(quote["timestamp"]),
                              color=user.color)
        embed.set_author(name=user.name)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(
            text=f"{'Quo' if quoter.id == quote['by'] else 'Reques'}ted by {quoter.name}",
            icon_url=quoter.avatar_url
        )

        await ctx.send(embed=embed)
    
    @cog_ext.cog_subcommand(base="quote",
                            subcommand_group="add",
                            name="external",
                            description="Create a quote for the provided person.",
                            guild_ids=whitelisted_guilds,
                            options=[
                                create_option(
                                    name="name",
                                    description="the person's last name",
                                    option_type=3,
                                    required=True
                                ),
                                create_option(
                                    name="quote",
                                    description="the quote you are saving",
                                    option_type=3,
                                    required=True
                                )
                            ])
    async def create_quote_ext(self, ctx, name: str, quote: str):
        await ctx.respond()

        timestamp = time.utcnow()
        user = name.capitalize()

        if user not in whitelisted:
            embed = discord.Embed(title="Not Whitelisted",
                                  description=f"You may not quote {name}.",
                                  timestamp=timestamp,
                                  color=discord.Color.from_rgb(255, 74, 74))
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            return await ctx.send(embed=embed)
        
        embed = discord.Embed(title="",
                              description=f"\"{quote}\"",
                              timestamp=timestamp,
                              color=discord.Color.from_rgb(46, 204, 113))
        embed.set_author(name=user)
        embed.set_footer(text=f"Quoted by {ctx.author.name}", icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)

        current = quote_data.get(user, [])
        current.append({
            "timestamp": timestamp.isoformat(),
            "by": ctx.author.id,
            "message": quote
        })

        quote_data[user] = current
        with open(quote_file, "w") as quotes:
            json.dump(quote_data, quotes, indent=4, sort_keys=True)

    @cog_ext.cog_subcommand(base="quote",
                            subcommand_group="get",
                            name="external",
                            description="Retrieve a random quote by the provided person.",
                            guild_ids=whitelisted_guilds,
                            options=[
                                create_option(
                                    name="name",
                                    description="the last name of the user to retrieve a quote from",
                                    option_type=3,
                                    required=True
                                )
                            ])
    async def get_quote_ext(self, ctx, name: str):
        await ctx.respond()

        user = name.capitalize()
        quote_list = quote_data.get(user, False)

        if not quote_list:
            embed = discord.Embed(title="No Quotes",
                                  description=f"{user} has no saved quotes.",
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
                              description=f"\"{quote['message']}\"",
                              timestamp=time.fromisoformat(quote["timestamp"]),
                              color=discord.Color.random())
        embed.set_author(name=user)
        embed.set_footer(
            text=f"{'Quo' if quoter.id == quote['by'] else 'Reques'}ted by {quoter.name}",
            icon_url=quoter.avatar_url
        )

        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(base="quote",
                            name="whitelist",
                            description="View the whitelisted people you can quote.",
                            guild_ids=whitelisted_guilds)
    async def whitelist(self, ctx):
        await ctx.respond()

        await ctx.send("\n".join(whitelisted))


def setup(bot):
    bot.add_cog(Quotes(bot))
