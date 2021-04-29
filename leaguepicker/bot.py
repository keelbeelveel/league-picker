import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from picker import Picker
from cogs import bot_cogs
load_dotenv()
owner = 195241303460675584
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='~', case_insensitive=True)
for cog in bot_cogs:
    bot.add_cog(cog(bot))

#@bot.command(name)
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching,name="you int"))
    print("==[ Ready. ]==")


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

bot.run(TOKEN)
