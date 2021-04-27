import sys
import json
from pathlib import Path
from datetime import datetime
import re
import random
import os
from helper import champ_file, data_file, data_dir


with open(champ_file, 'r') as file:
    champs = json.load(file)

with open(data_file, 'r') as file:
    game_history = json.load(file)

debug = False;

def get_aliases(alias):
    while True:
        fancy_champ = champs[champ]['displayname']
        list_aliases = input(f'List comma separated aliases for {fancy_champ}:\t').lower().split(',')
        print(f"\nAdding the following aliases for {fancy_champ}:\n")
        redundant = []
        for idx, al in enumerate(list_aliases):
            al = al.lstrip().rstrip()
            list_aliases[idx] = al
            if al in champs[alias]['aliases']:
                redundant.append(al)

        for al in redundant:
            list_aliases.remove(al)
        for al in list_aliases:
            print(f'\t"{al}"')
        if len(redundant):
            print("\nThe following aliases were ignored (redundant):\n")
            for al in redundant:
                print(f'\t"{al}"\n')

        good = input("\nLooks good? (y/n)\t").lower()
        if bool(good != '' and good[0] == "y"):
            for al in list_aliases:
                champs[alias]['aliases'].append(al)
            return


def alias_to_champ(alias):
    if alias in champs.keys():
        return alias
    for champ, data in champs.items():
        if alias in data['aliases']:
            conf = input(f"Did you mean {champs[champ]['displayname']}? (y/n)\t").lower()
            if conf != '' and conf[0] == 'y':
                alias = champ
                break
    return alias


def filter_feasibility(sel_body, min_feas=0, max_feas=9):
    remove = []
    for pick in sel_body:
        champ = pick['champ']
        pos = pick['position']
        feas = int(champs[champ]['feasibility'][pos])
        if feas < min_feas or feas > max_feas:
            remove.append(pick)

    for pick in remove:
        sel_body.remove(pick)
    return sel_body


def filter_fun(sel_body, min_fun = 0, max_fun=9):
    remove = []
    for pick in sel_body:
        champ = pick['champ']
        pos = pick['position']
        fun = int(champs[champ]['fun'])
        if fun < min_fun or fun > max_fun:
            remove.append(pick)

    for pick in remove:
        sel_body.remove(pick)
    return sel_body


def filter_skill(sel_body, min_skill=0, max_skill=9):
    remove = []
    for pick in sel_body:
        champ = pick['champ']
        pos = pick['position']
        fun = int(champs[champ]['skill'])
        if skill < min_skill or skill > max_skill:
            remove.append(pick)

    for pick in remove:
        sel_body.remove(pick)
    return sel_body


def filter_age(sel_body, min_age=0, max_age=None):
    # TODO
    return sel_body


def generate_selection_body(params, exclude_champs=None):
    if exclude_champs is None:
        exclude_champs = []
    sel_body = []
    champ_list = []
    if params['use_list'] is not None:
        if params['use_list'] == "":
            list_file = data_dir / '.tmp' / 'tmp.json'
        else:
            print("found list ")
            list_file = data_dir / 'lists' / params['use_list']
            print(list_file)
        with open(list_file) as file:
            raw_list = json.load(file)
            for item in raw_list:
                champ = alias_to_champ(item)
                if champ in champs.keys():
                    champ_list.append(champ)
                else:
                    print(f"{champ} not found in valid champ directory. Add new champs with python3 stat_loader.py")
    else:
        for champ in champs.keys():
            champ_list.append(champ)

    for champ in exclude_champs:
        champ_list.remove(champ)
    for champ in champ_list:
        positions = ['top', 'mid', 'jungle', 'bottom', 'support'] if params['positions'] is None else params['positions']
        for pos in positions:
            pos_acceptable = ((params['pos_sanity'] == 'sane' and champs[champ]['positions'][pos]) or (params['pos_sanity'] == 'insane' and not champs[champ]['positions'][pos]) or params['pos_sanity'] == 'all')
            if pos_acceptable:
                pick = {
                    'champ': champ,
                    'position': pos
                }
                sel_body.append(pick)

    if params['min_feas'] is not None or params['max_feas'] is not None:
        min_feas = 0 if params['min_feas'] is None else params['min_feas']
        max_feas = 9 if params['max_feas'] is None else params['max_feas']
        sel_body = filter_feasibility(sel_body, min_feas, max_feas)

    if params['min_fun'] is not None or params['max_fun'] is not None:
        min_fun = 0 if params['min_fun'] is None else params['min_fun']
        max_fun = 9 if params['max_fun'] is None else params['max_fun']
        sel_body = filter_fun(sel_body, min_fun, max_fun)

    if params['min_skill'] is not None or params['max_skill'] is not None:
        min_skill = 0 if params['min_skill'] is None else params['min_skill']
        max_skill = 9 if params['max_skill'] is None else params['max_skill']
        sel_body = filter_skill(sel_body, min_skill, max_skill)

    return sel_body

def do_selection(params, choices, exclude_champs=None):
    if exclude_champs is None:
        exclude_champs = []
    sel_body = generate_selection_body(params, exclude_champs)
    shuffles = random.randint(0,10)
    for _ in range(shuffles):
        random.shuffle(sel_body)

    if choices > len(sel_body):
        sys.stderr.write("Parameters make search body too narrow. Adjust your options.\n")
        sys.exit(1)
    elif choices == 1:
        result = random.choice(sel_body)
        print(f"Selected {champs[result['champ']]['displayname']} {result['position'][0].upper()+result['position'][1:]}")
        if debug:
            print(f"Feasibility: {champs[result['champ']]['feasibility'][result['position']]}")
        exclude_champs.append(result['champ'])
    else:
        result = random.sample(sel_body, choices)
        for pick in result:
            print(f"Selected {champs[pick['champ']]['displayname']} {pick['position'][0].upper()+pick['position'][1:]}")
            if debug:
                print(f"Feasibility: {champs[pick['champ']]['feasibility'][pick['position']]}")
            exclude_champs.append(pick['champ'])
    return exclude_champs

def center_title(title, char, cols):
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

def smart_print_inline(text, indent, cols):
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
        smart_print_inline(" ".join(text.split(' ')[split_at-1:]), indent, cols)

def show_help():
    cols, lines = os.get_terminal_size()
    print("Run to randomly select League picks.\n\n")
    center_title("ARGUMENTS", "=", cols)
    print('')
    center_title("The selector itself supports many arguments. One or more can be used, although overconstraining the selection may return an error.", " ", cols)
    print('')
    print(" --position=[+/-][tjmbs] | --pos=[+/-][tjmbs] | -p=[+/-][tjmbs]")
    print('')
    smart_print_inline("Contrain the roles to be selected from.\n", 4, cols)
    smart_print_inline("List the roles to play, like --pos=tjb for Top, Jungle, or Bottom.\n", 4, cols)
    smart_print_inline("Use '-' to subtract a role to avoid, like --pos=-mj to indicate anything but Mid or Jungle.\n", 4, cols)
    if lines < 50:
        input("Press ENTER to continue.")
    print('')
    print(" --sanity=[sane|insane|all] | -s=[sane|insane|all]\n")
    smart_print_inline("Constrain role/champ pairs using a sanity check. Options:\n", 4, cols)
    smart_print_inline("'sane'\t: (default) only select champs/roles where the sanity is set to True.\n", 4, cols)
    smart_print_inline("'insane'\t: Invert the sanity check. Only select champs/roles where the sanity is set to False.\n", 4, cols)
    smart_print_inline("'all'\t: Ignore the sanity check entirely. All champs/roles are fair game.\n", 4, cols)
    if lines < 50:
        input("Press ENTER to continue.")
    print('')
    print(' --feas=[preset] | -f=[preset]\n')
    smart_print_inline("Constrain the selection to feasibility scores within the preset range. Presets include:\n", 4, cols)
    print("    |  PRESET  | MIN_FEAS  | MAX_FEAS  |")
    print("    |----------|-----------|-----------|")
    print("    | meta/std |     7     |     9     |")
    print("    | nonmeta  |     5     |     7     |")
    print("    | troll    |     3     |     5     |")
    print("    | hell     |     0     |     3     |")
    print("    |-meta/-std|     0     |     7     |")
    print("    | -nonmeta |     0     |     5     |")
    print("    | -troll   |     5     |     9     |")
    print("    | -hell    |     3     |     9     |")
    print("    |----------|-----------|-----------|\n")
    smart_print_inline("NOTE: For most presets (other than meta), -s=all needs to be specified to ignore sanity check!\n", 4, cols)
    smart_print_inline("Feasibility scores for individual champ/roles can be edited using the 'edit' flag (more info below).\n",4,cols)
    if lines < 50:
        input("Press ENTER to continue.")
    print('')
    print(' --minfeas=[count] | -mnfs=[count]\n')
    smart_print_inline("The minimum acceptable feasibility score to be included in the result. 0 (default) includes all results. Count must be between 0 and 9 (inclusive).\n", 4, cols)
    print(' --maxfeas=[count] | -mxfs=[count]\n')
    smart_print_inline("The maximum acceptable feasibility score to be included in the result. 9 (default) includes all results. Count must be between 0 and 9 (inclusive).\n", 4, cols)
    print(' --5q | -5\n')
    smart_print_inline("Specify this flag to generate 5 sets of selections, one for each role (for teams of 5). The 5q flag guarantees that selections for each role will not conflict with one another.\n", 4, cols)
    print(' --choices=[count] | -n=[count]\n')
    smart_print_inline("Specify the number of options to choose from for each selection. Choices will not repeat. This is compatible with the --5q option (designed to ensure at least one champ is not banned or is owned, especially in 5q mode)\n", 4, cols)
    smart_print_inline("NOTE: If [count] exceeds the number of available selections, an error will be returned. Reduce the constraints/parameters or decrease [count] to produce results. (Make sure to use --sanity=all with the --feas flag)\n", 4, cols)
    print("")
    input("Press ENTER to continue.")
    print('')
    center_title("PRESETS", "=", cols)
    print('')
    smart_print_inline("The following commands allow the saving and loading from preset champion lists. Champion lists must be saved to the /league-picker/ folder and use the naming convention listName.json.\n", 4, cols)
    smart_print_inline("To use a champion pool, simply specify the flag:\n", 4, cols)
    print('''    --from='["champA","champB","champC",...]'  \n''')
    smart_print_inline("Champion names specified in the list must be quoted as seen here. Listed names can either be champion names or acceptable aliases (ie. 'mundo'). The program will confirm that it interpreted your alias correctly. Aliases can be customized using the 'edit' flag (more info below).\n", 4, cols)
    smart_print_inline("The list can also be inverted (ie. a list of champs to exclude) by putting a minus sign '-' after the equals sign. This only works for the --from= flag, and will not work if a '-' is added to a saved list.\n", 4, cols)
    smart_print_inline("By default, the specified champion list will not be saved. To save the list for easy use later, use the flag:\n", 4, cols)
    print('''    --as=[listName]\n''')
    smart_print_inline("listName must be an acceptable filename or the program will not be able to store your list. The list can then be edited at the file `/league-picker/listName.json`.\n", 4, cols)
    smart_print_inline("In the future, a saved list can be accessed using only the `--as=listName` flag. This can also be shortened to `-i=listName`. This flag will load the list from the file at listName.json and select from the specified champion pool. Champion lists are compatible with all previously listed flags.\n", 4, cols)
    input("Press ENTER to continue.")
    print('')
    center_title("EDITING", '=', cols)
    print('')
    smart_print_inline("The mastery, ownership, aliases, displaynames, play frequency, sanity, and feasibility of each role/champ can be customized. Custom builds or runes can easily be added to the system. To access the champion data editor, run this command with 'edit' as the first argument.\n", 4, cols)
    smart_print_inline('To add a new build/runeset from the editor, simply create a custom name for a new "champion". Name it something distinctive, for example "Omnistone Nasus" or "AD Twitch". The system will walk you through assigning sanity and feasibility scores to your addition. These entries can now be selected like any other champion.\n''', 4, cols)
    smart_print_inline("To edit the mastery, ownership, alias, frequency, feasibility, sanity, etc. for an existing entry, just type an existing name or alias into the editor dialog. The program will confirm that it interpreted your alias correctly, and show you the entry data. Then, enter the field to be altered.\n", 4, cols)
    smart_print_inline("Note that the 'fun', 'skill', and 'freq' categories cannot be used to filter selections at this time.\n", 4, cols)
    smart_print_inline("For additional editing help, type 'help' into the editor dialog for more information.\n", 4, cols)
    input("Press ENTER to exit.")


def select(args):
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
        'positions': None,
        'pos_sanity': 'sane',
    }


    choices = 1
    args_list = []
    list_as = None
    team_mode = False
    for arg in args:
        arg = arg.lower()
        if '-' in arg:
            arg = re.sub(r'^-+', '', arg)
        if '=' in arg:
            key = arg.split('=')[0]
            val = arg.split('=')[1]
            if key == 'sanity' or key == "s":
                if val == 'sane' or val == "s":
                    print("sane")
                    parameters['pos_sanity'] = 'sane'
                elif val == 'insane' or val == "i":
                    print("insane")
                    parameters['pos_sanity'] = 'insane'
                elif val == 'all' or val == "a":
                    print("all")
                    parameters['pos_sanity'] = 'all'
                else:
                    sys.stderr.write("Invalid value for key 'sanity', valid options include [s]ane, [i]nsane, [a]ll\n")
                    sys.exit(1)
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
                print(f"selecting from {opts}")
            if key == 'choices' or key == "n":
                choices = int(val)
                if choices <= 0 or choices > 155:
                    sys.stderr.write("Invalid value for key 'choices', must be 0 < n <= 155\n")
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
                        sys.stderr.write("Invalid feasibility setting. Valid options are [std|meta|nonmeta|troll|hell|9|0]\n")
                        sys.exit(1)
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
                        sys.stderr.write("Invalid feasibility setting. Valid options are [std|meta|nonmeta|troll|hell|9|0]\n")
                        sys.exit(1)
                print(f"Filtering feasibilty by range {parameters['min_feas']} <= f <= {parameters['max_feas']}")
            if key == 'from':
                invert_list = False
                if val[0] == "-":
                    invert_list = True
                    val = val[1:]
                try:
                    entered_list = json.loads(val)
                except:
                    sys.stderr.write("Failed to load from list. Make sure list in json format.")
                    sys.exit(1)
                if invert_list:
                    for champ in champs.keys():
                        args_list.append(champ)
                for item in entered_list:
                    champ = alias_to_champ(item)
                    if champ not in champs.keys():
                        print(f"Could not find {champ} in data. Ignoring.")
                        continue
                    if invert_list:
                        args_list.remove(champ)
                    else:
                        args_list.append(champ)
            if key == 'as' or key == "i":
                list_as = f'{val}.json'
        else:
            if arg == '5q' or arg == "5":
                team_mode = True
            elif arg == 'help' or arg == "h":
                show_help()
                sys.exit(0)
    if len(args_list):
        if list_as is None:
            list_as = 'tmp.json'
            list_dir = data_dir /'.tmp'
            parameters['use_list'] = ""
        else:
            list_dir = data_dir / 'lists'
            parameters['use_list'] = list_as
        if list_as == 'champ_data' or list_as == 'game_data':
            sys.stderr.write("Invalid list name-- would overwrite a necessary program file.\n")
            sys.exit(1)
        list_file = list_dir / list_as
        if not list_file.exists():
            list_file.touch()
        with open(list_file, 'w') as file:
            json.dump(args_list, file, indent=4)
    if team_mode:
        exclude_champs = None
        for pos in ['top', 'jungle', 'mid', 'bottom', 'support']:
            parameters['positions'] = [pos]
            print(f"Selection for {pos[0].upper()}{pos[1:].lower()} ======")
            exclude_champs = do_selection(parameters, choices, exclude_champs)
            print("\n======================================================\n")
    else:
        do_selection(parameters, choices)
