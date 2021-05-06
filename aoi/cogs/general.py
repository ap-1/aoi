from aoi.utility import whitelisted_guilds

from discord.ext import commands
from discord_slash import cog_ext

class General(commands.Cog, name="General Commands"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="ping",
                       description="Find the latency from the bot to discord.",
                       guild_ids=whitelisted_guilds)
    async def ping(self, ctx):
        await ctx.respond()
        await ctx.send(f"pong! ({self.bot.latency * 1000} ms)")


def setup(bot):
    bot.add_cog(General(bot))
