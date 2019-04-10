import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db_engine.db_driver import Player
import os

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
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

    def get_player(self, fls_api_id=None, fd_api_id=None, name=None):
        """
        Query DB for player record
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


if __name__ == "__main__":
    qe = QueryEngine()
    qe.get_player(fls_api_id=18866, name="Aubameyang")