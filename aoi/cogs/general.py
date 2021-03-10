import discord
from discord.ext import commands

class General(commands.Cog, name="General Commands"):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	async def ping(self, ctx):
		""" Find the latency from the bot to discord. """

		await ctx.send(f"pong! ({self.bot.latency * 1000} ms)")

def setup(bot):
	bot.add_cog(General(bot))
