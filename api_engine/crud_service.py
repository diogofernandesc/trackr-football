from threading import Thread

from flask import Blueprint, request, jsonify, current_app
from db_engine.db_filters import StandingsBaseFilters, CompFilters, MatchFilters, TeamFilters
from api_engine.api_service import get_vals, InvalidUsage
from api_engine.api_cons import API_ERROR
from ingest_engine.cons import  Standings as STANDINGS, Competition as COMPETITION, Match as MATCH, Player as PLAYER\
    , Team as TEAM
from ingest_engine.ingest_driver import Driver

crud_service = Blueprint('crud_service', __name__, template_folder='templates', url_prefix='/v1/db', subdomain='api')
api_ingest = Driver()

class FilterException(Exception):
   """Raised when filter applied is incorrect"""
   pass


@crud_service.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    Handler methods for when API calls do not work
    :param error:
    :return:
    """
    response = jsonify(**error.to_dict(), **{"status_code": error.status_code})
    response.status_code = error.status_code
    return response


@crud_service.route('/standings')
def get_standings():
    pass


@crud_service.route('/matches', methods=['GET'])
@crud_service.route('/match', methods=['GET'])
def get_match() -> dict:
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    multi = 'matches' in request.url_rule.rule
    ra = request.args
    limit = ra.get("limit", 10)
    try:
        limit = int(limit)
    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    season = '2019-2020'
    comp_fd_id = 2021
    comp_fls_id = 2
    temp_filters = {}

    # Get premier league db_id
    comp_filters = CompFilters(**{k: get_vals(v) for k, v in {COMPETITION.NAME: "Premier League"}.items()})
    comp = db_interface.get_competition(filters=comp_filters)
    if comp:
        db_id = comp[COMPETITION.ID]

    else:
        raise InvalidUsage(API_ERROR.MISSING_COMPETITION_404, status_code=404)

    if STANDINGS.SEASON in ra:
        season = ra[STANDINGS.SEASON]

    temp_filters[STANDINGS.COMPETITION_ID] = db_id

    if MATCH.MATCHDAY not in ra:
        standings_filters = StandingsBaseFilters(**{k: get_vals(v) for k, v in temp_filters.items()})
        match_day = db_interface.get_last_game_week(filters=standings_filters)

    else:
        match_day = ra[MATCH.MATCHDAY]

    # To be used when API compatible with multiple leagues
    # comp_filters = CompFilters(**{k: get_vals(v) for k, v in ra.items()})
    # comp = db_interface.get_competition(multi=False, filters=comp_filters)
    match_filters = MatchFilters(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
    db_matches = db_interface.get_match(limit=limit, multi=False, filters=match_filters)
    if db_matches:
        matches = db_matches

    else:
        if not multi and MATCH.ID in ra:
            raise InvalidUsage(API_ERROR.MATCH_404, status_code=404)

        matches = api_ingest.request_match(fls_comp_id=comp_fls_id,
                                           fd_comp_id=comp_fd_id,
                                           game_week=match_day,
                                           season=season,
                                           limit=limit
                                           )

        # Inserts record into the database in parallel
        thread = Thread(target=lambda record: db_interface.insert_match(record), kwargs={'record': matches})
        thread.start()
        thread.join()

    if matches:
        return jsonify(matches)

    else:
        raise InvalidUsage(API_ERROR.MATCH_404, status_code=404)


@crud_service.route('/teams', methods=['GET'])
@crud_service.route('/team', methods=['GET'])
def get_team() -> dict:
    """
    CRUD endpoint for inserting teams into DB
    :return: Result that is also inserted into DB
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    multi = 'teams' in request.url_rule.rule
    ra = request.args
    limit = ra.get("limit", 20)
    try:
        limit = int(limit)
    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    season = '2019-2020'
    comp_fd_id = 2021
    comp_fls_id = 2

    team_filters = TeamFilters(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
    db_teams = db_interface.get_team(limit=limit, multi=multi, filters=team_filters)

    if db_teams:
        teams = db_teams

    else:

        teams = api_ingest.request_teams(fd_comp_id=comp_fd_id, fls_comp_id=comp_fls_id, season=season, limit=limit)

        # Inserts record into the database in parallel
        thread = Thread(target=lambda record: db_interface.insert_team(record), kwargs={'record': teams})
        thread.start()
        thread.join()

    if teams:
        return jsonify(teams)

    else:
        raise InvalidUsage(API_ERROR.TEAM_404, status_code=404)


@crud_service.route('/players', methods=['GET'])
@crud_service.route('/player', methods=['GET'])
def get_player() -> dict:
    """
    CRUD endpoint for inserting players into DB
    :return: Result that is also inserted into DB
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    ra = request.args
    limit = ra.get("limit", 20)
    try:
        limit = int(limit)
    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    # season = '2019-2020'
    # comp_fd_id = 2021
    # comp_fls_id = 2
    #
    # # player_fd_id = None
    # team_fls_id = None
    try:
        if PLAYER.FANTASY_TEAM_ID not in ra:
            raise FilterException
        f_team_id = int(ra[PLAYER.FANTASY_TEAM_ID])

    except (FilterException, ValueError):
        raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)

    # Retrieve the player's team
    temp_filters = {TEAM.FANTASY_ID: f_team_id}
    team_filters = TeamFilters(**{k: get_vals(v) for k, v in temp_filters.items() if k != "limit"})
    player_team = db_interface.get_team(limit=1, multi=False, filters=team_filters)
    if not player_team:
        raise InvalidUsage(API_ERROR.TEAM_404, status_code=404)

    # player_filters = PlayerCrudFilters(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
    # db_players = db_interface.get_player(limit=limit, multi=multi, filters=player_filters)

    # if db_players:
    #     players = db_players

    # else:
    players = api_ingest.request_player_details(f_team_id=f_team_id)

    # Inserts record into the database in parallel
    thread = Thread(target=lambda record: db_interface.insert_player(record), kwargs={'record': players})
    thread.start()
    thread.join()

    if players:
        return jsonify(players)

    else:
        raise InvalidUsage(API_ERROR.PLAYER_404, status_code=404)

