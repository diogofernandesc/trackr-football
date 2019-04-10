from ingest_engine.ingest_driver import Driver, str_comparator
from ingest_engine.cons import Player as PLAYER
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db_engine.db_driver import Player, Competition
import os

# logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
# driver = Driver()
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
# db = SQLAlchemy(app)


class QueryEngine(object):
    """
    Interface class for db queries
    """
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
        print(os.getenv('POSTGRES_CONNECTION_STR'))
        self.db = SQLAlchemy(self.app)

    def get_player(self, id=None, fls_api_id=None, fd_api_id=None, name=None):
        """
        Query DB for player record
        :param id: DB ID of player
        :param fls_api_id: fastestlivescores API id for player
        :param fd_api_id: football-data.org API id for player
        :param name: name of player used for SQL LIKE search
        :return: matched (if any) player records
        """

        player_query = Player.query
        if fls_api_id:
            player_query = player_query.filter_by(fls_api_id=fls_api_id)

        if fd_api_id:
            player_query = player_query.filter_by(fd_api_id=fd_api_id)

        if name:
            player_query = player_query.filter(Player.name.like(f"%{name}%"))

        player_query = player_query.all()

        return player_query

    def get_competition(self, name=None, code=None, location=None, fd_api_id=None, fls_api_id=None):
        """
        Query DB for competition record
        :param name: The name of the competition, LIKE match performed
        :param code: The code of the competition
        :param location: Country/Location of the competition
        :param fd_api_id: Football data API id for competition
        :param fls_api_id: FastestLiveScores API id for competition
        :return:  matched (if any) competition records
        """
        comp_query = Competition.query
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

        


if __name__ == "__main__":
    qe = QueryEngine()
    qe.get_player(fls_api_id=18866, name="Aubameyang")