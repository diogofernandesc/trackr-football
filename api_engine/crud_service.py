from threading import Thread

from flask import Blueprint, request, jsonify, current_app

from db_engine.db_driver import Competition, Standings, StandingsEntry
from db_engine.db_filters import StandingsBaseFilters, CompFilters, TeamFilters
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


@crud_service.route('/competition', methods=['GET'])
def get_competition_and_standings():
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    competitions = api_ingest.request_competitions()
    for comp in competitions:
        if comp[COMPETITION.FOOTBALL_DATA_API_ID] == 2021:  # Premier league data only
            comp_query = db_interface.db.session \
                        .query(Competition) \
                        .filter(Competition.code == comp[COMPETITION.CODE])
            if not comp_query.count():
                db_comp = Competition(**comp)
                if comp[COMPETITION.FOOTBALL_DATA_API_ID] == 2021:  # Premier league data only
                    standings = api_ingest.request_standings(competition_id=comp[COMPETITION.FOOTBALL_DATA_API_ID])
                    if standings:
                        for stan in standings['standings']:
                            table = stan.pop(STANDINGS.TABLE, [])
                            stan_query = db_interface.db.session \
                                .query(Standings) \
                                .filter(Standings.match_day == stan[STANDINGS.MATCH_DAY])

                            if not stan_query.count():
                                db_standing = Standings(**stan)

                                for entry in table:
                                    se = StandingsEntry(**entry)
                                    db_standing.standings_entries.append(se)

                                db_comp.standings.append(db_standing)

                        db_interface.db.session.add(db_comp)
                        db_interface.db.session.commit()
                        return jsonify({"Message": "Update successful"})

    return jsonify({"Message": "Nothing to update"})


@crud_service.route('/update/standings', methods=['GET'])
def get_standings():
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    ra = request.args
    try:
        if STANDINGS.MATCH_DAY not in ra:
            raise FilterException

        match_day = int(ra[STANDINGS.MATCH_DAY])

    except (FilterException, ValueError):
        raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)

    standings = api_ingest.request_standings(competition_id=2021)
    update = db_interface.update_standings(match_day=match_day, record=standings)
    if not update:
        return jsonify({"Message": "Nothing to update"})

    return jsonify({"Message": "Update successful"})


@crud_service.route('/players', methods=['GET'])
@crud_service.route('/player', methods=['GET'])
@crud_service.route('/player/all', methods=['GET'])
def get_player() -> dict:
    """
    CRUD endpoint for inserting players into DB
    :return: Result that is also inserted into DB
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    ra = request.args
    limit = ra.get("limit", 20)
    multi = 'player/all' in request.url_rule.rule
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
        if PLAYER.FANTASY_TEAM_ID not in ra and not multi:
            raise FilterException
        if not multi:
            f_team_id = int(ra[PLAYER.FANTASY_TEAM_ID])

    except (FilterException, ValueError):
        raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)

    # Retrieve the player's team
    if not multi:
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

    if multi:
        players = []
        for f_id in list(range(1, 21)):
            players += api_ingest.request_player_details(f_team_id=f_id)
    else:
        players = api_ingest.request_player_details(f_team_id=f_team_id)

    # Inserts record into the database in parallel
    thread = Thread(target=lambda record: db_interface.insert_player(record), kwargs={'record': players})
    thread.start()
    thread.join()

    if players:
        return jsonify(players)

    else:
        raise InvalidUsage(API_ERROR.PLAYER_404, status_code=404)


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

