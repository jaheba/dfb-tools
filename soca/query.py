
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


class SQL(object):
    def __init__(self, sql, schema=config.schema):
        self.sql = sql.format(schema=schema)
        self.schema = schema
        self.where = []
        self.args = []
        self.opta_id = None

    def check_opta_id(self, query):
        if OPTA_RE.match(query):
            self.opta_id = query
            self.where.append(r'OPTA_ID = ?')
            self.args.append(query)

    def check_id(self, query):
        if query.isdigit():
            self.where.append(r'ID = ?')
            self.args.append(int(query))

    def check_name(self, query, column):
        if query and not any(char.isdigit() for char in query):
            self.where.append(
                r"UPPER({column}) LIKE '%'|| UPPER(?) || '%' ESCAPE '\'".format(column=column)
            )
            self.args.append(
                query
                .replace('%', r'\%')
                .replace('_', r'\_')
                .replace('\\', r'\\')
            )

    def check_opta_wildcard(self, query, classififer):
        if query.isalnum() and len(query) >= 2:
            self.where.append(
                r"OPTA_ID LIKE 'DFL-{classififer}-%' || UPPER(?)".format(classififer=classififer)
            )
            self.args.append(query)

    def execute(self):
        sql = self.sql
        if self.where:
            sql += ' WHERE ' + ' OR '.join(self.where)
        return execute(sql, self.args)


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

    sql = SQL('''SELECT ID, NAME, CODE, OPTA_ID
        FROM {schema}.TEAM
    ''')

    sql.check_opta_id(query)

    if not sql.opta_id:
        sql.check_id(query)
        sql.check_name(query, 'NAME')
        sql.check_opta_wildcard(query, 'CLU')

    return map(lambda row: Team(*row), sql.execute())


def get_matches(query):
    query = query.strip()

    sql = SQL('''SELECT ID, DATE, COMPETITION, PITCH_HEIGHT, PITCH_WIDTH, OPTA_ID
        FROM {schema}.MATCH''')

    sql.check_opta_id(query)

    if not sql.opta_id:
        sql.check_id(query)
        sql.check_opta_wildcard(query, 'MAT')

    matches = []
    for id_, date, competition, height, width, opta_id in sql.execute():
        home, guest = _get_teams_of_match(id_)
        matches.append(Match(
            id_, date, competition, height, width, opta_id,
            home=home,
            guest=guest,
        ))

    return matches


def get_players(query):
    query = query.strip()

    sql = SQL('''SELECT ID, FIRST_NAME, LAST_NAME, OPTA_ID
        FROM {schema}.PLAYER''')

    sql.check_opta_id(query)

    if not sql.opta_id:
        sql.check_id(query)
        sql.check_name(query, 'FIRST_NAME')
        sql.check_name(query, 'LAST_NAME')
        sql.check_opta_wildcard(query, 'OBJ')

    return [
        Player(
            '%s %s' % (first_name, last_name),
            opta_id=opta_id,
            id=id_
        )
        for id_, first_name, last_name, opta_id
        in sql.execute()
    ]
