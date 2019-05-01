# from ingest_engine.ingest_driver import Driver, str_comparator
# from ingest_engine.cons import Player as PLAYER
# import logging
from functools import wraps

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ingest_engine.cons import IGNORE
from db_engine.db_driver import Player, Team, Competition, Standings, StandingsEntry
import os
import logging
import click

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
# driver = Driver()
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
# db = SQLAlchemy(app)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def to_json(result_map):
    dict_result = {}
    for k, v in result_map.items():
        dict_result = k.__dict__
        dict_result.pop(IGNORE.INSTANCE_STATE, None)
        dict_result['standings_entries'] = clean_output(v)
        # dict_result['standings_entries'] = [se.__dict__ for se in v]
    return dict_result


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
def get_player(_id=None, fls_api_id=None, fd_api_id=None, name=None):
    """
    Query DB for player record
    :param _id: DB ID of player
    :param fls_api_id: fastestlivescores API id for player
    :param fd_api_id: football-data.org API id for player
    :param name: name of player used for SQL LIKE search
    :return: matched (if any) player records
    """

    player_query = Player.query

    if _id:
        player_query = player_query.filter_by(id=_id)

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
@click.option('--id', default=None, help='DB ID of standings')
@click.option('--competition_id', default=None, help='Competition id for which to retrieve standings')
@click.option('--type', default=None, help='The type of standing e.g. TOTAL | HOME | AWAY')
@click.option('--season', default=None, help='Str season representer for the year of the standings e.g. 2018/19')
@click.option('--match_day', default=None, help='The match day value the standing belongs to')
@click.option('--position', default=None, help='Standing position to retrieve teams for')
def get_standings(id=None, competition_id=None, type=None, season=None, match_day=None, position=None):
    """
    Query DB for standings records
    :param id: DB ID of standings
    :param competition_id: The ID of the competition for corresponding standings
    :param type: Type of standing -> TOTAL | HOME | AWAY
    :param season: Str season for which the standings belong -> e.g. "2018/2019"
    :param match_day: int value of the matchday for the standings
    :param position: Filter by the position of teams in standings e.g. 1 -> get only standings of teams in first place
    :return: matched (if any) standings records
    """
    stan_query = db.session.query(Standings, StandingsEntry)

    if id:
        stan_query = stan_query.filter(Standings.id == id)

    if competition_id:
        stan_query = stan_query.filter(Standings.competition_id == competition_id)

    if type:
        stan_query = stan_query.filter(Standings.type == type)

    if season:
        stan_query = stan_query.filter(Standings.season == season)

    if match_day:
        stan_query = stan_query.filter(Standings.match_day == match_day)

    if position:
        stan_query = stan_query.filter(StandingsEntry.position == position)

    stan_query = stan_query.all()
    standings_map = {}

    # Reformatting dict to get standings in list per comp as "standing_entries" field
    for tpl in stan_query:
        if tpl[0] not in standings_map:
            standings_map[tpl[0]] = [tpl[1]]

        else:
            standings_map[tpl[0]].append(tpl[1])

    return to_json(standings_map)
    # print(to_json(standings_map))


@click.command()
@click.option('--id', default=None, help='DB ID of team')
@click.option('--name', default=None, help='Name of team used for SQL LIKE search')
@click.option('--country', default=None, help='Country/location of the team')
@click.option('--year_founded', default=None, help='Year the team was founded in')
@click.option('--fd_api_id', default=None, help='Football data API ID for team')
@click.option('--fls_api_id', default=None, help='FastestLiveScores API ID for team')
def get_team(id=None, name=None, country=None, year_founded=None, fd_api_id=None, fls_api_id=None):
    """
    Query DB for team records
    :param id: DB team ID
    :param name: team name used for SQL LIKE search
    :param country: team country
    :param year_founded: year team founded in
    :param fd_api_id: football-data.org API ID
    :param fls_api_id: fastestlivescores API ID
    :return: matched (if any) team records
    """
    # team_query = db.session.query(Team, Player)
    team_query = db.session.query(Team)
    if id:
        team_query.filter(Team.id == id)

    if name:
        team_query.filter(Team.name == name)

    if country:
        team_query.filter(Team.country == country)

    if year_founded:
        team_query.filter(Team.year_founded == year_founded)

    if fd_api_id:
        team_query.filter(Team.fd_id == fd_api_id)

    if fls_api_id:
        team_query.filter(Team.fls_api_id == fls_api_id)

    team_query = team_query.all()
    return clean_output(team_query)


if __name__ == "__main__":
    # qe = QueryEngine()
    # db_cli.add_command(QueryEngine.get_player)
    db_cli.add_command(get_competition)
    db_cli.add_command(get_standings)
    db_cli.add_command(get_team)
    db_cli()
    # get_standings(competition_id=1, position=1)
    # qe.get_player(fls_api_id=18866, name="Aubameyang")