from flask import request, jsonify, Blueprint, current_app, abort
from api_engine.api_cons import API_ENDPOINTS, API, ENDPOINT_DESCRIPTION, API_ERROR
from db_engine.db_filters import TeamFilters, StandingsFilters, CompFilters, MatchFilters, PlayerFilters, StatFilters
from ingest_engine.ingest_driver import Driver
from sqlalchemy import exc
import logging

api_service = Blueprint('api_service', __name__, template_folder='templates', url_prefix='/v1', subdomain='api')
api_ingest = Driver()

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# db = SQLAlchemy(app)
# db_interface = DBInterface(db=db)
# Logging using app.logger.debug/warning/error


def get_vals(v):
    """
    Extract multiple values comma separated if they exist
    :param v: url parameter
    :param type_: type of url parameter e.g. int, str
    :return: multiple (typed) values or single
    """
    def isfloat(x):
        try:
            a = float(x)
        except ValueError:
            return False
        else:
            return True

    def isint(x):
        try:
            a = float(x)
            b = int(a)
        except ValueError:
            return False
        else:
            return a == b

    if v:
        # Perform type inference from the query string
        def type_eval(x):
            if isint(x):
                return int(x)
            elif isfloat(x):
                return float(x)
            else:
                return x

        if isinstance(v, list):
            v = v[0]

        if ',' in str(v):
            return [type_eval(val) for val in v.split(",")]

        return [type_eval(v)]

    return None


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> dict:
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@api_service.route('/')
def base():
    api_endpoints = []
    for cons, endpoint in vars(API_ENDPOINTS).items():
        if not cons.startswith('__'):
            api_endpoints.append({
                API.ENDPOINT_URL: f'/v1/{endpoint}',
                API.URL_DESCRIPTION: ENDPOINT_DESCRIPTION.get(endpoint, "")
            })

    return jsonify({
        API.ENDPOINTS: api_endpoints
    })


@api_service.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """
    Handler methods for when API calls do not work
    :param error:
    :return:
    """
    response = jsonify(**error.to_dict(), **{"status_code": error.status_code})
    response.status_code = error.status_code
    return response


@api_service.route('/competition', methods=['GET'])
@api_service.route('/competitions', methods=['GET'])
def competition():
    """
    /v1/competitions will be used to allow OR type querying across all the available competitions
    /v1/competition is AND querying on competitions but still allows multiple values to be chosen per field
    :return: API request json format
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']
    multi = 'competitions' in request.url_rule.rule
    ra = request.args
    comp_filters = CompFilters(**{k: get_vals(v) for k, v in ra.items()})
    result = jsonify(db_interface.get_competition(multi=multi, filters=comp_filters))

    if result.json:
        return result
    #
    else:
        raise InvalidUsage(API_ERROR.COMPETITION_404, status_code=404)


@api_service.route('/team/all', methods=['GET'])
@api_service.route('/team', methods=['GET'])
def team():
    """
    /v1/team/all will be used to allow OR type querying across all the available teams
    /v1/team is AND querying on competitions but still allows multiple values to be chosen per field
    :return: API request json format
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']
    multi = 'team/all' in request.url_rule.rule
    ra = request.args
    limit = ra.get("limit", 10)
    result = {}
    try:
        limit = int(limit)
    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    try:
        team_filters = TeamFilters(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
        result = jsonify(db_interface.get_team(limit=limit, multi=multi, filters=team_filters))

    except exc.DataError as e:
        if "invalid input syntax" in e.args[0]:  # e.args[0] is the psycopg2 errors text field
            raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)
        else:
            abort(400)

    except TypeError:
        raise InvalidUsage(API_ERROR.RESOURCE_NOT_FOUND_404, status_code=404)

    if result.json:
        return result

    else:
        raise InvalidUsage(API_ERROR.TEAM_404, status_code=404)


@api_service.route('/standings/all', methods=['GET'])
@api_service.route('/standings', methods=['GET'])
def standings():
    """
    /v1/standings/all OR type querying across ALL available standings
    /v1/standings AND querying on standings, multiple values allowed per field
    :return: API request JSON format
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']
    multi = 'standings/all' in request.url_rule.rule
    ra = request.args
    limit = ra.get("limit", 10)
    result = {}
    try:
        limit = int(limit)
    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    try:
        standings_filters = StandingsFilters(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
        result = jsonify(db_interface.get_standings(limit=limit, multi=multi, filters=standings_filters))

    except exc.DataError as e:
        if "invalid input syntax" in e.args[0]:  # e.args[0] is the psycopg2 errors text field
            raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)
        else:
            abort(400)

    except TypeError:
        raise InvalidUsage(API_ERROR.RESOURCE_NOT_FOUND_404, status_code=404)

    if result.json:
        return result

    else:
        raise InvalidUsage(API_ERROR.STANDINGS_404, status_code=404)


@api_service.route('/match/all', methods=['GET'])
@api_service.route('/match', methods=['GET'])
def match():
    """
    /v1/match/all OR type querying across ALL available matches
    /v1/match AND querying on matches
    :return: Match data as JSON (if available)
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    multi = 'match/all' in request.url_rule.rule
    ra = request.args
    limit = ra.get("limit", 10)
    result = {}
    try:
        limit = int(limit)
        match_filters = Matc(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
        result = jsonify(db_interface.get_match(limit=limit, multi=multi, filters=match_filters))

    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    except exc.DataError as e:
        if "invalid input syntax" in e.args[0]:  # e.args[0] is the psycopg2 errors text field
            raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)
        else:
            abort(400)

    except TypeError:
        raise InvalidUsage(API_ERROR.RESOURCE_NOT_FOUND_404, status_code=404)

    if result.json:
        return result

    else:
        raise InvalidUsage(API_ERROR.MATCH_404, status_code=404)

@api_service.route('/stats', methods=['GET'])
def stats():
    """
    Returns match stats for a specific player or match
    :return: Match stat data as JSON (if available)
    """
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    ra = request.args
    limit = ra.get("limit", 10)
    result = {}
    try:
        limit = int(limit)
        match_filters = StatFilters(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
        result = jsonify(db_interface.get_stats(limit=limit, filters=match_filters))

    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    except exc.DataError as e:
        if "invalid input syntax" in e.args[0]:  # e.args[0] is the psycopg2 errors text field
            raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)
        else:
            abort(400)

    except TypeError:
        raise InvalidUsage(API_ERROR.RESOURCE_NOT_FOUND_404, status_code=404)

    if result.json:
        return result

    else:
        raise InvalidUsage(API_ERROR.MATCH_404, status_code=404)




@api_service.route('/player/all', methods=['GET'])
@api_service.route('player', methods=['GET'])
def player():
    """
    /v1/player/all OR type querying across ALL available player info
    /v1/player AND querying on players
    :return: Player data as JSON (if available)
    """
    result = {}
    with current_app.app_context():
        db_interface = current_app.config['db_interface']

    multi = 'player/all' in request.url_rule.rule
    ra = request.args
    if not ra:
        raise InvalidUsage(API_ERROR.MISSING_FILTER_400, status_code=400)
    limit = ra.get("limit", 10)
    try:
        limit = int(limit)
        player_filters = PlayerFilters(**{k: get_vals(v) for k, v in ra.items() if k != "limit"})
        result = db_interface.get_player(limit=limit, multi=multi, filters=player_filters)
        if isinstance(result, dict):
            result.pop('matches')
        elif isinstance(result, list):
            for player_ in result:
                player_.pop('matches')
        result = jsonify(result)

    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    except exc.DataError as e:
        if "invalid input syntax" in e.args[0]:  # e.args[0] is the psycopg2 errors text field
            raise InvalidUsage(API_ERROR.FILTER_PROBLEM_400, status_code=400)
        else:
            abort(400)

    except TypeError as e:
        logging.error(e)
        raise InvalidUsage(API_ERROR.RESOURCE_NOT_FOUND_404, status_code=404)

    if result.json:
        return result

    else:
        raise InvalidUsage(API_ERROR.PLAYER_404, status_code=404)

















