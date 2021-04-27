# Script modified:
import os
from pathlib import Path
import sqlite3
import json
from dotenv import load_dotenv
load_dotenv()

champ_file = Path(__file__).parent / "champ_data.json"
data_file = Path(__file__).parent / "game_data.json"

default_champ_list = json.load(champ_file)

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

def user_check(ctx):
    uid = str(ctx.author.id)
    result = database_request((
        "SELECT userid "
        "FROM users "
        "WHERE userid = ? "
        "LIMIT 1;",
        (uid,)
    ))
    if result is not None:
        return
    database_request((
        "INSERT INTO users "
        "(userid, summonerid) "
        "VALUES (?, ?);",
        (uid, "PLACEHOLDER")
    ))
    for champ, data in default_champ_list.items():
        cid = champ['cid']
        database_request((
            "INSERT INTO champs "
            "(champid, userid, mastery, owned, displayname) "
            "VALUES "
            "(?, ?, ?, ?, ?);",
            (cid, uid, 0, False, champ['displayname'])
        ))
        for pos in ['top', 'jungle', 'mid', 'bottom', 'support']:
            database_request((
                "INSERT INTO sanity "
                "(champid, userid, position, sane, feas) "
                "VALUES "
                "(?, ?, ?, ?, ?);",
                (cid, uid, pos, champ['positions']['pos'],
                 champ['feasibility']['pos'])
            ))



def database_request(command):
    """Execute database command.

    Open connection, execute command,
    then close the connection automatically.
    """
    DATABASE = os.getenv('DATABASE')
    db = sqlite3.connect(str(DATABASE))
    db.row_factory = dict_factory
    db.execute("PRAGMA foreign_keys = ON")
    cur = db.execute(command)
    result = cur.fetchall()
    if db is not None:
        db.commit()
        db.close()
    return result

def get_list_ids(ctx, list_name):
    """Get a list for userid with name."""
    user_check(ctx)
    uid = str(ctx.author.id)
    result = database_request((
        "SELECT champid FROM listdata "
        "WHERE userid = ? "
        "AND listname = ?;"
        (uid, list_name)))
    if result is not None:
        return [row['champid'] for row in result]
    return None

def get_champ_attrib(ctx, champid, attrib):
    """Get User's attrib (can be list) for champid."""
    user_check(ctx)
    was_string = False
    if type(attrib) is str:
        attrib = [attrib]
        was_string = True
    uid = str(ctx.author.id)
    attribs = ','.join([f'champs.{a} AS {a}' for a in attrib])
    result = database_request((
       "SELECT ? FROM champs "
       "WHERE userid = ? "
       "AND champid = ? "
       "LIMIT 1;",(attr, uid, champid)))
    if was_string:
        if result is None:
            return None
        return result[0][attr]
    return result[0]

async def get_list_attrib(ctx, list_name, attrib):
    """Get a list in displayname format."""
    user_check(ctx)
    was_string = False
    ret = {}
    if type(attrib) is str:
        attrib = [attrib]
        was_string = True
    uid = str(ctx.author.id)
    attribs = ','.join([f'champs.{a}' for a in attrib])
    result = database_request((
       "SELECT ? FROM lists "
       "LEFT JOIN champs ON "
       "lists.champid = champs.champid "
       "AND lists.userid = champs.userid "
       "WHERE userid = ?;",(attribs, uid, champid)))
    if was_string:
        if result is None:
            return None
        return [row[attr] for row in result]
    return result


async def alias_to_champid(ctx, alias):
    uid = str(ctx.author.id)
    result = database_request((
        "SELECT champs.champid AS cid, "
        "champs.displayname AS dname "
        "FROM aliases "
        "LEFT JOIN champs "
        "ON champs.champid = aliases.champid "
        "AND champs.userid = aliases.userid "
        "WHERE aliases.alias = ? "
        "AND (aliases.userid = ? "
        "OR aliases.userid = STANDARD) "
        "AND champs.userid = ?;",
        (alias.lstrip().rstrip(), uid, uid)
    ))
    if len(result):
        for displayname, champid in [(row['dname'], row['cid']) for row in
                                     result]:
            response = None
            while response not in ['y', 'n']:
                response = \
                    call_input(ctx, f"By '{alias}', did you mean {displayname}?'")
            if response == 'y':
                return int(champid)
    ctx.send(f'```fix\nWARN: Could not resolve alias "{alias}". Ignoring.\n```')
    return None

async def create_list(ctx, list_name, list_json):
    """Create a list for userid under name."""
    user_check(ctx)
    uid = str(ctx.author.id)
    existing = get_list_attrib(ctx, list_name, 'displayname')
    if existing is not None:
        list_text = "```\n"+ ",\n".join(existing) + '\n```'
        warn = f'```fix\nWARN: You are attempting to overwrite an existing list!\n"{list_name}" already exists, and contains:\n```'
        prompt = '''```fix\nAre you sure you want to overwrite this list? (y/n)\n'''
        await ctx.send(warn)
        await ctx.send(list_text)
        response = None
        while response not in  ['y', 'n']:
            response = await call_input(prompt)
        if response == 'n':
            await ctx.send("List was not overwritten.")
            return
    database_request((
        "INSERT INTO lists (userid, listname) "
        "VALUES (?, ?);", (uid, list_name)
    ))
    for alias in list(set(list_json)):
        champid = await alias_to_champid(ctx, alias)
        if champid is None:
            continue
        database_request((
            "INSERT INTO listdata "
            "(userid, listname, champid) "
            "VALUES (?, ?, ?);", (uid, list_name, champid)
        ))
    new_list = get_list_attrib(ctx, list_name, 'displayname')
    await ctx.send(f"New list {list_name} created!")
    await ctx.send(f"```\nList Contains:\n" + (",\n".join(new_list)) + "\n```")
    return


def get_sanity(ctx, cid):
    uid = str(ctx.author.id)
    positions = {}
    feasibility = {}
    for pos in ['top', 'jungle', 'mid', 'bottom', 'support']:
        for user in [uid, "STANDARD"]:
            result = database_request((
                "SELECT sane, feas FROM "
                "champs WHERE champid = ? "
                "AND userid = ? LIMIT 1;",
                (cid, user)
            ))
            if result is None:
                continue
            sane = result[0]['sane']
            feas = result[0]['feas']
            if positions.get(pos, None) is None and sane is not None:
                positions[pos] = bool(sane)
            if feasibility.get(pos, None) is None and feas is not None:
                feasibility[pos] = int(feas)
    return positions, feasibility



def get_champ_list(ctx, use_list=None):
    user_check(ctx)
    champ_list = {}
    if use_list is not None:
        list_dicts = get_list_attrib(ctx, use_list, ['displayname', 'mastery','owned', 'champid'])
        for champ in list_dicts:
            cid = int(champ['champid'].pop(0))
            dname = champ['displayname']
            mastery = int(champ['mastery'])
            owned = bool(champ['owned'])
            positions, feasibilty = get_sanity(ctx, cid)
            champ_list[cid] = {
                'owned': owned,
                'displayname': dname,
                'champid': cid,
                'mastery': mastery,
                'positions': positions,
                'feasibility': feasibility
            }
    return champ_list

