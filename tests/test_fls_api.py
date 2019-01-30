import unittest
import json
from time import sleep
from ingest_engine.cons import Team
from ingest_engine.fastest_live_scores_api import FastestLiveScores
from ingest_engine.cons import Competition, Match, Team, Player, FootballDataApiFilters as fda


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.fls = FastestLiveScores()
        self.test_fls = FastestLiveScores(api_key='test')

    def tearDown(self):
        self.fls.session.close()
        self.test_fls.session.close()

    def testCompetitionEndPoint(self):
        comps = self.fls.request_competitions()
        self.assertTrue(len(comps) > 0)
        self.assertEqual(self.test_fls.request_competitions(), [])

    def testTeamsEndpoint(self):
        teams = self.fls.request_teams()
        self.assertTrue(len(teams) > 0)
        for team in teams:
            self.assertTrue(Team.FASTEST_LIVE_SCORES_API_ID in team)
            self.assertTrue(Team.NAME in team)
            if Team.STADIUM_CAPACITY in team:
                self.assertTrue(team[Team.STADIUM_CAPACITY] > 0)

            if Team.STADIUM_LONG in team:
                self.assertTrue(-180 <= team[Team.STADIUM_LONG] <= 180)

            if Team.STADIUM_LAT in team:
                self.assertTrue(-90 <= team[Team.STADIUM_LAT] <= 90)

    def testMatchesEndpoint(self):
        matches = self.fls.request_matches()
        self.assertTrue(len(matches) > 0)
        self.assertEqual(self.test_fls.request_matches(), [])


