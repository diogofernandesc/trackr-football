import os

from sqlalchemy import create_engine

from db_engine.db_interface import DBInterface
from db_engine.db_driver import Match
from ingest_engine.ingest_driver import Driver
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class WeeklyIngest(object):

    def __init__(self, db):
        self.db_interface = DBInterface(db=db)
        self.api_ingest = Driver()
        self.logger = logging.getLogger(__name__)

    def ingest_standings(self):
        standings = self.api_ingest.request_standings(competition_id=2021)
        latest_game_week = standings['standings'][0]['match_day']
        update = self.db_interface.update_standings(match_day=latest_game_week, record=standings)
        if update:
            self.logger.info('Standings - updated successfully')

        else:
            self.logger.info('Standings - nothing to update')

    def ingest_matches(self):
        season = '2019-2020'
        comp_fd_id = 2021
        comp_fls_id = 2
        latest_game_week = self.db_interface.get_last_game_week(table=Match)
        if latest_game_week < 38:
            latest_game_week += 1

        matches = self.api_ingest.request_match(fls_comp_id=comp_fls_id,
                                                fd_comp_id=comp_fd_id,
                                                game_week=latest_game_week,
                                                season=season,
                                                limit=None
                                                )
        self.db_interface.insert_match(record=matches)
        self.logger.info('Matches - Insert requested')

    def ingest_players(self):
        for f_id in list(range(1, 21)):
            players = self.api_ingest.request_player_details(f_team_id=f_id)
            self.db_interface.insert_player(record=players)

        self.logger.info('Players - Insert requested')


if __name__ == "__main__":

    db = create_engine(os.getenv('POSTGRES_CREDS'))
    ingest = WeeklyIngest(db=db)
    ingest.ingest_standings()
    ingest.ingest_matches()
    ingest.ingest_players()
