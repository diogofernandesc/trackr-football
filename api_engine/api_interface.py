import flask
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from ingest_engine.cons import Competition as COMPETITION
from api_engine.api_cons import API_ENDPOINTS, API, ENDPOINT_DESCRIPTION
from db_engine.db_interface import DBInterface
import os

app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db_interface = DBInterface(db=db)
# Logging using app.logger.debug/warning/error


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


# @app.route('/v1/competitions?id=<int:id>&name=<string:name>&code=<string:code>&location=<string:location>&fd_api_id=<int:fd_api_id>&fls_api_id=<int:fls_api_id')

# def competitions(id=None, name=None, code=None, location=None, fd_api_id=None, fls_api_id=None):
@app.route('/v1/competitions', methods=['GET'])
def competitions():
    id = request.args.get(COMPETITION.ID, None, int)
    name = request.args.get(COMPETITION.NAME, None, str)
    code = request.args.get(COMPETITION.CODE, None, str)
    location = request.args.get(COMPETITION.LOCATION, None, str)
    fd_api_id = request.args.get(COMPETITION.FOOTBALL_DATA_API_ID, None, int)
    fls_api_id = request.args.get(COMPETITION.FASTEST_LIVE_SCORES_API_ID, None, int)
    return jsonify(db_interface.get_competition(id=id, name=name, code=code, location=location,
                                                fd_api_id=fd_api_id, fls_api_id=fls_api_id))


if __name__ == '__main__':
    app.run()



