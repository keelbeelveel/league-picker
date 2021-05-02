import re
from exceptions import UserException, SystemException
from discord.ext import commands
from msg_types import code_msg
import data_handler as db

class My(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.debug = bot.debug
        self.max_len = 10

    async def list_handler(self, ctx, msg_list, list_cols=None, list_title=None):
        """
        Output given list to ctx.

        If list is less than MAX_LEN, send to ctx.
        If list exceeds MAX_LEN, DM it instead.
        """

        msg = ""
        if list_title is not None or list_cols is not None:
            msg += f"# [{ctx.author}]"
            if list_title is not None:
                msg += f" [{list_title}] "
            if list_cols is not None:
                msg += f" [{list_cols[0]}] [{list_cols[1]}]"
            msg += "\n\n"
        for i, item in enumerate(msg_list):
            if type(item) is list:
                item = f'[{item[0]}]({item[1]})'
            msg += f"{i+1}. {item}\n"
        msg = msg.rstrip()
        if len(msg_list) > self.max_len or True:
            await ctx.author.send(code_msg(msg, 'md'))

    def format_to_args(self, list_datas, args):
        reverse=False
        args.reverse()
        for arg in args:
            if '=' in arg:
                key = arg.split('=')[0]
                val = arg.split('=')[1]
                key = key.lower()
                val = val.lower()
                if key == "sort":
                    if val in ['l', 'len', 'length', 'size']:
                        if 'length' in list_datas[0].keys():
                            list_datas.sort(key=lambda o: o['length'])
                            reverse=True
                    elif val in ['m', 'mastery']:
                        if 'mastery' in list_datas[0].keys():
                            list_datas.sort(key=lambda o: o['mastery'])
                    elif val in ['alpha', 'az']:
                        if 'name' in list_datas[0].keys():
                            list_datas.sort(key=lambda o: o['name'])
                elif key in ['n', 'length', 'len', 'size', 'results']:
                    list_datas = list_datas[0:int(val)]
                else:
                    raise UserException(f"Unknown key {key}.")
            else:
                if arg == "sort":
                    list_datas.sort(key=lambda o: o['name'])
                elif arg in ['rev', 'reverse', 'descending']:
                    reverse = True
        if reverse:
            list_datas.reverse()
        return list_datas



    @commands.command(name='my', help='')
    async def my_handler(self, ctx, *cmdargs):
        args = []
        subargs = []
        for arg in cmdargs:
            if re.search(r'^-+', arg):
                subargs.append(re.sub(r'^-+', '', arg.lower()))
            else:
                args.append(arg.lower())
        if args is None or len(args) == 0:
            # Usage stuff
            if self.debug:
                print("usage")
        elif args[0] in ['lists', 'l'] and len(args) == 1:
            # self.list_lists
            await self.list_lists(ctx, subargs)
        elif args[0] in ['list', 'l']:
            # self.list_list
            await self.list_list(ctx, args[1:], subargs)
        elif args[0] in ['champs', 'c'] and len(args) == 1:
            # self.list_champs
            await self.list_champs(ctx, subargs)
        elif args[0] in ['champ', 'c']:
            # self.list_champ
            await self.list_champ(ctx, args[1:], subargs)
        elif args[0] in ['mastery', 'm']:
            # self.list_mastery
            await self.list_mastery(ctx, args[1:], subargs)
        elif args[0] in ['recent', 'recents', 'r']:
            # self.list_recent
            await self.list_recent(ctx, args[1:], subargs)
        else:
            await ctx.send(code_msg(f"Unknown argument '{args[1]}'.", 'diff'))

    @commands.command(name='my lists', help='')
    async def list_lists(self, ctx, args):
        u_lists = db.get_user_lists(ctx)
        list_datas = []
        for lst in u_lists:
            list_datas.append({
                'name': lst,
                'length': db.get_list_len(ctx, lst),
                'mastery': db.get_list_mastery(ctx, lst)
            })
        list_datas = self.format_to_args(list_datas, args)
        for arg in args:
            if 'mastery' in arg:
                list_datas = [[lst['name'], lst['mastery']] for lst in list_datas]
                await self.list_handler(ctx, list_datas, ['Name', 'Mastery'],
                                        "Lists")
                return
            for word in ['len', 'size']:
                if word in arg:
                    list_datas = [[lst['name'], lst['length']] for lst in list_datas]
                    await self.list_handler(ctx, list_datas, ['Name',
                                                              'Length'],
                                            "Lists")
                    return
        await self.list_handler(ctx, [[lst['name'], lst['length']] for lst in
                                      list_datas], ['Name', 'Length'], "Lists")


    @commands.command(name='my list [listname]', aliases=['my [listname]'], help='')
    async def list_list(self, ctx, listname, args):
        #TODO
        return "TODO"

    @commands.command(name='my champs', aliases=['my champions'], help='')
    async def list_champs(self, ctx, args):
        #TODO
        return "TODO"

    @commands.command(name='my champ [champname]', help='')
    async def list_champ(self, ctx, alias, args):
        #TODO
        return "TODO"

    @commands.command(name='my mastery', help='')
    async def list_mastery(self, ctx, args):
        #TODO
        return "TODO"

    @commands.command(name='my recents', help='', aliases=['my recent'])
    async def list_recent(self, ctx, champs, args):
        #TODO
        return "TODO"

