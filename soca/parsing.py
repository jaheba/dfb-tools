
import csv
from lxml import etree

def convert_id(opta_id):
    'DFL-OBJ-0000XT'
    suffix = opta_id.split('-')[-1]
    return int(suffix, 36)


def player_id(elem):
    if team_id(elem) == 0:
        return 0

    player = elem.get('PersonId') or elem.get('Object')

    return convert_id(player)

def team_id(elem):
    team = elem.get('TeamId') or elem.get('Club')
    if team.lower() == 'ball':
        return 0
    return convert_id(team)

def convert_positions(infile, outfile):
    pos_writer = csv.writer(outfile)

    context = etree.iterparse(infile)

    for _, elem in context:
        if elem.tag == 'FrameSet':
            # print elem.attrib
            player = player_id(elem)
            team = team_id(elem)
            
            match = convert_id(elem.get('MatchId') or elem.get('Match'))
            period = 1+ (elem.get('GameSection') == 'secondHalf')

            for n, frame in enumerate(elem):
                #to centi seconds (1/100 s)
                time = n*4
                x = frame.get('X')
                y = frame.get('Y')

                #last 0 for velocity
                pos_writer.writerow([match, period, time, player, team, x, y, 0])

            elem.clear()

def convert_players(infile, outfile):
    player_writer = csv.writer(outfile)
    context = etree.iterparse(infile)

    for _, elem in context:
        if elem.tag == 'Object':
            opta_id = convert_id(elem.get('ObjectId'))
            first_name = elem.get('FirstName').encode('utf-8')
            last_name = elem.get('LastName').encode('utf-8')
            shirt = elem.get('ShirtNumber')
            club = convert_id(elem.get('ClubId'))

            player_writer.writerow([opta_id, club, first_name, last_name, shirt])
