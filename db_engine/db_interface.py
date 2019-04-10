# from ingest_engine.ingest_driver import Driver, str_comparator
# from ingest_engine.cons import Player as PLAYER
# import logging
from functools import wraps

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ingest_engine.cons import IGNORE
from db_engine.db_driver import Player, Competition, Standings
import os
import click

# logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
# driver = Driver()
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
# db = SQLAlchemy(app)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def clean_output(query_res):
    """
    Ensure only the right fields come out following a DB query
    :param query_res: the query result to be clean
    :return:
    """
    result = []
    for res in query_res:
        final_res = res.__dict__
        if IGNORE.INSTANCE_STATE in final_res:
            final_res.pop(IGNORE.INSTANCE_STATE, None)

        result.append(final_res)

    return result


@click.group()
def db_cli():
    pass


@click.command()
@click.option('--id', default=None, help='DB ID of player record')
@click.option('--fls_api_id', default=None, help='FLS API ID for player record')
@click.option('--fd_api_id', default=None, help='FD API ID for player record')
@click.option('--name', default=None, help='Name of player used for SQL LIKE search')
def get_player(id=None, fls_api_id=None, fd_api_id=None, name=None):
    """
    Query DB for player record
    :param id: DB ID of player
    :param fls_api_id: fastestlivescores API id for player
    :param fd_api_id: football-data.org API id for player
    :param name: name of player used for SQL LIKE search
    :return: matched (if any) player records
    """

    player_query = Player.query

    if id:
        player_query = player_query.filter_by(id=id)

    if fls_api_id:
        player_query = player_query.filter_by(fls_api_id=fls_api_id)

    if fd_api_id:
        player_query = player_query.filter_by(fd_api_id=fd_api_id)

    if name:
        player_query = player_query.filter(Player.name.like(f"%{name}%"))

    player_query = player_query.all()
    return clean_output(player_query)


@click.command()
@click.option('--name', default=None, help='Name of competition used for SQL LIKE search')
@click.option('--id', default=None, help='DB ID of competition')
@click.option('--code', default=None, help='The code of the competion')
@click.option('--location', default=None, help='Country/location of the competition')
@click.option('--fd_api_id', default=None, help='Football data API ID for competition')
@click.option('--fls_api_id', default=None, help='FastestLiveScores API ID')
def get_competition(id=None, name=None, code=None, location=None, fd_api_id=None, fls_api_id=None):
    """
    Query DB for competition record
    :param id: DB ID of competition
    :param name: The name of the competition, LIKE match performed
    :param code: The code of the competition
    :param location: Country/Location of the competition
    :param fd_api_id: Football data API id for competition
    :param fls_api_id: FastestLiveScores API id for competition
    :return:  matched (if any) competition records
    """
    comp_query = Competition.query

    if id:
        comp_query = comp_query.filter_by(id=id)

    if name:
        comp_query = comp_query.filter(Competition.name.like(f"%{name}%"))

    if code:
        comp_query = comp_query.filter_by(code=code)

    if location:
        comp_query = comp_query.filter_by(location=location)

    if fd_api_id:
        comp_query = comp_query.filter_by(football_data_api_id=fd_api_id)

    if fls_api_id:
        comp_query = comp_query.filter_by(fls_api_id=fls_api_id)

    query_result = comp_query.all()
    clean_output(query_result)


@click.command()
@click.option('--id', default=None, help='DB ID of competition')
@click.option('--competition_id', default=None, help='Competition id for which to retrieve standings')
@click.option('--type', default=None, help='The type of standing e.g. TOTAL | HOME | AWAY')
@click.option('--season', default=None, help='Str season representer for the year of the standings e.g. 2018/19')
@click.option('--match_day', default=None, help='The match day value the standing belongs to')
def get_standings(id=None, competition_id=None, type=None, season=None, match_day=None):
    """
    Query DB for standings records
    :param id: DB ID of standings
    :param competition_id: The ID of the competition for corresponding standings
    :param type: Type of standing -> TOTAL | HOME | AWAY
    :param season: Str season for which the standings belong -> e.g. "2018/2019"
    :param match_day: int value of the matchday for the standings
    :return: matched (if any) standings records
    """
    stan_query = Standings.query
    if id:
        stan_query = stan_query.filter_by(id=id)

    if competition_id:
        stan_query = stan_query.filter_by(competition_id=competition_id)

    if type:
        stan_query = stan_query.filter_by(type=type)

    if season:
        stan_query = stan_query.filter_by(season=season)

    if match_day:
        stan_query = stan_query.filter_by(match_day=match_day)

    stan_query = stan_query.all()
    clean_output(stan_query)


if __name__ == "__main__":
    # qe = QueryEngine()
    # db_cli.add_command(QueryEngine.get_player)
    db_cli.add_command(get_competition)
    db_cli.add_command(get_standings)
    db_cli()
    # qe.get_player(fls_api_id=18866, name="Aubameyang")