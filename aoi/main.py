import os, dotenv

import discord
from discord.ext import commands

dotenv.load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents.all()
client = commands.Bot(command_prefix=commands.when_mentioned_or('-'), intents=intents)
activity = discord.Activity(activity=discord.ActivityType.listening, name="to you")

@client.command()
@commands.is_owner()
async def load(ctx, *, name: str):
	"""Load a cog."""

	try:
		client.load_extension(f"aoi.cogs.{name}")
	except commands.ExtensionNotFound:
		await ctx.send(f"{name} doesn't exist")
	except commands.ExtensionAlreadyLoaded:
		await ctx.send(f"{name} is already loaded")
	except commands.ExtensionFailed as err:
		print(f"an error prevented {cog} from loading:\n{err}")
	else:
		await ctx.send(f"{name} has been loaded.")

@client.command()
@commands.is_owner()
async def unload(ctx, *, name: str):
	"""Unload a cog."""

	try:
		client.unload_extension(f"aoi.cogs.{name}")
	except commands.ExtensionNotFound:
		await ctx.send(f"{name} doesn't exist")
	except commands.ExtensionNotLoaded:
		await ctx.send(f"{name} isn't loaded")
	else:
		await ctx.send(f"unloaded {name}")

@client.event
async def on_ready():
	await client.change_presence(status=discord.Status.dnd, activity=activity)
	print(f"{client.user.name} loaded.")

def init():
	for cog in ["general"]:
		try:
			client.load_extension(f"aoi.cogs.{cog}")
		except commands.ExtensionFailed as err:
			print(f"an error prevented {cog} from loading:\n{err}")

	client.run(token, reconnect=True)
