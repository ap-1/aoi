import ast

from datetime import datetime as time
from aoi.utility import is_owner, whitelisted_guilds

import discord
from discord.ext import commands
from discord.utils import escape_markdown

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

replacements = str.maketrans({
    '‘': "'",
    '’': "'",
    '“': "\"",
    '”': "\"",
})

def insert_returns(body):
	if isinstance(body[-1], ast.Expr):
		body[-1] = ast.Return(body[-1].value)
		ast.fix_missing_locations(body[-1])

	if isinstance(body[-1], ast.If):
		insert_returns(body[-1].body)
		insert_returns(body[-1].orelse)

	if isinstance(body[-1], (ast.With, ast.AsyncWith)):
		insert_returns(body[-1].body)

def format_body(code: str):
    return code.translate(replacements).splitlines()

class Owner(commands.Cog, name="Owner Commands"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="eval",
                       description="Execute arbitrary python code in an environment similar to that of a command.",
                       guild_ids=whitelisted_guilds,
                       options=[
                           create_option(
                               name="code",
                               description="the code to be executed",
                               option_type=3,
                               required=True
                           )
                       ])
    @is_owner
    async def _eval(self, ctx, code: str):    
        await ctx.respond()

        closure = "_aoi_eval"
        code = "\n".join(f"\t{line}" for line in format_body(code))
        environment = {
            # bot
            "ctx": ctx,
            "bot": self.bot,
            "client": self.bot,

            # utility
            "discord": discord,
            "commands": commands,
            "__name__": __name__,
            "__file__": __file__,
            "__import__": __import__,

            # shorthands
            "guild": ctx.guild,
            "author": ctx.author,
            "channel": ctx.channel,
        }

        try:
            parsed = ast.parse(f"async def {closure}():\n{code}")
            insert_returns(parsed.body[0].body)
            await ctx.send(f"```py\n{ast.unparse(parsed)}\n\nawait {closure}()\n```")

            exec(compile(parsed, filename="<eval>", mode="exec"), environment)
            result = await eval(f"{closure}()", environment)

            if result is not None and result != "":
                await ctx.send(result)
        except Exception as err:
            embed = discord.Embed(title=f"{type(err).__name__}",
                                  description=f"{err}",
                                  timestamp=time.utcnow(),
                                  color=discord.Color.from_rgb(255, 74, 74))
            embed.set_author(name="Evaluation Failure")
            embed.set_footer(text=ctx.author.name)

            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="environment",
                       description="View the environment used in the eval command.",
                       guild_ids=whitelisted_guilds,
                       options=[])
    @is_owner
    async def environment(self, ctx):
        await ctx.respond()

        environment = {
            # bot
            "ctx": ctx,
            "bot": self.bot,
            "client": self.bot,

            # utility
            "discord": discord,
            "commands": commands,
            "__name__": __name__,
            "__import__": __import__,

            # shorthands
            "guild": ctx.guild,
            "author": ctx.author,
            "channel": ctx.channel,
        }

        message = "\n".join([f"- {var}: {environment[var]}" for var in environment])
        await ctx.send(escape_markdown(message))


def setup(bot):
    bot.add_cog(Owner(bot))
