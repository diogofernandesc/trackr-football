import flask
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from ingest_engine.cons import Competition as COMPETITION, Team as TEAM
from api_engine.api_cons import API_ENDPOINTS, API, ENDPOINT_DESCRIPTION, API_ERROR
from db_engine.db_interface import DBInterface
from db_engine.db_filters import TeamFilters, StandingsFilters
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

    id_ = get_vals(request.args.get(COMPETITION.ID, None), int)
    name = get_vals(request.args.get(COMPETITION.NAME, None), str)
    code = get_vals(request.args.get(COMPETITION.CODE, None), str)
    location = get_vals(request.args.get(COMPETITION.LOCATION, None), str)
    fd_api_id = get_vals(request.args.get(COMPETITION.FOOTBALL_DATA_API_ID, None), int)
    fls_api_id = get_vals(request.args.get(COMPETITION.FASTEST_LIVE_SCORES_API_ID, None), int)

    result = jsonify(db_interface.get_competition(multi=multi,
                                                  id_=id_,
                                                  name=name,
                                                  code=code,
                                                  location=location,
                                                  fd_api_id=fd_api_id,
                                                  fls_api_id=fls_api_id))

    if result.json:
        return result

    else:
        raise InvalidUsage('There is no competition with those filters', status_code=404)


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
    return jsonify(db_interface.get_team(multi=multi, filters=team_filters))
    # team_filters1 = {**team_filters._asdict()}
    # db_interface.get_team(multi=multi, filters=**team_filters)
    # result = jsonify()
    # print(ra)


@app.route('/v1/ip/<string:ip>', methods=['GET'])
def ip_lol(ip):
    return jsonify({"ip": ip})


@app.route('/v1/standings/all', methods=['GET'])
@app.route('/v1/standings', methods=['GET'])
def standings():
    """
    /v1/standings/all OR type querying across ALL available standings
    /v1/standings AND querying on standings, multiple values allowed per field
    :return: API request JSON format
    """
    rule_ = request.url_rule.rule
    multi = 'standings/all' in request.url_rule.rule
    ra = request.args
    standings_filters = StandingsFilters(**{k: get_vals_(v) for k, v in ra.items()})
    return jsonify(db_interface.get_standings(multi=multi, filters=standings_filters))






if __name__ == '__main__':
    app.run()



