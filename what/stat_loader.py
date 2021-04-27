import json
import sys
from pathlib import Path
import re
import time
from helper import data_dir, champ_file

def default_aliases(name, existing=None):
    if existing is None:
        existing = []
    aliases = existing
    for char in [" ", "'", "~", "&"]:
        abbrev = ""
        for part in name.split(char):
            part = part.lower().lstrip().rstrip()
            part = re.sub(r'[^a-zA-Z]+', '', part)
            if part != '':
                abbrev = abbrev + part[0]
            if part not in aliases and part != '':
                aliases.append(part)
                if name != part:
                    print(f"(Automatically added new alias for {name} : {part})")
        if abbrev not in aliases and char in name:
            aliases.append(abbrev)
            if name != part:
                print(f"(Automatically added new alias for {name} : {abbrev})")

    return aliases


def write_to_file():
    tmp_file = data_dir/'.tmp'/"champ_data.json.tmp"
    with open(tmp_file, 'w') as file:
        json.dump(champs, file, indent = 4)

    champ_file.write_text(tmp_file.read_text())
    print("Champ data written.")


def write_to_revert():
    tmp_file = data_dir/'.tmp'/"champ_data.json.revert.tmp"
    with open(tmp_file, 'w') as file:
        json.dump(champs, file, indent = 4)

    revert_file = data_dir/'tmp'/"champ_data.json.revert"
    revert_file.write_text(tmp_file.read_text())
    print("Backup saved.")


def fancy_name(name):
    fname = name.lower()
    for char in [" ", "'"]:
        if char in name:
            list_parts = name.split(char)
            temp = list_parts.pop(0)
            fname = temp[0].upper() + temp[1:].lower()
            for part in list_parts:
                fname = fname + char + part[0].upper() + part[1:].lower()
            break
    fname = fname[0].upper() + fname[1:]
    return fname


def get_fun(champ):
    print(f"Rate how much fun you have playing {champ} on a 0-9 scale. 5 if unsure/neutral.")
    while True:
        try:
            rating = int(input("Your fun rating: "))
        except ValueError:
            print("Invalid input.")
        else:
            if rating < 0 or rating > 9:
                print("Invalid input.")
            else:
                return rating


def get_skill(champ):
    print(f"Rate how skilled you are at playing {champ} on a 0-9 scale. 5 if unplayed/neutral.")
    while True:
        try:
            rating = int(input("Your skill rating: "))
        except ValueError:
            print("Invalid input.")
        else:
            if rating < 0 or rating > 9:
                print("Invalid input.")
            else:
                return rating


def get_feasibility(champ):
    feasibility = {}
    positions = ['top', 'jungle', 'mid', 'bottom', 'support']
    for idx, pos in enumerate(['in top lane', 'in the jungle', 'in mid lane', 'as an ADC/APC', 'as a support']):
        print(f"On the following scale, rate the feasibility of playing {champ} {pos}.\n")
        print(" 9 \t It's their main role.")
        print(" 8 \t It's a common/meta role for them, but not their main.")
        print(" 7 \t It's not necessarily common, but you see it often enough.")
        print(" 6 \t I'm not sure because I've never tried/seen it, but it could work.")
        print(" 5 \t Maybe some people could make this work, but it would be pretty troll.")
        print(" 4 \t With the right composition or build it could be a pretty funny lane.")
        print(" 3 \t I'm not sure because I've never tried/seen it, but I'm pretty sure it wouldn't work.")
        print(" 2 \t If I saw this on the enemy loading screen, I would laugh.")
        print(" 1 \t If I saw a teammate hover this, I would report them or dodge.")
        print(" 0 \t I hope to god I never play this lane .")
        while True:
            try:
                rating = int(input("\nYour rating: "))
            except ValueError:
                print("Bad input.")
            else:
                break

        feasibility[positions[idx]] = rating

    return feasibility


def get_ownership():
    ownstring = input('Owned?\t').lower()
    owned = bool(ownstring != '' and ownstring[0] == 't')
    mastery = int(input('Mastery?\t'))
    return (owned, mastery)


def get_positions():
    position_string = input('Positions?\t').lower()
    positions = {
        'top': False,
        'jungle': False,
        'mid': False,
        'bottom': False,
        'support': False
    }
    for position in position_string.split():
        for pos, _ in positions.items():
            if position[0] == pos[0]:
                positions[pos] = True
    return positions


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


def show_help():
    print("\n\nAdditional options:")
    print("\t[name or alias] - Edit an existing champion.")
    print("\tdone - Save all changes and exit the editor.")
    print("\tsave - Save changes but continue editing.")
    print("\texit - Exit without saving changes.")
    print("\tsetall [freq/owned/mastery/sanity] - Edit a field for all champs at once.")


def are_you_absolutely_certain(msg):
    print(msg)
    print("Are you absolutely certain you would like to make this action?")
    for _ in range(5):
        sys.stdout.write('. ')
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write('\n')
    resp = ""
    while resp != "YES" and resp != "NO":
        resp = input('Type exactly "YES" to continue or "NO" to abort. ').lstrip().rstrip()
    return bool(resp == "YES")


def setall(prompt):
    key = prompt.split()[1].rstrip().lstrip()
    try:
        if key == "freq":
            val = int(input("Input a new frequency value.\n"))
            print(f"You are about to set the play frequency for every champion to {val}. This action is irreversible.")
            if are_you_absolutely_certain("This action is irreversible. Changes to the JSON file will be saved immediately."):
                write_to_revert()
                for _, data in champs.items():
                    data['freq'] = val
                write_to_file()
                print("Changes saved. Version before changes can be found at champ_data.json.revert, but will be overwritten by the next save action.")
        elif key == "owned":
            val = None
            while val != "TRUE" and val != "FALSE":
                val = int(input('Input exactly "TRUE" or "FALSE" to set the ownership for all champtions.\n')).lstrip().rstrip()
            val = bool(val == "TRUE")
            print(f"You are about to set the ownership for every champion to {val}. This action is irreversible.")
            if are_you_absolutely_certain("This action is irreversible. Changes to the JSON file will be saved immediately."):
                write_to_revert()
                for _, data in champs.items():
                    data['owned'] = val
                write_to_file()
                print("Changes saved. Version before changes can be found at champ_data.json.revert, but will be overwritten by the next save action.")
        elif key == "mastery":
            val = int(input("Input a new mastery value.\n"))
            print(f"You are about to set the mastery for every champion to {val}. This action is irreversible.")
            if are_you_absolutely_certain("This action is irreversible. Changes to the JSON file will be saved immediately."):
                write_to_revert()
                for _, data in champs.items():
                    data['freq'] = val
                write_to_file()
                print("Changes saved. Version before changes can be found at champ_data.json.revert, but will be overwritten by the next save action.")
        elif key == "sanity":
            val = None
            while val != "TRUE" and val != "FALSE":
                val = int(input('Input exactly "TRUE" or "FALSE" to set the sanity for all champtions in all lanes.\n')).lstrip().rstrip()
            val = bool(val == "TRUE")
            print(f"You are about to set the sanity for every champion to {val}. This action is irreversible.")
            if are_you_absolutely_certain("This action is irreversible. Changes to the JSON file will be saved immediately."):
                write_to_revert()
                for _, data in champs.items():
                    for pos in data['positions'].values():
                        pos = val
                write_to_file()
                print("Changes saved. Version before changes can be found at champ_data.json.revert, but will be overwritten by the next save action.")
        else:
            print("Invalid setall field.")
    except ValueError or TypeError:
        print("Invalid input. Changes were not saved.")
        return
    return

# Always run
data_file = Path(__file__).parent / 'champ_data.json'
with open(data_file, 'r') as file:
    champs = json.load(file)

for champ, data in champs.items():
    data['aliases'] = default_aliases(champ, data['aliases'])
    if 'feasibility' not in data.keys():
        data['feasibility'] = get_feasibility(champ)
    if 'fun' not in data.keys():
        data['fun'] = 5
    if 'skill' not in data.keys():
        data['skill'] = 5
    if 'owned' not in data.keys():
        data['owned'] = False
    if 'mastery' not in data.keys():
        data['mastery'] = 0


def run():
    champ = input('\n\nEnter champion to edit/add or "help" provides additional options.\t').lower()
    while champ != "done":
        if champ == "help" or champ == "":
            show_help()
        elif champ.split()[0] == "setall":
            setall(champ)
        elif champ == "save":
            write_to_revert()
            write_to_file()
        elif champ == "exit":
            if are_you_absolutely_certain("Exit without saving? Unwritten changes will be lost."):
                return
        else:
            try:
                champ = alias_to_champ(champ)
                if champ in champs.keys():
                    print(f"The champion {champ} already exists in the list. The current entry is:\n")
                    print(json.dumps(champs[champ], indent = 4))
                    print("\nWhat would you like to edit?\n")
                    options = ""
                    for key in champs[champ].keys():
                        options = options + f"{key} "
                    options = options + "none"

                    edit = input(f"Editing {champs[champ]['displayname']}. Pick from: [{options}]\n\t").lower()
                    while edit != 'none':
                        if edit == 'owned' or edit == 'mastery':
                            champs[champ]['owned'], champs[champ]['mastery'] = get_ownership()
                        elif edit == 'positions' or edit == 'pos':
                            champs[champ]['positions'] = get_positions()
                        elif edit == 'aliases' or edit == 'alias' or edit == 'a':
                            get_aliases(champ)
                        elif edit == 'displayname' or edit == 'dname':
                            dname = input("Provide a new displayname.\t")
                            champs[champ]['displayname'] = dname
                        elif edit == 'feasibility' or edit == 'f':
                            champs[champ]['feasibility'] = get_feasibility(champ)
                        elif edit == 'fun':
                            champs[champ]['fun'] = get_fun(champ)
                        elif edit == 'skill' or edit == 's':
                            champs[champ]['skill'] = get_skill(champ)
                        else:
                            print("This key cannot currently be edited or is invalid.")
                        print("The new entry reads:\n")
                        print(json.dumps(champs[champ], indent = 4))
                        edit = input(f"Editing {champs[champ]['displayname']}. Pick from: [{options}]\n\t").lower()
                    champ = input('\n\nChamp Name:\t').lower()
                    continue
                owned, mastery = get_ownership()
                positions = get_positions()
                feasibility = get_feasibility(champ)
                fun = get_fun(champ)
                skill = get_skill(champ)
                list_positions = ""
                for pos, valid in positions.items():
                    if valid:
                        list_positions = list_positions + f"{pos} "
                print(f"Looks correct?\n\nName:\t{champ}\nOwned:\t{owned}\nMastery:\t{mastery}\nPositions:\t{list_positions}\n")
                confirm = input('(y/n)\t').lower()
                aliases = default_aliases(champ)
            except ValueError or IndexError:
                print("Error with input occurred. The last champ added or edited may not have been saved.\n")
            else:
                if confirm[0] == 'y':
                    champs[champ] = {
                        'owned': owned,
                        'mastery': mastery,
                        'positions': positions,
                        'freq': 0,
                        'aliases': aliases,
                        'displayname': fancy_name(champ),
                        'feasibility': feasibility,
                        'fun': fun,
                        'skill': skill
                    }
        champ = input('\n\nEnter champion to edit/add or "help" provides additional options.\t').lower()

    for champ, data in champs.items():
        if 'freq' not in data.keys():
            data['freq'] = 0
        if 'aliases' not in data.keys():
            data['aliases'] = []
    write_to_file()
