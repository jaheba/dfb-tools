

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
    config.foo = 'bar'

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

@cli.command(help='Convert opta position xml file to csv')
@click.argument('input', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def convert(input, output):
    parsing.convert(input, output)

if __name__ == '__main__':
    cli()
