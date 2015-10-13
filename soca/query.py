
import pyhdb

import config
from config import schema
from model import Player, Team, Match

import re

OPTA_RE = re.compile(r'DFL-...-.+')


def execute(query, arguments):
    connection = pyhdb.connect(
        config.HOST, config.PORT,
        config.USER, config.PASSWORD
    )

    cur = connection.cursor()
    cur.execute(query, arguments)
    result = cur.fetchall()
    connection.close()

    return result



def _get_teams_of_match(match_id):

    sql = '''WITH T AS (
            SELECT DISTINCT TEAM_ID, IS_HOME_TEAM FROM {schema}.APPEARANCE
            WHERE MATCH_ID = ?
        )
        SELECT ID, NAME, CODE, OPTA_ID, T.IS_HOME_TEAM FROM {schema}.TEAM
            JOIN T ON
                T.TEAM_ID = ID
        ORDER BY IS_HOME_TEAM DESC
    '''.format(schema=schema)

    teams = execute(sql, [match_id])

    home = Team(*teams[0][:-1])
    guest = Team(*teams[1][:-1])

    return home, guest

def get_teams(query):
    query = query.strip()

    sql = '''SELECT ID, NAME, CODE, OPTA_ID
        FROM {schema}.TEAM'''.format(schema=schema)
    where = []
    args = []

    if OPTA_RE.match(query):
        where.append(r'OPTA_ID = ?')
        args.append(query)

    else:
        if query.isdigit():
            where.append(r'ID = ?')
            args.append(int(query)) 

        if query.isalnum() and len(query) >= 2:
            where.append(r"OPTA_ID LIKE 'DFL-CLU-%' || UPPER(?)")
            args.append(query)

    if where:
        sql += ' WHERE ' + ' OR '.join(where)

    return [
        Team(id_, name, code, opta_id)
        for id_, name, code, opta_id
          in execute(sql, args)
    ]



def get_matches(query):
    query = query.strip()

    sql = '''SELECT ID, DATE, COMPETITION, PITCH_HEIGHT, PITCH_WIDTH, OPTA_ID
        FROM {schema}.MATCH'''.format(schema=schema)
    where = []
    args = []

    if OPTA_RE.match(query):
        where.append(r'OPTA_ID = ?')
        args.append(query)

    else:
        if query.isdigit():
            where.append(r'ID = ?')
            args.append(int(query)) 

        if query.isalnum() and len(query) >= 2:
            where.append(r"OPTA_ID LIKE 'DFL-MAT-%' || UPPER(?)")
            args.append(query)

    if where:
        sql += ' WHERE ' + ' OR '.join(where)

    matches = []
    for id_, date, competition, height, width, opta_id in execute(sql, args):
        home, guest = _get_teams_of_match(id_)
        matches.append(Match(
            id_, date, competition, height, width, opta_id,
            home=home,
            guest=guest,
        ))

    return matches

def get_players(query):
    query = query.strip()

    sql = '''SELECT ID, FIRST_NAME, LAST_NAME, OPTA_ID
        FROM {schema}.PLAYER'''.format(schema=schema)
    where = []
    args = []

    if OPTA_RE.match(query):
        where.append(r'OPTA_ID = ?')
        args.append(query)
    else:
        # check for database id
        if query.isdigit():
            where.append(r'ID = ?')
            args.append(int(query))
        # check name
        if not any(char.isdigit() for char in query):
            where.append(r"UPPER(FIRST_NAME) LIKE '%'|| UPPER(?) || '%'")
            where.append(r"UPPER(LAST_NAME) LIKE '%'|| UPPER(?) || '%'")
            args.append(query)
            args.append(query)

        # check for wildcarding opta
        if query.isalnum() and len(query) >= 2:
            where.append(r"OPTA_ID LIKE 'DFL-OBJ-%' || UPPER(?)")
            args.append(query)

    if where:
        sql += ' WHERE ' + ' OR '.join(where)

    
    return [
        Player(
            '%s %s' % (first_name, last_name),
            opta_id=opta_id,
            id=id_
        ) for id_, first_name, last_name, opta_id
          in execute(sql, args)
    ]
