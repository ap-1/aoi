import os, dotenv
from aoi.utility import is_owner

import discord
from discord.ext import commands

from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

dotenv.load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.all()
client = commands.Bot(command_prefix=commands.when_mentioned_or('/'), intents=intents)
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)

activity = discord.Activity(type=discord.ActivityType.listening, name="you")
guild_ids = [765588555010670654] #, 738965773531217972]

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=activity)
    print(f"{client.user.name} loaded.")

@slash.slash(name="load",
             description="Load a cog.",
             guild_ids=guild_ids,
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
        print(f"an error prevented {cog} from loading:\n{err}")
    else:
        await ctx.send(f"{name} has been loaded")

@slash.slash(name="unload",
             description="Unload a cog.",
             guild_ids=guild_ids,
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
    for cog in ["general", "owner"]:
        try:
            client.load_extension(f"aoi.cogs.{cog}")
        except commands.ExtensionFailed as err:
            print(f"an error prevented {cog} from loading:\n{err}")

    client.remove_command("help")
    client.run(token, reconnect=True)
