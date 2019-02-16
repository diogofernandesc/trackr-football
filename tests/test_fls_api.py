import unittest
from ingest_engine.fastest_live_scores_api import FastestLiveScores
from ingest_engine.cons import Match, Team, Player


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

    def testMatchDetailsEndpoint(self):
        match_details = self.fls.request_match_details(match_id=321042)
        self.assertTrue(len(match_details) > 0)
        self.assertEqual(self.test_fls.request_match_details(match_id=321042), {})
        self.assertTrue(Match.HOME_TEAM_FLS_ID in match_details)
        self.assertTrue(Match.AWAY_TEAM_FLS_ID in match_details)
        self.assertTrue(Match.HOME_FORM in match_details)
        self.assertTrue(Match.AWAY_FORM in match_details)
        self.assertTrue(Match.PREVIOUS_ENCOUNTERS in match_details)

    def testPlayerDetailsEndpoint(self):
        player_details = self.fls.request_player_details(team_ids=1)
        self.assertTrue(len(player_details) > 0)
        self.assertEqual(self.test_fls.request_player_details(team_ids=1), [])
        self.assertTrue(Player.NAME in player_details[0])



