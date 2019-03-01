import unittest
import json
from ingest_engine.football_data import FootballData
from ingest_engine.ingest_driver import Driver, str_comparator
from ingest_engine.cons import Competition, Match, Team, Player, FootballDataApiFilters as fdf
from ingest_engine.cons import FLSApiFilters as flsf
from ingest_engine.fantasy_api import team_mapper
import os


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.driver = Driver()

    def tearDown(self):
        pass

    def testStringComparator(self):
        hello1 = "Hello"
        hello2 = "Hello"
        self.assertTrue(str_comparator(hello1, hello2) == 1)
        champions_league1 = "Champions League"
        champions_league2 = "UEFA Champions League"
        self.assertTrue(str_comparator(champions_league1, champions_league2) >= 0.9)
        random_word1 = "altogether"
        random_word2 = "nevermind"
        self.assertTrue(str_comparator(random_word1, random_word2) <= 0.5)

    def testRequestCompetitions(self):
        competitions = self.driver.request_competitions()
        for comp in competitions:
            self.assertTrue(all(k in comp for k in (Competition.NAME,
                                                    Competition.CODE,
                                                    Competition.LOCATION,
                                                    Competition.FOOTBALL_DATA_API_ID,
                                                    Competition.FASTEST_LIVE_SCORES_API_ID)))

    def testRequestMatch(self):
        # In FLS, 2 is id for premier league, 2021 in football-data
        fls_comp_id = 2
        fd_comp_id = 2021
        game_week = 1
        season = 2018
        final_matches_result = self.driver.request_match(competition_name="test", game_week=game_week, season=season)
        fantasy_matches = self.driver.fantasy.request_matches()
        fd_matches = self.driver.fd.request_competition_match(competition_id=fd_comp_id,
                                                       **{fdf.MATCHDAY: game_week, fdf.SEASON: season})
        game_week_start = f'{fd_matches[0][Match.MATCH_UTC_DATE].split("T")[0]}T00:00:00'
        fls_matches = self.driver.fls.request_matches(**{flsf.COMPETITION_ID: fls_comp_id,
                                                         flsf.FROM_DATETIME: game_week_start})

        for match in final_matches_result:
            for fls_match in fls_matches:
                if fls_match[Match.HOME_TEAM] in match[Match.HOME_TEAM] and \
                    fls_match[Match.AWAY_TEAM] in match[Match.AWAY_TEAM] and \
                        match[Match.FULL_TIME_HOME_SCORE] == fls_match[Match.FULL_TIME_HOME_SCORE] and \
                        match[Match.FULL_TIME_AWAY_SCORE] == fls_match[Match.FULL_TIME_AWAY_SCORE]:
                    self.assertEqual(fls_match[Match.FLS_MATCH_ID], match[Match.FLS_MATCH_ID])

                self.assertTrue(all(k in match for k in fls_match))

            for f_match in fantasy_matches:
                f_home_team = team_mapper(f_match[Match.FANTASY_HOME_TEAM_ID])
                f_away_team = team_mapper(f_match[Match.FANTASY_AWAY_TEAM_ID])
                if f_match[Match.START_TIME] == match[Match.MATCH_UTC_DATE]:
                    if f_home_team in match[Match.HOME_TEAM] and f_away_team in match[Match.AWAY_TEAM] and \
                            match[Match.FULL_TIME_HOME_SCORE] == f_match[Match.FULL_TIME_HOME_SCORE] and \
                            match[Match.FULL_TIME_AWAY_SCORE] == f_match[Match.FULL_TIME_AWAY_SCORE]:
                        self.assertEqual(f_match[Match.FANTASY_MATCH_CODE], match[Match.FANTASY_MATCH_CODE])

                self.assertTrue(all(k in match for k in f_match))

            self.assertTrue(all(k in match for k in [Match.FOOTBALL_DATA_ID,
                                                     Match.SEASON_START_DATE,
                                                     Match.SEASON_END_DATE,
                                                     Match.MATCH_UTC_DATE,
                                                     Match.STATUS,
                                                     Match.MATCHDAY,
                                                     Match.FULL_TIME_HOME_SCORE,
                                                     Match.FULL_TIME_AWAY_SCORE,
                                                     Match.HALF_TIME_HOME_SCORE,
                                                     Match.HALF_TIME_AWAY_SCORE,
                                                     Match.EXTRA_TIME_HOME_SCORE,
                                                     Match.EXTRA_TIME_AWAY_SCORE,
                                                     Match.PENALTY_HOME_SCORE,
                                                     Match.PENALTY_AWAY_SCORE,
                                                     Match.WINNER,
                                                     Match.HOME_TEAM,
                                                     Match.AWAY_TEAM]))



