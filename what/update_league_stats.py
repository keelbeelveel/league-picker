import json
from pathlib import Path
import re
import datetime
import sys
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

def yes_or_no(prompt):
    while True:
        resp = input(prompt)
        if resp == "":
            continue
        if resp[0] == "y":
            return True
        elif resp[0] == "n":
            return False
        else:
            continue


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



champ_file = Path(__file__).parent / 'champ_data.json'
with open(champ_file, 'r') as file:
    champs = json.load(file)

data_file = Path(__file__).parent / 'game_data.json'
with open(data_file, 'r') as  file:
    game_history = json.load(file)

for champ, data in champs.items():
    data['aliases'] = default_aliases(champ, data['aliases'])
    if 'feasibility' not in data.keys():
        data['feasibility'] = get_feasibility(champ)
    if 'fun' not in data.keys():
        data['fun'] = get_fun(champ)
    if 'skill' not in data.keys():
        data['skill'] = get_skill(champ)


champ = alias_to_champ(input("Who did you just play?\n").lower())
while champ not in champs.keys():
    print("Invalid champion. You can add new champs with ~/bin/stat_loader.py .")
    champ = alias_to_champ(input("Who did you just play?\n"))

position = input("What position did you play?\n").lower()
while position == "" or position[0] not in ['t', 'j', 'm', 'b', 's', 'a']:
    position = input("What position did you play?\n").lower()

position = 'top' if position[0] == "t" else position
position = 'jungle' if position[0] == "j" else position
position = 'mid' if position[0] == "m" else position
position = 'bottom' if position[0] == "b" else position
position = 'support' if position[0] == "s" else position
position = 'aram' if position[0] == "a" else position

did_win = yes_or_no("Did you win? (y/n)\n")
had_fun = yes_or_no("Did you have fun? (y/n)\n")
impacted_game = yes_or_no("Did you feel like you had control over the outcome? (y/n)\n")
notes = input("Any other notes?\n")

match = {
    'champ': champ,
    'position': position,
    'win': did_win,
    'fun': had_fun,
    'did_well': impacted_game,
    'notes': notes,
    'time': f"{datetime.datetime.now()}"
}

print("Does this look right?\n")
print(json.dumps(match))
if not yes_or_no("(y/n)\n"):
    sys.exit(0)


if 'history' not in champs[champ].keys():
    champs[champ]['history'] = []

champs[champ]['history'] = [match] + champs[champ]['history']

if game_history is None:
    game_history = []

game_history = [match] + game_history

champs[champ]['freq'] = 1 + champs[champ]['freq']

tmp_file = Path(__file__).parent/"tmp.json"
with open(tmp_file, 'w') as file:
    json.dump(champs, file, indent = 4, default = lambda o: 'not serializable')
champ_file.write_text(tmp_file.read_text())

print("Champ data written.")

with open(tmp_file, 'w') as  file:
    json.dump(game_history, file, indent = 4)

print("Game data written.")
data_file.write_text(tmp_file.read_text())
