import ast

import discord
from discord.ext import commands

from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

guild_ids = [765588555010670654]

def insert_returns(body):
	if isinstance(body[-1], ast.Expr):
		body[-1] = ast.Return(body[-1].value)
		ast.fix_missing_locations(body[-1])

	if isinstance(body[-1], ast.If):
		insert_returns(body[-1].body)
		insert_returns(body[-1].orelse)

	if isinstance(body[-1], ast.With) or isinstance(body[-1], ast.AsyncWith):
		insert_returns(body[-1].body)

def remove_markdown(code: str):
    return code.replace("py", ' ').strip("` ").translate(str.maketrans({
        '‘': "'",
        '’': "'",
        '“': "\"",
        '”': "\"",
    }))

class Owner(commands.Cog, name="Owner Commands"):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="eval",
                       description="Execute arbitrary python code in an environment similar to that of a command.",
                       guild_ids=guild_ids,
                       options=[
                           create_option(
                               name="code",
                               description="the code to be executed",
                               option_type=3,
                               required=True
                           )
                       ])
    async def _eval(self, ctx, *, code: str):    
        await ctx.respond()

        code = remove_markdown(code)
        closure = "_aoi_eval"

        code = "\n".join(f"    {line}" for line in code.splitlines())
        body = f"async def {closure}():\n{code}"
        await ctx.send(f"```py\n{body}\n```")

        try:
            if not await self.bot.is_owner(ctx.author):
                embed = discord.Embed(description="This command is owner-only.",
                                      color=discord.Color.from_rgb(255, 74, 74))
                embed.set_author(name="Error")

                return await ctx.send(embed=embed)
            
            parsed = ast.parse(body)
            body = parsed.body[0].body
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

            insert_returns(body)
            exec(compile(parsed, filename="<eval>", mode="exec"), environment)
            result = await eval(f"{closure}()", environment)

            if result != None and result != "":
                await ctx.send(result)
        except Exception as err:
            embed = discord.Embed(title=f"{type(err).__name__}",
                                  description=f"{err}",
                                  timestamp=ctx.message.created_at,
                                  color=discord.Color.from_rgb(255, 74, 74))
            embed.set_author(name="Evaluation Failure")
            embed.set_footer(text=ctx.author.name)

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Owner(bot))
