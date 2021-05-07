import random
import aiohttp

from datetime import datetime as time
from aoi.utility import whitelisted_guilds

import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

class General(commands.Cog, name="General Commands"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping",
                    description="Find the latency from the bot to discord.",
                    guild_ids=whitelisted_guilds)
    async def ping(self, ctx):
        await ctx.respond()
        await ctx.send(f"pong! ({self.bot.latency * 1000} ms)")
    
    @cog_ext.cog_slash(name="numberfact",
                    description="Get a random fact for the provided number.",
                    guild_ids=whitelisted_guilds,
                    options=[
                        create_option(
                            name="number",
                            description="the number to get a fact for",
                            option_type=4,
                            required=True
                        )
                    ])
    async def numberfact(self, ctx, number: int):
        await ctx.respond()

        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://numbersapi.com/{number}") as response:
                embed = discord.Embed(title="Number Fact",
                                    description=await response.text(),
                                    timestamp=time.utcnow(),
                                    color=discord.Color.random())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="8ball",
                       description="Ask the magic 8ball a question.",
                       guild_ids=whitelisted_guilds,
                       options=[
                           create_option(
                               name="query",
                               description="what you are asking the 8ball",
                               option_type=3,
                               required=True
                           )
                       ])
    async def _8ball(self, ctx, query: str):
        await ctx.respond()
        
        embed = discord.Embed(title="",
                              description=random.choice([
                                  "It is certain",
                                  "Without a doubt",
                                  "You may rely on it",
                                  "Yes definitely",
                                  "It is decidedly so",
                                  "As I see it, yes",
                                  "Most likely",
                                  "Yes",
                                  "Outlook good",
                                  "Signs point to yes",
                                  "Reply hazy try again",
                                  "Better not tell you now",
                                  "Ask again later",
                                  "Cannot predict now",
                                  "Concentrate and ask again",
                                  "Don't count on it",
                                  "Outlook not so good",
                                  "My sources say no",
                                  "Very doubtful",
                                  "My reply is no",
                              ]),
                              timestamp=time.utcnow(),
                              color=discord.Color.random())
        embed.set_author(name=query)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
