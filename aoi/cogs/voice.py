import asyncio
import youtube_dl

from collections import deque
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

def after(coro, loop):
    future = asyncio.run_coroutine_threadsafe(coro, loop)

    try:
        future.result()
    except Exception as err:
        print(type(err).__name__, err)

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
        self.playing = {}

    @cog_ext.cog_slash(name="listen",
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
                           )
                       ])
    async def listen(self, ctx, url: str, stream: bool = False):
        guild = ctx.guild
        bot_loop = self.bot.loop

        if not guild.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                return await ctx.send("You must be connected to a voice channel.")

        player = await Player.from_url(url, loop=bot_loop, stream=stream)

        playing = self.playing.get(guild, None)
        if not playing:
            self.playing[guild] = False
            playing = False
        
        queue = self.queue.get(guild, None)
        if not queue:
            self.queue[guild] = deque([])
            queue = self.queue[guild]

        if len(queue) > 0 or playing:
            queue.append(player)

            items = "\n".join([f'- {player.title}' for player in queue])
            await ctx.send(f"Queued {player.title}\nPosition: {len(queue)}\n\n**Queue:**\n{items}")
        else:
            async def play_next():
                self.playing[guild] = False
                now_playing = None

                try:
                    now_playing = self.queue[guild].popleft()
                except:
                    return await ctx.send("Stopped playback because the queue is complete.")
                
                if not guild.voice_client:
                    return await ctx.send("Stopped playback because the bot was disconnected.")

                self.playing[guild] = now_playing

                await ctx.send(f"Playing {now_playing.title}")
                guild.voice_client.play(now_playing, after=lambda _: after(play_next(), bot_loop))

            queue.append(player)
            await play_next()

    @cog_ext.cog_slash(name="playing",
                       description="View the music that is currently playing.",
                       guild_ids=whitelisted_guilds)
    async def playing(self, ctx):
        guild = ctx.guild
        playing = self.playing.get(ctx.guild, None)

        if playing == None:
            self.playing[guild] = False
            playing = False
        
        await ctx.send(f"Now Playing: {playing}" if playing != False else "Nothing playing.")

    @cog_ext.cog_slash(name="queue",
                       description="View the music queue.",
                       guild_ids=whitelisted_guilds)
    async def queue(self, ctx):
        guild = ctx.guild
        queue = self.queue.get(guild, None)

        if not queue:
            self.queue[guild] = deque([])
            queue = False

        await ctx.send("\n".join([player.title for player in queue]) if queue else "Empty queue.")

    @cog_ext.cog_slash(name="pause",
                       description="Pause the music playback.",
                       guild_ids=whitelisted_guilds)
    async def pause(self, ctx):
        client = ctx.guild.voice_client
        
        if not client:
            return await ctx.send("The bot is not connected to a voice channel.")
        
        if client.is_playing():
            client.pause()
            await ctx.send("Paused playback.")
        else:
            client.resume()
            await ctx.send("Resumed playback.")

    @cog_ext.cog_slash(name="volume",
                       description="Adjust the volume of the bot.",
                       guild_ids=whitelisted_guilds,
                       options=[
                           create_option(
                               name="percentage",
                               description="the volume to change the bot to",
                               option_type=4,
                               required=True
                           )
                       ])
    async def volume(self, ctx, number: int):
        if not ctx.guild.voice_client:
            return await ctx.send("The bot is not connected to a voice channel.")

        ctx.guild.voice_client.source.volume = max(0.0, min(1.0, number / 100))
        await ctx.send(f"Adjusted volume to {number}%")

    @cog_ext.cog_slash(name="stop",
                       description="Make the bot leave its voice channel.",
                       guild_ids=whitelisted_guilds)
    async def stop(self, ctx):
        await ctx.respond()

        guild = ctx.guild
        client = guild.voice_client

        if client:
            client.stop()
            await client.disconnect()

        self.playing[guild] = False
        self.queue[guild] = deque([])

        await ctx.send("Disconnected from voice.")

def setup(bot):
    bot.add_cog(Voice(bot))
