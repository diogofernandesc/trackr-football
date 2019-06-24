from threading import Thread

from flask import Blueprint, request, jsonify, current_app
from db_engine.db_filters import TeamFilters, StandingsBaseFilters, CompFilters, MatchFilters
from api_engine.api_service import get_vals, InvalidUsage
from api_engine.api_cons import API_ENDPOINTS, API, ENDPOINT_DESCRIPTION, API_ERROR
from ingest_engine.cons import IGNORE, Team as TEAM, Standings as STANDINGS, Competition as COMPETITION, Match as MATCH
from ingest_engine.ingest_driver import Driver

crud_service = Blueprint('crud_service', __name__, template_folder='templates')


api_ingest = Driver()


@crud_service.route('/v1/db/insert/match')
def insert_match():
    pass


@crud_service.route('/v1/db/match', methods=['GET'])
def get_match() -> dict:
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    ra = request.args
    season = '2018-2019'
    comp_fd_id = 2021
    comp_fls_id = 2
    db_id = 2
    match_day = None
    temp_filters = {}

    # To be used when API compatible with multiple leagues
    # try:
    #     assert COMPETITION.ID in ra
    #
    # except AssertionError:
    #     raise InvalidUsage(API_ERROR.NO_COMPETITION_400, status_code=400)

    if STANDINGS.SEASON in ra:
        season = ra[STANDINGS.SEASON]

    # temp_filters[STANDINGS.SEASON] = season
    temp_filters[STANDINGS.COMPETITION_ID] = db_id
    if MATCH.MATCHDAY not in ra:
        standings_filters = StandingsBaseFilters(**{k: get_vals(v) for k, v in temp_filters.items()})
        match_day = db_interface.get_last_game_week(filters=standings_filters)

    else:
        match_day = ra[MATCH.MATCHDAY]

    # To be used when API compatible with multiple leagues
    # comp_filters = CompFilters(**{k: get_vals(v) for k, v in ra.items()})
    # comp = db_interface.get_competition(multi=False, filters=comp_filters)
    match_filters = MatchFilters(**{k: get_vals(v) for k, v in ra.items()})
    db_matches = db_interface.get_match(multi=False, filters=match_filters)
    if db_matches:
        matches = db_matches

    else:
        matches = api_ingest.request_match(fls_comp_id=comp_fls_id,
                                           fd_comp_id=comp_fd_id,
                                           game_week=match_day,
                                           season=season
                                           )

        # Inserts record into the database in parallel
        thread = Thread(target=lambda record: db_interface.insert_match(record), kwargs={'record': matches})
        thread.start()

    if matches:
        return jsonify(matches)

    else:
        raise InvalidUsage(API_ERROR.MATCH_404, status_code=404)


