import discord
from discord.ext import commands

from datetime import datetime as time

no_mentions = discord.AllowedMentions.none()

def check_ping(client, message: discord.Message):
    if message.author == client:
        return False

    # check if message had mentions that weren't just the bot
    pinged_bot = len(message.mentions) == 1 and message.mentions[0] == client
    return len(message.mentions) > 0 and not pinged_bot

async def send_notification(message: discord.Message, mentions):
    mentions = mentions or message.mentions
    title = f"{message.author.name} has ghost pinged " + ", ".join(mention.name for mention in mentions)
    
    embed = discord.Embed(
        title=title,
        description=f"Message content: {message.content}",
        timestamp=time.utcnow()
    )
    embed.set_author(name="Ghost Ping")
    await message.channel.send(embed=embed, allowed_mentions=no_mentions)

class Ghost(commands.Cog, name="Ghost Ping Detection"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if check_ping(self.bot.user, message):
            await send_notification(message, False)

    @commands.Cog.listener()
    async def on_message_edit(self, previous: discord.Message, new: discord.Message):
        if not check_ping(self.bot.user, previous):
            return

        mentions = [member for member in previous.mentions if not member in new.mentions]
        if len(mentions) > 0:
            await send_notification(previous, mentions)
    

def setup(bot):
    bot.add_cog(Ghost(bot))
