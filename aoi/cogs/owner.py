import ast

import discord
from discord.ext import commands

def insert_returns(body):
	# insert return stmt if the last expression is a expression statement
	if isinstance(body[-1], ast.Expr):
		body[-1] = ast.Return(body[-1].value)
		ast.fix_missing_locations(body[-1])

	# for if statements, we insert returns into the body and the orelse
	if isinstance(body[-1], ast.If):
		insert_returns(body[-1].body)
		insert_returns(body[-1].orelse)

	# for with blocks, again we insert returns into the body
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

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, code: str):
        """ Execute arbitrary python code in an environment similar to that of a command. """
        
        code = remove_markdown(code)
        fn_name = "_aoi_eval"

        code = "\n".join(f"    {i}" for i in code.splitlines())
        body = f"async def {fn_name}():\n{code}"

        try:
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
                "me": ctx.me,
                "guild": ctx.guild,
                "author": ctx.author,
                "channel": ctx.channel,
            }

            insert_returns(body)
            exec(compile(parsed, filename="<eval>", mode="exec"), environment)
            result = await eval(f"{fn_name}()", environment)

            await ctx.send(result)
        except Exception as err:
            embed = discord.Embed(
            	title=f"{type(err).__name__}",
                description=f"{err}",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(255, 74, 74)
            )
            embed.set_author(name="Evaluation Failure")
            embed.set_footer(text=ctx.author.name)

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Owner(bot))
