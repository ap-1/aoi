import youtube_dl

from aoi.utility import whitelisted_guilds

import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

ytdl = youtube_dl.YoutubeDL({
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0"
})

class Player(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1.0):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop, stream=False):
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, options="-vn"), data=data)

class Voice(commands.Cog, name="Voice Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    async def play_next(self, ctx):
        guild = ctx.guild
        self.queue[guild].pop(0).source.cleanup()

        if not guild.voice_client:
            return await ctx.send("Stopped playing because the bot was disconnected.")

        if len(self.queue) > 0:
            player = self.queue[guild][0]

            ctx.guild.voice_client.play(player, after=lambda _: self.play_next(ctx))
            await ctx.send(f"Playing {player.title}")
        else:
            await ctx.send("Stopped playing because the queue is complete.")

    @cog_ext.cog_subcommand(base="voice",
                            name="play",
                            description="Play audio from a YouTube video.",
                            guild_ids=whitelisted_guilds,
                            options=[
                                create_option(
                                    name="url",
                                    description="the url of the video",
                                    option_type=3,
                                    required=True
                                ),
                                create_option(
                                    name="stream",
                                    description="whether the video is live or not",
                                    option_type=5,
                                    required=False
                                ),
                                create_option(
                                    name="now",
                                    description="whether to bypass the queue or not",
                                    option_type=5,
                                    required=False
                                )
                            ])
    async def play(self, ctx, url: str, stream: bool = False, now: bool = False):
        await ctx.respond()

        guild = ctx.guild
        if not guild.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("You must be connected to a voice channel.")

        player = await Player.from_url(url, loop=self.bot.loop, stream=stream)

        if not self.queue.get(guild, False):
            self.queue[guild] = []

        queue = self.queue[guild]
        size = len(queue)

        if size > 0:
            queue.append(player)
            await ctx.send(f"Position in queue: {size}")
        else:
            ctx.guild.voice_client.play(player, after=lambda _: self.play_next(ctx))
            await ctx.send(f"Playing {player.title}")

    @cog_ext.cog_subcommand(base="voice",
                            name="pause",
                            description="Pause the playing of audio.",
                            guild_ids=whitelisted_guilds)
    async def pause(self, ctx):
        await ctx.respond()

        client = ctx.guild.voice_client
        if not client:
            return await ctx.send("The bot is not connected to a voice channel.")
        
        if client.is_playing():
            client.pause()
        else:
            client.resume()

    @cog_ext.cog_subcommand(base="voice",
                            name="volume",
                            description="Adjust the volume of the bot.",
                            guild_ids=whitelisted_guilds,
                            options=[
                                create_option(
                                    name="number",
                                    description="the volume to change the bot to",
                                    option_type=4,
                                    required=True
                                )
                            ])
    async def volume(self, ctx, number: int):
        await ctx.respond()

        if not ctx.guild.voice_client:
            return await ctx.send("The bot is not connected to a voice channel.")
        
        ctx.guild.voice_client.source.volume = max(0.0, min(1.0, number / 100))
        await ctx.send(f"Adjusted volume to {number}")

    @cog_ext.cog_subcommand(base="voice",
                            name="stop",
                            description="Make the bot leave its voice channel.",
                            guild_ids=whitelisted_guilds)
    async def stop(self, ctx):
        await ctx.respond()

        await ctx.guild.voice_client.disconnect()
        await ctx.send("Disconnected from voice.")

def setup(bot):
    bot.add_cog(Voice(bot))
