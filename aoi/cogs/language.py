import aiohttp

from pyquery import PyQuery
from datetime import datetime as time
from aoi.utility import whitelisted_guilds

import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

SEARCH = "https://api.verbix.com/db/verbindex/9/{}"
DEFN = "https://api.verbix.com/translator/iv2/52ecc57c-4b90-11e7-ae0f-00089be4dcbc/lat/eng/{}"
HTML = "https://api.verbix.com/conjugator/iv1/ab8e7bb5-9ac6-11e7-ab6a-00089be4dcbc/1/9/109/{}"

conjugations = {
    "Present": 0,
    "Imperfect": 1,
    "Perfect": 3,
}

words = {
	"ego": 1,
	"tū": 3,
	"is": 5,
	"nōs": 7,
	"vōs": 9,
	"iī": 11,
}

def error_embed(embed, function):
    embed.add_field(name="Error", value=f"No {function.lower()} could be found for your input.")

    return embed

async def create_embed(ctx, word, function):
    async with aiohttp.ClientSession() as session:
        async with session.get(SEARCH.format(word.lower())) as response:
            result = await response.json()

            embed = discord.Embed(title=word,
                                timestamp=time.utcnow(),
                                color=discord.Color.random())
            embed.set_author(name=function)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            try:
                verb = result[0]
            except IndexError:
                await ctx.send(embed=error_embed(embed, function))
            else:
                return embed, verb

class Language(commands.Cog, name="Language Conjugator"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="define",
                    description="Search for a definition for the provided word.",
                    guild_ids=whitelisted_guilds,
                    options=[
                        create_option(
                            name="word",
                            description="the word to define",
                            option_type=3,
                            required=True
                        )
                    ])
    async def define(self, ctx, word: str):
        await ctx.respond()

        embed, verb = await create_embed(ctx, word, "Definitions")
        if not embed:
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(DEFN.format(verb["verb"])) as word_info:
                for index, definition in enumerate((await word_info.json())["p1"], start=1):
                    embed.add_field(
                        name=f"{index}: {definition['translation']}",
                        value=definition["meaning"]
                    )
                
                await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="conjugate",
                    description="Find the conjugations of the provided word.",
                    guild_ids=whitelisted_guilds,
                    options=[
                        create_option(
                            name="word",
                            description="the word to conjugate",
                            option_type=3,
                            required=True
                        )
                    ])
    async def conjugate(self, ctx, word: str):
        await ctx.respond()

        embed, verb = await create_embed(ctx, word, "Conjugations")
        if not embed:
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(HTML.format(verb["verb"])) as word_info:
                try:
                    pq = PyQuery((await word_info.json())["p1"]["html"])
                except:
                    await ctx.send(embed=error_embed(embed, "Conjugations"))
                else:
                    active = PyQuery(pq("h3:contains('Active')")[1]).nextAll()
                    groups = PyQuery(active[0]).find("h4:contains('Indicative')").parents("div")
                    tables = PyQuery(groups[-1]).children("table")

                    for tense in conjugations:
                        category = PyQuery(tables[conjugations[tense]]).find("tr > td > span")
                        results = [f"{word} {category[words[word]].text}" for word in words]
                        embed.add_field(name=tense, value="\n".join(results))
                    
                    await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Language(bot))
