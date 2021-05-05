import os
import random
import asyncpraw

import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

reddit = asyncpraw.Reddit(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT")
)

guild_ids = [765588555010670654, 738965773531217972]
subreddits = {}

async def embed(submission, ctx):
    await submission.author.load()

    embed = discord.Embed(
        title=submission.title,
        color=random.randint(0, 0xffffff),
        url=f"https://reddit.com{submission.permalink}",
        description=submission.selftext
    )
    embed.set_image(url=submission.url)
    embed.set_author(
        name=submission.author.name,
        url=f"https://reddit.com/u/{submission.author.name}",
        icon_url=submission.author.icon_img
    )
    embed.set_thumbnail(url=submission.author.icon_img)
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    embed.add_field(
        name="Score",
        value=f"{submission.score} votes - {submission.upvote_ratio * 100}%"
    )
    
    if not submission.over_18:
        return embed

    notif = discord.Embed(title=f"{type(err).__name__}",
                            description="This post has been sent to you directly because it is " \
                                "marked NSFW.",
                            timestamp=ctx.message.created_at,
                            color=discord.Color.from_rgb(255, 74, 74))
    notif.set_author(name="NSFW")
    notif.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    await ctx.author.send(embed=embed)

    return notif

class Reddit(commands.Cog, name="Reddit Commands"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="post",
                    description="Get a random post from the specified subreddit.",
                    guild_ids=guild_ids,
                    options=[
                        create_option(
                            name="subreddit",
                            description="the subreddit to get a post from",
                            option_type=3,
                            required=True
                        )
                    ])
    async def post(self, ctx, subreddit: str):
        if not subreddits.get(subreddit, False):
            subreddits[subreddit] = await reddit.subreddit(subreddit)
        
        submission = await subreddits[subreddit].random()
        await ctx.send(embed=await embed(submission, ctx))

def setup(bot):
    bot.add_cog(Reddit(bot))
