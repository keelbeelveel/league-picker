from discord.ext import commands
from picker import Picker
from exceptions import SystemException

class Rolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.debug = self.bot.debug

    @commands.command(name='roll', help='Roll a champ/position to play from your pool.', usage='--pos=[-][tjmbs] --sanity=[sane|insane|all] --feas=[std|nonmeta|troll|hell] -n=[#] --5q --from=[list,champs,here] --as=saveListorSavedList')
    async def roll(self, ctx, *args):
        try:
            p = Picker(self.bot,ctx,self.debug)
            result = await p.select(args)
        except SystemException as err:
            await self.bot.sys_ex(err, ctx)
            result = '''```diff\n- Something went wrong on our end.\n```'''
        await ctx.send(f"{result}")

    @commands.command(name='top', aliases=['t'], help='Roll a top champion from your pool.', usage='--sanity=[sane|insane|all] --feas=[std|nonmeta|troll|hell] -n=[#] --from=[list,champs,here] --as=saveListorSavedList')
    async def roll_top(self, ctx, *args):
        try:
            p = Picker(self.bot, ctx,self.debug)
            params = ['top']
            for arg in args:
                params.append(arg)
            result = await p.select(params)
        except SystemException as err:
            await self.bot.sys_ex(err, ctx)
            result = '''```diff\n- Something went wrong on our end.\n```'''
        await ctx.send(f"{result}")

    @commands.command(name='jungle', aliases=['jg', 'j'], help='Roll a jungle champion from your pool.', usage='--sanity=[sane|insane|all] --feas=[std|nonmeta|troll|hell] -n=[#] --from[list,champs,here] --as=saveListorSavedList')
    async def roll_jungle(self, ctx, *args):
        try:
            p = Picker(self.bot, ctx,self.debug)
            params = ['jg']
            for arg in args:
                params.append(arg)
            result = await p.select(params)
        except SystemException as err:
            await self.bot.sys_ex(err, ctx)
            result = '''```diff\n- Something went wrong on our end.\n```'''
        await ctx.send(f"{result}")

    @commands.command(name='middle', aliases=['mid', 'm'], help='Roll a middle champion from your pool.', usage='--sanity=[sane|insane|all] --feas=[std|nonmeta|troll|hell] -n=[#] --from=[list,champs,here] --as=saveListorSavedList')
    async def roll_mid(self, ctx, *args):
        try:
            p = Picker(self.bot, ctx,self.debug)
            params = ['mid']
            for arg in args:
                params.append(arg)
            result = await p.select(params)
        except SystemException as err:
            await self.bot.sys_ex(err, ctx)
            result = '''```diff\n- Something went wrong on our end.\n```'''
        await ctx.send(f"{result}")

    @commands.command(name='bottom', aliases=['bot', 'b', 'adc', 'shitrole'], help='Roll a bottom champion from your pool.', usage='--sanity=[sane|insane|all] --feas=[std|nonmeta|troll|hell] -n=[#] --from=[list,champs,here] --as=saveListorSavedList')
    async def roll_bot(self, ctx, *args):
        try:
            p = Picker(self.bot, ctx,self.debug)
            params = ['bot']
            for arg in args:
                params.append(arg)
            result = await p.select(params)
        except SystemException as err:
            await self.bot.sys_ex(err, ctx)
            result = '''```diff\n- Something went wrong on our end.\n```'''
        await ctx.send(f"{result}")

    @commands.command(name='support', aliases=['sup', 'supp', 's'], help='Roll a support champion from your pool.', usage='--sanity=[sane|insane|all] --feas=[std|nonmeta|troll|hell] -n=[#] --from=[list,champs,here] --as=saveListorSavedList')
    async def roll_supp(self, ctx, *args):
        try:
            p = Picker(self.bot, ctx,self.debug)
            params = ['supp']
            for arg in args:
                params.append(arg)
            result = await p.select(params)
        except SystemException as err:
            await self.bot.sys_ex(err, ctx)
            result = '''```diff\n- Something went wrong on our end.\n```'''
        await ctx.send(f"{result}")

