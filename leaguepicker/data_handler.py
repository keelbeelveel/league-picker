# Script modified:
import os
from pathlib import Path
import sqlite3
import json
from dotenv import load_dotenv
load_dotenv()

champ_file = Path(__file__).parent / "champ_data.json"
data_file = Path(__file__).parent / "game_data.json"
with open(champ_file) as file:
    default_champ_list = json.load(file)

def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries. Note that this is inefficient
    for larger queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

async def call_input(ctx, prompt):
    from bot import get_input
    string = await get_input(ctx, prompt)
    return string.lower()

def database_request(command):
    """Execute database command.

    Open connection, execute command,
    then close the connection automatically.
    """
    DATABASE = os.getenv('DATABASE')
    dfile = Path(__file__).parent.parent / 'var' / DATABASE
    db = sqlite3.connect(str(dfile))
    db.row_factory = dict_factory
    db.execute("PRAGMA foreign_keys = ON")
    if len(command) < 2:
        cur = db.execute(command[0])
    else:
        cur = db.execute(command[0], command[1])
    result = cur.fetchall()
    if db is not None:
        db.commit()
        db.close()
    return result

def user_check(uid):
    result = database_request([
        "SELECT userid "
        "FROM users "
        "WHERE userid = ? "
        "LIMIT 1;",
        (uid,)
    ])
    if result is not None and result != []:
        return
    database_request([
        "INSERT INTO users "
        "(userid, summonerid) "
        "VALUES (?, ?);",
        (uid, "PLACEHOLDER")
    ])
    for champ, data in default_champ_list.items():
        cid = data['cid']
        database_request([
            "INSERT INTO champs "
            "(champid, userid, mastery, owned, champ, displayname) "
            "VALUES "
            "(?,?,?,?,?,?);",
            (cid, uid, 0, False, champ, data['displayname'])
        ])
        for pos in ['top', 'jungle', 'mid', 'bottom', 'support']:
            database_request([
                "INSERT INTO sanity "
                "(champid, userid, position, sane, feas) "
                "VALUES "
                "(?,?,?,?,?);",
                (cid, uid, pos, data['positions'][pos],
                 data['feasibility'][pos])
            ])

def create_standard_aliases():
    user_check('STANDARD')
    result = database_request([
        "SELECT * FROM aliases WHERE "
        "userid = 'STANDARD' LIMIT 1;"
    ])
    if result is not None and result != []:
        return
    for champ, data in default_champ_list.items():
        for alias in data['aliases']:
            database_request([
                "INSERT INTO aliases (champid, userid, alias) "
                "VALUES (?,?,?);",
                (data['cid'], 'STANDARD', alias)
            ])
            print(f"--[Loaded alias:][{alias}]--")


def get_user_lists(ctx):
    """Get all listnames for a user."""
    uid = str(ctx.author.id)
    user_check(uid)
    result = database_request([
        "SELECT listname FROM "
        "lists WHERE userid = ?;",
        (uid,)
    ])
    lists = []
    if result is not None and result != []:
        for row in result:
            if row['listname'] == '~~tmp~~':
                # Exclude tmp lists
                continue
            lists.append(row['listname'])
    return lists

def get_list_len(ctx, list_name):
    """Get the length of a list for uid with name."""
    uid = str(ctx.author.id)
    user_check(uid)
    result = database_request([
        "SELECT champid FROM "
        "listdata WHERE userid = ? "
        "AND listname = ?;",
        (uid, list_name)
    ])
    return len(list(set([row['champid'] for row in result])))

def get_list_mastery(ctx, list_name):
    """Get the total mastery of a list."""
    uid = str(ctx.author.id)
    user_check(uid)
    result = database_request([
        "SELECT champs.mastery FROM "
        "listdata LEFT JOIN champs "
        "ON listdata.champid = champs.champid "
        "AND listdata.userid = champs.userid "
        "WHERE listdata.userid = ? "
        "AND listdata.listname = ?;",
        (uid, list_name)
    ])
    mastery = 0
    for row in result:
        mastery += int(row['mastery'])
    return mastery


def get_list_ids(ctx, list_name):
    """Get a list for userid with name."""
    uid = str(ctx.author.id)
    user_check(uid)
    result = database_request([
        "SELECT champid FROM listdata "
        "WHERE userid = ? "
        "AND listname = ?;",
        (uid, list_name)
    ])
    if result is not None and result != []:
        return [row['champid'] for row in result]
    return None

def get_champ_attrib(ctx, champid, attrib):
    """Get User's attrib (can be list) for champid."""
    uid = str(ctx.author.id)
    user_check(uid)
    was_string = False
    if type(attrib) is str:
        attrib = [attrib]
        was_string = True
    attribs = ','.join([f'champs.{a} AS {a}' for a in attrib])
    result = database_request([
       f"SELECT {attribs} FROM champs "
       "WHERE userid = ? "
       "AND champid = ? "
       "LIMIT 1;",(uid, champid)
    ])
    if was_string:
        if result == []:
            return None
        return result[0][attrib[0]]
    return result[0]

def get_list_attrib(ctx, list_name, attrib):
    """Get a list in displayname format."""
    uid = str(ctx.author.id)
    user_check(uid)
    was_string = False
    ret = {}
    if type(attrib) is str:
        attrib = [attrib]
        was_string = True
    attribs = ','.join([f'champs.{a} AS {a}' for a in attrib])
    result = database_request([
        f"SELECT {attribs} FROM listdata "
        "LEFT JOIN champs ON "
        "listdata.champid = champs.champid "
        "AND listdata.userid = champs.userid "
        "WHERE listdata.userid = ? "
        "AND listdata.listname = ?;",(uid,list_name)
    ])
    if was_string:
        if result is None or result == []:
            return None
        return [row[attrib[0]] for row in result]
    return result

def get_all_attrib(ctx, attrib):
    uid = str(ctx.author.id)
    user_check(uid)
    was_string = False
    ret = {}
    if type(attrib) is str:
        attrib = [attrib]
        was_string = True
    attribs = ','.join([f'champs.{a} AS {a}' for a in attrib])
    result = database_request([
       f"SELECT {attribs} FROM champs "
       "WHERE userid = ?;",
        (uid,)
    ])
    if was_string:
        if result is None or result == []:
            return None
        return [row[attrib[0]] for row in result]
    return result

async def alias_to_champid(ctx, alias):
    uid = str(ctx.author.id)
    result = database_request([
        "SELECT champs.champid AS cid, "
        "champs.displayname AS dname "
        "FROM aliases "
        "LEFT JOIN champs "
        "ON champs.champid = aliases.champid "
        "AND champs.userid = aliases.userid "
        "WHERE aliases.alias = ? "
        "AND (aliases.userid = ? "
        "OR aliases.userid = 'STANDARD');",
        (alias.lstrip().rstrip(), uid)
    ])
    if len(result) > 1:
        for displayname, champid in [(row['dname'], row['cid']) for row in
                                     result]:
            if alias.lower().lstrip().rstrip() == displayname.lower():
                response = 'y'
            else:
                response = None
            while response not in ['y', 'n']:
                response = \
                    await call_input(ctx, f"By '{alias}', did you mean {displayname}?'")
            if response == 'y':
                return int(champid)
    elif len(result) == 1:
        # If only one champ with alias, dont ask for confimation
        return(int(result[0]['cid']))
    await ctx.send(f'```fix\nWARN: Could not resolve alias "{alias}". Ignoring.\n```')
    return None

async def create_list(ctx, list_name, list_json):
    """Create a list for userid under name."""
    uid = str(ctx.author.id)
    user_check(uid)
    existing = database_request([
        "SELECT * FROM lists WHERE "
        "listname = ? AND userid = ? "
        "LIMIT 1;", (list_name,uid)
    ])
    if existing is not None and existing != []:
        if list_name != '~~tmp~~':
            existing = get_list_attrib(ctx, list_name, 'displayname')
            existing.sort()
            warn = f'```fix\nWARN: You are attempting to overwrite an existing list!\n"{list_name}" already exists'
            if existing is not None and existing != []:
                warn = warn + ' and contains:'
                list_text = "```\n"+ ",\n".join(existing) + '\n```'

                warn = warn + '\n```'
                prompt = '''```fix\nAre you sure you want to overwrite this list? (y/n)\n```'''
                await ctx.send(warn)
                await ctx.send(list_text)
                response = None
                while response not in ['y', 'n']:
                    response = await call_input(ctx, prompt)
                if response == 'n':
                    await ctx.send("List was not overwritten.")
                    return
        database_request([
            "DELETE FROM lists "
            "WHERE lists.userid = ? "
            "AND lists.listname = ?;",
            (uid, list_name)
        ])
    database_request([
        "INSERT INTO lists (userid, listname) "
        "VALUES (?, ?);", (uid, list_name)
    ])
    for alias in list(set(list_json)):
        if type(alias) is not int:
            champid = await alias_to_champid(ctx, alias)
        else:
            champid = alias
        if champid is None:
            continue
        database_request([
            "INSERT INTO listdata "
            "(userid, listname, champid) "
            "VALUES (?, ?, ?);", (uid, list_name, champid)
        ])
    new_list = get_list_attrib(ctx, list_name, 'displayname')
    new_list.sort()
    if list_name != '~~tmp~~':
        await ctx.send(f"New list **{list_name}** created!")
        await ctx.send(f"```\nList {list_name} Contains:\n" + (",\n".join(new_list)) + "\n```")
    return


def get_sanity(ctx, cid):
    uid = str(ctx.author.id)
    positions = {}
    feasibility = {}
    for pos in ['top', 'jungle', 'mid', 'bottom', 'support']:
        result = database_request([
            "SELECT sanity.sane AS sane, "
            "sanity.feas AS feas FROM "
            "champs LEFT JOIN sanity "
            "on champs.champid = sanity.champid "
            "WHERE champs.champid = ? "
            "AND sanity.position = ? "
            "AND sanity.userid = ? LIMIT 1;",
            (cid, pos, uid)
        ])
        if result == []:
            continue
        sane = result[0]['sane']
        feas = result[0]['feas']
        positions[pos] = bool(sane)
        feasibility[pos] = int(feas)
    return positions, feasibility



def get_champ_list(ctx, use_list=None):
    uid = str(ctx.author.id)
    user_check(uid)
    champ_list = {}
    if use_list is not None:
        list_dicts = get_list_attrib(ctx, use_list, ['displayname', 'mastery','owned', 'champid'])
    else:
        list_dicts = get_all_attrib(ctx, ['displayname', 'mastery', 'owned','champid'])
    for champ in list_dicts:
        cid = int(champ['champid'])
        dname = champ['displayname']
        mastery = int(champ['mastery'])
        owned = bool(champ['owned'])
        positions, feasibility = get_sanity(ctx, cid)
        champ_list[cid] = {
            'owned': owned,
            'displayname': dname,
            'champid': cid,
            'mastery': mastery,
            'positions': positions,
            'feasibility': feasibility
        }
    return champ_list

