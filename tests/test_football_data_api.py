import unittest
import json
from ingest_engine.football_data import FootballData
from ingest_engine.cons import Competition, Match, Team, Player, FootballDataApiFilters as fda
import os


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.fd = FootballData(api_key=os.getenv("FOOTBALL_DATA_API_KEY"))
        self.test_fd = FootballData(api_key='test')

    def tearDown(self):
        self.fd.session.close()
        self.test_fd.session.close()

    def testApiSetUp(self):
        req = self.test_fd.session.get('http://api.football-data.org/v2/competitions').text
        req = json.loads(req)
        self.assertEqual(req['errorCode'], 400)
        self.test_fd.session.close()

    def testCompetitionEndPoint(self):
        comps = self.fd.request_competitions(competition_id=2002)
        all_comps = self.fd.request_competitions()
        self.assertEqual(self.test_fd.request_competitions(), [])
        self.assertEqual(comps[0][Competition.FOOTBALL_DATA_API_ID], 2002)
        self.assertTrue(len(all_comps) > 100)

    def testCompetitionMatchEndPoint(self):
        comp_matches = self.fd.request_competition_match(competition_id='PL', **{fda.MATCHDAY: 11})
        self.assertEqual(self.test_fd.request_competition_match(competition_id=2003), [])
        self.assertEqual(comp_matches[0][Match.MATCHDAY], 11)

    def testCompetitionTeamEndpoint(self):
        comp_teams = self.fd.request_competition_team(competition_id=2002)
        self.assertEqual(self.test_fd.request_competition_team(competition_id=2002), [])
        self.assertEqual(comp_teams[0][Team.FOOTBALL_DATA_ID], 1)

    def testCompetitionStandingsEndpoint(self):
        comp_standings_league = self.fd.request_competition_standings(competition_id=2002)
        self.assertEqual(self.test_fd.request_competition_standings(competition_id=2002), [])
        self.assertIsNone(comp_standings_league['standings'][0]['group'])

    def testCompetitionScorersEndpoint(self):
        comp_scorers = self.fd.request_competition_scorers(competition_id=2002)
        self.assertEqual(self.test_fd.request_competition_scorers(competition_id=2002), [])
        if comp_scorers:
            self.assertIsInstance(comp_scorers[0][Player.NUMBER_OF_GOALS], int)

    def testMatchEndPoint(self):
        matches = self.fd.request_match(**{fda.TO_DATE: '2018-09-15', fda.FROM_DATE: '2018-09-05'})
        player_matches = self.fd.request_match(player_id=1)
        self.assertTrue(len(player_matches[0]) > 0)
        self.assertRaises(ValueError, self.fd.request_match, 223, 1)
        self.assertTrue(len(matches[0]) > 0)
        self.assertEqual(matches[0]['filters'][fda.FROM_DATE], '2018-09-05')
        self.assertEqual(self.test_fd.request_match(match_id=204998), [])

    def testTeamEndpoint(self):
        team = self.fd.request_team(team_id=4)
        self.assertEqual(self.test_fd.request_team(team_id=4), {})
        self.assertTrue(len(team[Team.SQUAD]) >= 11)
        self.assertIsInstance(team[Team.FOOTBALL_DATA_ID], int)

    def testPlayerEndpoint(self):
        player = self.fd.request_player(player_id=1)
        self.assertEqual(self.test_fd.request_player(player_id=1), {})
        self.assertTrue(len(player) >= 7)

    def testCompetitionParse(self):
        test_res = {
            Competition.NAME: 'Bundesliga',
            Competition.FOOTBALL_DATA_API_ID: 2002,
            Competition.LOCATION: 'Germany',
            Competition.CODE: 'BL1',
        }
        self.assertEqual(self.fd.request_competitions(competition_id=2002), [test_res])
