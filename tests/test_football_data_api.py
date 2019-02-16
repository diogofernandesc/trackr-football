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

    def testPerformGet(self):
        comps_locked = self.fd.request_competitions(2004)
        self.assertEqual(self.test_fd.request_competitions(), [])
        self.assertEqual(comps_locked, [])

    def testCompetitionEndPoint(self):
        comps = self.fd.request_competitions(competition_id=2002)
        all_comps = self.fd.request_competitions()
        self.assertEqual(self.test_fd.request_competitions(), [])
        self.assertEqual(comps[0][Competition.FOOTBALL_DATA_API_ID], 2002)
        self.assertTrue(len(all_comps) > 100)

    def testCompetitionMatchEndPoint(self):
        comp_matches = self.fd.request_competition_match(competition_id=2003, **{Match.MATCHDAY: 11})
        self.assertEqual(self.test_fd.request_competition_match(competition_id=2003), [])
        self.assertEqual(comp_matches[0][Match.MATCHDAY], 11)

    def testCompetitionTeamEndpoint(self):
        comp_teams = self.fd.request_competition_team(competition_id=2002)
        comp_season = self.fd.request_competition_team(competition_id=2002, season=2017)
        self.assertEqual(comp_season[0][Team.FOOTBALL_DATA_ID], 1)
        self.assertEqual(self.test_fd.request_competition_team(competition_id=2002), [])
        self.assertEqual(comp_teams[0][Team.FOOTBALL_DATA_ID], 2)

    def testCompetitionStandingsEndpoint(self):
        comp_standings_league = self.fd.request_competition_standings(competition_id=2002)
        comp_standings_non_league = self.fd.request_competition_standings(competition_id=2001)
        comp_standing_type = self.fd.request_competition_standings(competition_id=2002, standing_type=fda.STANDING_HOME)
        self.assertTrue(len(comp_standing_type['standings'][0]) > 5)
        self.assertEqual(self.test_fd.request_competition_standings(competition_id=2002), [])
        self.assertIsNone(comp_standings_league['standings'][0]['group'])
        self.assertIsInstance(comp_standings_non_league['standings'][0]['group'], str)

    def testCompetitionScorersEndpoint(self):
        comp_scorers = self.fd.request_competition_scorers(competition_id=2002)
        comp_limit = self.fd.request_competition_scorers(competition_id=2002, limit=5)
        self.assertEqual(self.test_fd.request_competition_scorers(competition_id=2002), [])
        self.assertIsInstance(comp_scorers[0][Player.NUMBER_OF_GOALS], int)
        self.assertEqual(len(comp_scorers[0]), 10)
        self.assertEqual(len(comp_limit), 5)

    def testMatchEndPoint(self):
        matches = self.fd.request_match(**{fda.TO_DATE: '2018-09-15', fda.FROM_DATE: '2018-09-05'})
        # print(f'MATCHES LINE: {matches}')
        # player_matches = self.fd.request_match(player_id=1)
        # self.assertTrue(len(player_matches[0]) > 0)
        # self.assertRaises(ValueError, self.fd.request_match, 223, 1)
        self.assertTrue(len(matches[0]) > 0)
        # self.assertEqual(matches[0]['filters'][fda.FROM_DATE], '2018-09-05')
        # self.assertEqual(self.test_fd.request_match(match_id=204998), [])

    def testTeamEndpoint(self):
        team = self.fd.request_team(team_id=4)
        self.assertEqual(self.test_fd.request_team(team_id=4), {})
        self.assertTrue(len(team[Team.SQUAD]) >= 11)
        self.assertIsInstance(team[Team.FOOTBALL_DATA_ID], int)

    def testPlayerEndpoint(self):
        player = self.fd.request_player(player_id=1)
        self.assertEqual(self.test_fd.request_player(player_id=1), {})
        self.assertTrue(len(player) >= 7)
        self.assertIsInstance(player[Player.SHIRT_NUMBER], int)

    def testCompetitionParse(self):
        test_res = {
            Competition.NAME: 'Bundesliga',
            Competition.FOOTBALL_DATA_API_ID: 2002,
            Competition.LOCATION: 'Germany',
            Competition.CODE: 'BL1',
        }
        self.assertEqual(self.fd.request_competitions(competition_id=2002), [test_res])
        
    def testMatchParse(self):
        test_res = {'season_football_data_id': 235686,
                     'season_start_date': '2018-08-24',
                     'season_end_date': '2019-05-18',
                     'utc_date': '2018-08-24T18:30:00Z',
                     'status': 'FINISHED',
                     'matchday': 1,
                     'full_time_home_score': 3,
                     'full_time_away_score': 1,
                     'half_time_home_score': 1,
                     'half_time_away_score': 0,
                     'extra_time_home_score': None,
                     'extra_time_away_score': None,
                     'penalty_home_score': None,
                     'penalty_away_score': None,
                     'winner': 'HOME_TEAM',
                     'home_team': 'FC Bayern München',
                     'away_team': 'TSG 1899 Hoffenheim',
                     'referees':
                         ['Bastian Dankert', 'René Rohde', 'Markus Häcker', 'Thorsten Schiffner', 'Sören Storks']}

        test_res2 = {
            "season_football_data_id": 204998,
            "season_start_date": "2018-04-14",
            "season_end_date": "2018-12-02",
            "utc_date": "2018-09-05T22:30:00Z",
            "status": "FINISHED",
            "matchday": 23,
            "full_time_home_score": 1,
            "full_time_away_score": 1,
            "half_time_home_score": 1,
            "half_time_away_score": 1,
            "extra_time_home_score": None,
            "extra_time_away_score": None,
            "penalty_home_score": None,
            "penalty_away_score": None,
            "winner": "DRAW",
            "home_team": "Botafogo FR",
            "away_team": "Cruzeiro EC",
            "referees": [
                "Raphael Claus",
                "Danilo Ricardo Simon Manis",
                "Rogerio Pablos Zanardo",
                "Daniel do Espirito Santo Parro"],
            'filters': {'dateFrom': '2018-09-05',
                        'dateTo': '2018-09-15',
                        'permission': 'TIER_ONE'},
            
        }

        self.assertEqual(self.fd.request_competition_match(competition_id=2002)[0], test_res)
        self.assertEqual(self.fd.request_match(**{fda.TO_DATE: '2018-09-15', fda.FROM_DATE: '2018-09-05'})[0], test_res2)
