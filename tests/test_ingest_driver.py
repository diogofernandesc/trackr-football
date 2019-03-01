import unittest
import json
from ingest_engine.football_data import FootballData
from ingest_engine.ingest_driver import Driver, str_comparator
from ingest_engine.cons import Competition, Match, Team, Player, FootballDataApiFilters as fda
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
