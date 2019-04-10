# from ingest_engine.ingest_driver import Driver, str_comparator
# from ingest_engine.cons import Player as PLAYER
# import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ingest_engine.cons import IGNORE
from db_engine.db_driver import Player, Competition
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
    return [r.__dict__ for r in player_query]


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

    comp_query = comp_query.all()
    result = []
    for res in comp_query:
        final_res = res.__dict__
        if IGNORE.INSTANCE_STATE in final_res:
            final_res.pop(IGNORE.INSTANCE_STATE, None)

        result.append(final_res)

    print(result)
    # return [r.__dict__ for r in comp_query]


if __name__ == "__main__":
    # qe = QueryEngine()
    # db_cli.add_command(QueryEngine.get_player)
    db_cli.add_command(get_competition)
    db_cli()
    # qe.get_player(fls_api_id=18866, name="Aubameyang")