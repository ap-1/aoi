import discord
from discord.ext import commands

from datetime import datetime as time

no_mentions = discord.AllowedMentions.none()

def check_ping(client, message: discord.Message):
    if len(message.mentions) < 1 or message.author == client:
        return False

    pinged_bot = message.mentions[0] == client
    pinged_self = message.mentions[0] == message.author
    single_mention = len(message.mentions) == 1

    return (len(message.mentions) > 0) and \
        not (single_mention and pinged_bot) and \
        not (single_mention and pinged_self)

async def send_notification(message: discord.Message, mentions):
    pings = [mention.name for mention in mentions or message.mentions]
    title = f"{', '.join(pings[:-1])}, and {pings[-1]}" if len(pings) > 2 \
        else f"{pings[0]}{f'and {pings[1]}' if len(pings) == 2 else ''}"

    embed = discord.Embed(
        title=f"{message.author.name} has ghost pinged {title}",
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

        mentions = [
            member for member in previous.mentions if \
                not member in new.mentions and \
                not member.bot
        ]

        if len(mentions) > 0:
            await send_notification(previous, mentions)


def setup(bot):
    bot.add_cog(Ghost(bot))
