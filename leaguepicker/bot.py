import os
import discord
import json
import sys
from dotenv import load_dotenv
from discord.ext import commands
from picker import Picker
from cogs import bot_cogs
from msg_types import code_msg
load_dotenv()
owner = int(os.getenv('OWNER'))
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='~', case_insensitive=True)

bot.debug = False
bot.silent = False
if len(sys.argv) > 2:
    bot.silent = bool(sys.argv[2].lower() == 'true')
if len(sys.argv) > 1:
    bot.debug = bool(sys.argv[1].lower() == 'true')

for cog in bot_cogs:
    bot.add_cog(cog(bot))

#@bot.command(name)
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching,name="you int"))
    msg = f"Bot started. [Debug={bot.debug}][Silent={bot.silent}]"
    print(msg)
    if not bot.silent:
        await to_owner(msg)



@bot.before_invoke
async def log_ctx(ctx):
    params = []
    print(f'@{ctx.author} : ~{ctx.invoked_with}')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
            user_owner = await bot.fetch_user(owner)
            await user_owner.send(f'```diff\n- Unhandled message: {args[0]}\n```')
        else:
            user_owner = await bot.fetch_user(owner)
            await user_owner.send(f'```diff\n- Unknown error: {event} {args} {kwargs}\n```')

async def to_owner(msg):
    user_owner = await bot.fetch_user(owner)
    await user_owner.send(msg)


async def system_ex(msg, ctx):
    msg = \
        code_msg(f"SystemException: {msg}", 'diff') + \
        "\n" + \
        code_msg(f'\tauthor: "{ctx.author}",\n\tcontent: "{ctx.message.content}"',
                 'json')
    await to_owner(msg)


@bot.event
async def on_command_error(ctx, error):
    with open('err.log', 'a') as f:
        f.write(f'Command error: {error}\n')
        user_owner = await bot.fetch_user(owner)
        await user_owner.send(f'```diff\n- Command error: {error}\n```')

async def get_input(ctx, prompt):
    await ctx.author.send(prompt)
    def check(msg):
        return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)

    msg = await bot.wait_for("message", check=check)
    return msg.content

bot.sys_ex = system_ex
bot.get_in = get_input
bot.to_own = to_owner
bot.run(TOKEN)
