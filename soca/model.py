
import click

class Player(object):
    def __init__(self, name, opta_id, id):
        self.name = name
        self.opta = opta_id
        self.id = id

    def __str__(self):
        return u'''{player}: {name}
Opta: {opta}
id: {id}'''.format(
            player=click.style('Player', bold=True, fg='green'),
            name=self.name,
            opta=self.opta,
            id=self.id
        )


class Match(object):
    def __init__(self, id, date, competition, height, width, opta_id, home=None, guest=None):
        self.id = id
        self.date = date
        self.competition = competition
        self.height = height
        self.width = width
        self.opta_id = opta_id
        self.home = home
        self.guest = guest

    def __str__(self):
        return u'''{match}: {home} vs {guest}
Opta: {opta}
Id: {id}
Video: {video}'''.format(
            match=click.style('Match', fg='red'),
            home=click.style(self.home.name, bold=True),
            guest=click.style(self.guest.name, bold=True),
            opta=self.opta_id,
            id=self.id,
            video=int(self.opta_id.split('-')[-1], 36)
        )

class Team(object):
    def __init__(self, id, name, code, opta_id):
        self.id = id
        self.name = name
        self.code = code
        self.opta_id = opta_id

    def __str__(self):
        return u'''{team}: {name} ({code})
Opta: {opta}
id: {id}'''.format(
            team=click.style('Team', bold=True, fg='yellow'),
            name=self.name,
            opta=self.opta_id,
            code=self.code,
            id=self.id
        )
