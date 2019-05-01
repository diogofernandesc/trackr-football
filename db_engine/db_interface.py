from db_engine.db_driver import Player, Team, Competition, Standings, StandingsEntry
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from ingest_engine.cons import IGNORE
import os

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
    comp_query = db.session.query(Competition)

    if id:
        comp_query = comp_query.filter(Competition.id == id)

    if name:
        comp_query = comp_query.filter(Competition.name.ilike(f"%{name}%"))

    if code:
        comp_query = comp_query.filter(Competition.code == code)

    if location:
        comp_query = comp_query.filter(Competition.location == location)

    if fd_api_id:
        comp_query = comp_query.filter(Competition.fd_api_id == fd_api_id)

    if fls_api_id:
        comp_query = comp_query.filter(Competition.fls_api_id == fls_api_id)

    query_result = comp_query.all()
    return clean_output(query_result)


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
    print(get_competition(name="premier league"))