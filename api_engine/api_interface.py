import flask
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from ingest_engine.cons import Competition as COMPETITION, Team as TEAM
from api_engine.api_cons import API_ENDPOINTS, API, ENDPOINT_DESCRIPTION, API_ERROR
from db_engine.db_interface import DBInterface
from db_engine.db_filters import TeamFilters, StandingsFilters, CompFilters
import os

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db_interface = DBInterface(db=db)
# Logging using app.logger.debug/warning/error


def get_vals(v, type_):
    """
    Extract multiple values comma separated if they exist
    :param v: url parameter
    :param type_: type of url parameter e.g. int, str
    :return: multiple (typed) values or single
    """
    if v:
        if ',' in v:
            return [type_(v) for v in v.split(",")]

        else:
            return [type_(v)]

    return None


def get_vals_(v):
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

        if ',' in v:
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

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.route('/v1')
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


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(**error.to_dict(), **{"status_code": error.status_code})
    response.status_code = error.status_code
    return response


@app.route('/v1/competition', methods=['GET'])
@app.route('/v1/competitions', methods=['GET'])
def competition():
    """
    /v1/competitions will be used to allow OR type querying across all the available competitions
    /v1/competition is AND querying on competitions but still allows multiple values to be chosen per field
    :return: API request json format
    """
    multi = 'competitions' in request.url_rule.rule
    ra = request.args
    comp_filters = CompFilters(**{k: get_vals_(v) for k, v in ra.items()})
    result = jsonify(db_interface.get_competition(multi=multi, filters=comp_filters))

    if result.json:
        return result
    #
    else:
        raise InvalidUsage(API_ERROR.COMPETITION_404, status_code=404)


@app.route('/v1/team', methods=['GET'])
@app.route('/v1/teams', methods=['GET'])
def team():
    """
    /v1/teams will be used to allow OR type querying across all the available teams
    /v1/team is AND querying on competitions but still allows multiple values to be chosen per field
    :return: API request json format
    """
    multi = 'teams' in request.url_rule.rule
    ra = request.args
    team_filters = TeamFilters(**{k: get_vals_(v) for k, v in ra.items()})
    result = jsonify(db_interface.get_team(multi=multi, filters=team_filters))

    if result.json:
        return result

    else:
        raise InvalidUsage(API_ERROR.TEAM_404, status_code=404)


@app.route('/v1/standings/all', methods=['GET'])
@app.route('/v1/standings', methods=['GET'])
def standings():
    """
    /v1/standings/all OR type querying across ALL available standings
    /v1/standings AND querying on standings, multiple values allowed per field
    :return: API request JSON format
    """
    multi = 'standings/all' in request.url_rule.rule
    ra = request.args
    limit = ra.get("limit", 10)
    try:
        limit = int(limit)
    except ValueError:
        raise InvalidUsage(API_ERROR.INTEGER_LIMIT_400, status_code=400)

    standings_filters = StandingsFilters(**{k: get_vals_(v) for k, v in ra.items() if k != "limit"})
    result = jsonify(db_interface.get_standings(limit=limit, multi=multi, filters=standings_filters))

    if result.json:
        return result

    else:
        raise InvalidUsage(API_ERROR.STANDINGS_404, status_code=404)


if __name__ == '__main__':
    app.run()



