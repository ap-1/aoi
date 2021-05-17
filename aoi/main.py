import os
import dotenv

from aoi.utility import is_owner, whitelisted_guilds

import discord
from discord.ext import commands

from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

dotenv.load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.all()
activity = discord.Activity(type=discord.ActivityType.listening, name="you")

client = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)

async def check_undeletable(messages):
    for message in messages:
        if len(message.embeds) != 1 or message.embeds[0].author.name != "Ghost Ping":
            continue
        
        await message.channel.send(embed=message.embeds[0])

@client.event
async def on_message_delete(message):
    await check_undeletable([ message ])

@client.event
async def on_bulk_message_delete(messages):
    await check_undeletable(messages)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=activity)
    print(f"{client.user.name} loaded.")

@slash.slash(name="load",
             description="Load a cog.",
             guild_ids=whitelisted_guilds,
             options=[
                 create_option(
                     name="cog",
                     description="the cog to load",
                     option_type=3,
                     required=True
                 )
             ])
@is_owner
async def load(ctx, name: str):
    await ctx.respond()

    try:
        client.load_extension(f"aoi.cogs.{name}")
    except commands.ExtensionNotFound:
        await ctx.send(f"{name} doesn't exist")
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f"{name} is already loaded")
    except commands.ExtensionFailed as err:
        print(f"an error prevented {name} from loading:\n{err}")
    else:
        await ctx.send(f"{name} has been loaded")

@slash.slash(name="unload",
             description="Unload a cog.",
             guild_ids=whitelisted_guilds,
             options=[
                 create_option(
                     name="cog",
                     description="the cog to unload",
                     option_type=3,
                     required=True
                 )
             ])
@is_owner
async def unload(ctx, name: str):
    await ctx.respond()

    try:
        client.unload_extension(f"aoi.cogs.{name}")
    except commands.ExtensionNotFound:
        await ctx.send(f"{name} doesn't exist")
    except commands.ExtensionNotLoaded:
        await ctx.send(f"{name} isn't loaded")
    else:
        await ctx.send(f"unloaded {name}")

def init():
    for cog in ["general", "owner", "reddit", "quotes", "ghost", "voice", "language"]:
        try:
            client.load_extension(f"aoi.cogs.{cog}")
        except commands.ExtensionFailed as err:
            print(f"an error prevented {cog} from loading:\n{err}")

    client.remove_command("help")
    client.run(token, reconnect=True)
