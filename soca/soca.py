import csv

import click

import query
import parsing


class Config(object):
    def __init__(self):
        pass

pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@pass_config
def cli(config):
    pass

@cli.group(help='Search for entities (player, match, team)')
def search():
    pass

@search.command()
@click.argument('identifier')
@pass_config
def player(config, identifier):
    for player in query.get_players(identifier):
        click.echo(player)


@search.command()
@click.argument('identifier')
@pass_config
def match(config, identifier):
    for match in query.get_matches(identifier):
        click.echo(match)


@search.command()
@click.argument('identifier')
@pass_config
def team(config, identifier):
    for team in query.get_teams(identifier):
        click.echo(team)


@cli.command()
@click.argument('milliseconds', type=click.INT)
def time(milliseconds):
    m, r = divmod(milliseconds, 600)
    s, ms = divmod(r, 10)
    click.echo('%s:%02d.%s' % (m, s, ms))

@cli.group(help='Convert opta position xml file to csv')
def convert():
    pass

@convert.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def position(input, output):
    parsing.convert_positions(input, output)

@convert.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def player(input, output):
    parsing.convert_players(input, output)


# parse
@cli.group()
def parse():
    pass

@parse.command()
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
@click.option('--match')
@click.option('--10/--25', 'freq', default=True)
@click.option('--step', default=1, type=int)
def status(input, output, match, freq, step):
    freq = 10 if freq else 25
    status = parsing.BallStatus(input)

    if freq == 10:
        result = status.r10
    else:
        result = status.result

    writer = csv.writer(output)

    for period in [1, 2]:
        for n, status in enumerate(result[period]):
            time = step*n
            writer.writerow((match, period, time, status))

if __name__ == '__main__':
    cli()
