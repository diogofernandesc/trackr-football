from db_engine.db_driver import Player, Team, Competition, Standings, StandingsEntry
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from ingest_engine.cons import IGNORE
import os

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)


def to_json(result_map):
    dict_result = {}
    for k, v in result_map.items():
        dict_result = k.__dict__
        dict_result.pop(IGNORE.INSTANCE_STATE, None)
        dict_result['standings_entries'] = clean_output(v)
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

    if len(result) == 1:
        return result[0]

    return result


class DBInterface(object):

    def __init__(self, db):
        self.db = db

    def get_competition(self, id=None, name=None, code=None, location=None, fd_api_id=None, fls_api_id=None):
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
        comp_query = self.db.session.query(Competition)

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
