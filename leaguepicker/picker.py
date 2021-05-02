import sys
import json
from pathlib import Path
from datetime import datetime
import re
import random
import os
from data_handler import alias_to_champid, call_input, create_list
from data_handler import get_list_attrib, get_champ_attrib
from data_handler import get_champ_list
from exceptions import UserException, SystemException

class Picker:
    def __init__(self, bot, ctx, debug=False):
        self.bot = bot
        self.ctx = ctx
        self.champs = get_champ_list(ctx)
        self.debug=debug


    async def call_input(self, prompt):
        string = await self.bot.get_in(self.ctx, prompt)
        return string

    def filter_feasibility(self, sel_body, min_feas=0, max_feas=9):
        remove = []
        for pick in sel_body:
            champ = pick['champ']
            pos = pick['position']
            feas = int(self.champs[champ]['feasibility'][pos])
            if feas < min_feas or feas > max_feas:
                remove.append(pick)

        for pick in remove:
            sel_body.remove(pick)
        return sel_body


    def filter_fun(self, sel_body, min_fun = 0, max_fun=9):
        remove = []
        for pick in sel_body:
            champ = pick['champ']
            pos = pick['position']
            fun = int(self.champs[champ]['fun'])
            if fun < min_fun or fun > max_fun:
                remove.append(pick)

        for pick in remove:
            sel_body.remove(pick)
        return sel_body


    def filter_skill(self, sel_body, min_skill=0, max_skill=9):
        remove = []
        for pick in sel_body:
            champ = pick['champ']
            pos = pick['position']
            fun = int(self.champs[champ]['skill'])
            if skill < min_skill or skill > max_skill:
                remove.append(pick)

        for pick in remove:
            sel_body.remove(pick)
        return sel_body


    def filter_age(self, sel_body, min_age=0, max_age=None):
        # TODO
        return sel_body


    async def generate_selection_body(self, params, exclude_champs=None):
        if exclude_champs is None:
            exclude_champs = []
        sel_body = []
        champ_list = []
        if params['use_list'] is not None:
            raw_list = get_champ_list(self.ctx, params['use_list'])
            for champ in raw_list.keys():
                champ_list.append(champ)
        else:
            for champ in self.champs.keys():
                champ_list.append(champ)

        for champ in exclude_champs:
            champ_list.remove(champ)
        for champ in champ_list:
            positions = ['top', 'mid', 'jungle', 'bottom', 'support'] if params['positions'] is None or params['positions'] == [] else params['positions']
            for pos in positions:
                pos_acceptable = ((params['pos_sanity'] == 'sane' and self.champs[champ]['positions'][pos]) or (params['pos_sanity'] == 'insane' and not self.champs[champ]['positions'][pos]) or params['pos_sanity'] == 'all')
                if pos_acceptable:
                    pick = {
                        'champ': champ,
                        'position': pos
                    }
                    sel_body.append(pick)

        if params['min_feas'] is not None or params['max_feas'] is not None:
            min_feas = 0 if params['min_feas'] is None else params['min_feas']
            max_feas = 9 if params['max_feas'] is None else params['max_feas']
            sel_body = self.filter_feasibility(sel_body, min_feas, max_feas)

        if params['min_fun'] is not None or params['max_fun'] is not None:
            min_fun = 0 if params['min_fun'] is None else params['min_fun']
            max_fun = 9 if params['max_fun'] is None else params['max_fun']
            sel_body = self.filter_fun(sel_body, min_fun, max_fun)

        if params['min_skill'] is not None or params['max_skill'] is not None:
            min_skill = 0 if params['min_skill'] is None else params['min_skill']
            max_skill = 9 if params['max_skill'] is None else params['max_skill']
            sel_body = self.filter_skill(sel_body, min_skill, max_skill)

        return sel_body

    async def do_selection(self, params, choices, exclude_champs=None):
        output = ""
        if exclude_champs is None:
            exclude_champs = []
        sel_body = await self.generate_selection_body(params, exclude_champs)
        shuffles = random.randint(0,10)
        for _ in range(shuffles):
            random.shuffle(sel_body)

        if choices > len(sel_body):
            raise UserException("Parameters make search body too narrow. Adjust your options.\n")
        elif choices == 1:
            result = random.choice(sel_body)
            output = output + f"Selected {self.champs[result['champ']]['displayname']} {result['position'][0].upper()+result['position'][1:]}\n"
            if self.debug:
                output = output + f"Feasibility: {self.champs[result['champ']]['feasibility'][result['position']]}\n"
            exclude_champs.append(result['champ'])
        else:
            result = random.sample(sel_body, choices)
            for pick in result:
                output = output + f"Selected {self.champs[pick['champ']]['displayname']} {pick['position'][0].upper()+pick['position'][1:]}\n"
                if self.debug:
                    output = output + f"Feasibility: {self.champs[pick['champ']]['feasibility'][pick['position']]}\n"
                exclude_champs.append(pick['champ'])
        return exclude_champs, output

    def center_title(self, title, char, cols):
        title = f" {title} "
        output = ""
        cols = cols - len(title)
        if cols % 2 != 0:
            first_half = int(((cols - 1)/2)+1)
            second_half = first_half - 1
        else:
            first_half = int(cols/2)
            second_half = first_half
        for _ in range(first_half):
            output = output + char
        output = output + title
        for _ in range(second_half):
            output = output + char
        print(output)

    def smart_print_inline(self, text, indent, cols):
        indent_string = " " * indent
        text = indent_string + text
        split_at = 0
        fit_text = " ".join(text.split(' ')[0:split_at])
        while len(fit_text) < cols and split_at <= len(text.split(' ')):
            split_at = split_at + 1
            fit_text = " ".join(text.split(' ')[0:split_at])
        fit_text = " ".join(text.split(' ')[0:split_at-1])
        print(fit_text)
        if split_at < len(text.split(' ')):
            self.smart_print_inline(" ".join(text.split(' ')[split_at-1:]), indent, cols)


    async def select(self,args):
        output = ""
        parameters = {
            'min_feas': None,
            'max_feas': None,
            'min_skill': None,
            'max_skill': None,
            'min_fun': None,
            'max_fun': None,
            'min_age': None,
            'max_age': None,
            'max_freq': None,
            'min_freq': None,
            'use_list': None,
            'positions': [],
            'pos_sanity': 'sane',
        }


        choices = 1
        args_list = []
        list_as = None
        team_mode = False
        still_listing=False
        entries = []
        for arg in args:
            arg = arg.lower()
            print(arg)
            if arg.isspace():
                continue
            if '-' in arg:
                arg = re.sub(r'^-+', '', arg)
            if '=' in arg or still_listing:
                if '=' not in arg:
                    val = arg
                else:
                    key = arg.split('=')[0]
                    val = arg.split('=')[1]
                if key == 'sanity' or key == "s":
                    if val == 'sane' or val == "s":
                        parameters['pos_sanity'] = 'sane'
                    elif val == 'insane' or val == "i":
                        parameters['pos_sanity'] = 'insane'
                    elif val == 'all' or val == "a":
                        parameters['pos_sanity'] = 'all'
                    else:
                        raise UserException("Invalid value for key 'sanity', valid options include [s]ane, [i]nsane, [a]ll")
                if key == 'position' or key == 'pos' or key == "p":
                    parameters['positions'] = ['top', 'jungle', 'mid', 'bottom', 'support']
                    remove = []
                    if val[0] == "-":
                        for pos in parameters['positions']:
                            if pos[0] in val:
                                remove.append(pos)
                        for pos in remove:
                            parameters['positions'].remove(pos)
                    else:
                        for pos in parameters['positions']:
                            if pos[0] not in val:
                                remove.append(pos)
                        for pos in remove:
                            parameters['positions'].remove(pos)
                    opts = ""
                    for pos in parameters['positions']:
                        opts = opts + f'{pos} '
                if key == 'choices' or key == "n":
                    choices = int(val)
                    if choices <= 0 or choices > 155:
                        raise UserException("Invalid value for key 'choices', must be 0 < n <= 155")
                        sys.exit(1)
                if key == 'minfeas' or key == 'mnfs':
                    minfeas = int(val)
                    if minfeas < 0:
                        minfeas = 0
                        print("Minimum feasibility below 0 -- Ignored. Defaulting to 0.")
                    if minfeas > 9:
                        minfeas = 9
                        print("Minimum feasibility above 9 -- Ignored. Defaulting to 9.")
                    parameters['min_feas'] = min_feas
                if key == 'maxfeas' or key == 'mxfs':
                    maxfeas = int(val)
                    if maxfeas < 0:
                        maxfeas = 0
                        print("Maximum feasibility below 0 -- Ignored. Defaulting to 0.")
                    if maxfeas > 9:
                        maxfeas = 9
                        print("Maximum feasibility above 9 -- Ignored. Defaulting to 9.")
                    parameters['min_feas'] = min_feas
                if key == 'feas' or key == "f":
                    if val[0] == "-":
                        if val[1:] == "std" or val[1:] == "meta":
                            parameters['max_feas'] = 7
                        elif val[1:] == "nonmeta":
                            parameters['max_feas'] = 5
                        elif val[1:] == "troll":
                            parameters['min_feas'] = 5
                        elif val[1:] == "hell":
                            parameters['min_feas'] = 3
                        elif val[1:] == "9":
                            parameters['max_feas'] = 8
                        elif val[1:] == "0":
                            parameters['min_feas'] = 1
                        else:
                            raise UserException("Invalid feasibility setting. Valid options are [std|meta|nonmeta|troll|hell|9|0]")
                    else:
                        if val == "std" or val == "meta":
                            parameters['min_feas'] = 7
                        elif val == "nonmeta":
                            parameters['min_feas'] = 5
                            parameters['max_feas'] = 7
                        elif val == "troll":
                            parameters['min_feas'] = 3
                            parameters['max_feas'] = 5
                        elif val == "hell":
                            parameters['max_feas'] = 3
                        elif val == "9":
                            parameters['min_feas'] = 9
                        elif val == "0":
                            parameters['max_feas'] = 0
                        else:
                            raise UserException("Invalid feasibility setting. Valid options are [std|meta|nonmeta|troll|hell|9|0]")
                            sys.exit(1)
                    print(f"Filtering feasibilty by range {parameters['min_feas']} <= f <= {parameters['max_feas']}")
                if key == 'from' or still_listing:
                    still_listing = bool(']' not in val)
                    print(still_listing)
                    invert_list = False
                    if val[0] == "-":
                        invert_list = True
                        val = val[1:]
                    val = re.sub('^\[|\]$', '', val)
                    try:
                        json_data = None
                        for v in val.split(','):
                            if v.lstrip().rstrip().lower().isspace():
                                continue
                            entries.append(v.lstrip().rstrip().lower())

                        print(still_listing)
                        if not still_listing:
                            if "" in entries:
                                entries.remove("")
                            json_data = '["' + ('","').join(entries) + '"]'
                            print(json_data)
                            entered_list = json.loads(json_data)
                    except:
                        raise SystemException("Failed to load from list.")
                    if json_data is None:
                        continue
                    if invert_list:
                        for champ in self.champs.keys():
                            args_list.append(champ)
                    for item in entered_list:
                        champ = await alias_to_champid(self.ctx, item)
                        if champ not in self.champs.keys():
                            print(f"Could not find {champ} in data. Ignoring.")
                            continue
                        if invert_list:
                            args_list.remove(champ)
                        else:
                            args_list.append(champ)
                if key == 'as' or key == "i":
                    list_as = f'{val}'
                    parameters['use_list'] = list_as
            else:
                if arg == '5q' or arg == "5":
                    team_mode = True
                elif arg == 'top' or arg == "t":
                    parameters['positions'].append('top')
                elif arg == 'mid' or arg == "m" or arg == "middle":
                    parameters['positions'].append('mid')
                elif arg == 'jg' or arg == "j" or arg == "jungle":
                    parameters['positions'].append('jungle')
                elif arg == 'bot' or arg == "b" or arg == "bottom" or arg == "adc":
                    parameters['positions'].append('bottom')
                elif arg == 'sup' or arg == "s" or arg == "support" or arg == "supp":
                    parameters['positions'].append('support')
                elif arg == 'sysex':
                    if self.debug:
                        raise SystemException("Forced SystemException")
                elif arg == 'stdex':
                    if self.debug:
                        raise Exception("Forced Exception")
                elif arg == 'usex':
                    if self.debug:
                        raise UserException("Forced UserException")

        if still_listing:
            raise UserException("No closing ']' found in list.")
        if len(args_list):
            if list_as is None:
                list_as = '~~tmp~~'
            parameters['use_list'] = list_as
            # TODO: Is this necessary?
            if list_as == 'champ_data' or list_as == 'game_data':
                raise SystemException("Invalid list name-- would overwrite a necessary program file.\n")
            await create_list(self.ctx, list_as, args_list)
        try:
            if team_mode:
                exclude_champs = None
                for pos in ['top', 'jungle', 'mid', 'bottom', 'support']:
                    parameters['positions'] = [pos]
                    output = output + f"Selection for {pos[0].upper()}{pos[1:].lower()} ======\n"

                    exclude_champs, fragment = await self.do_selection(parameters, choices, exclude_champs)
                    output = output + "\n======================================================\n"
            else:
                _, output = await self.do_selection(parameters, choices)
            return output
        except UserException as err:
            return f"```diff\n- {err}\n```"
        except Exception as err:
            raise SystemException(err)
