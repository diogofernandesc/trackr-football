import unittest
from ingest_engine.fantasy_api import Fantasy
from ingest_engine.cons import Team, Player, FantasyGameWeek


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.fantasy = Fantasy()

    def tearDown(self):
        self.fantasy.session.close()

    def testApiSetUp(self):
        req = self.fantasy.session.get(self.fantasy.uri + 'fixtures')
        self.assertEqual(req.status_code, 200)

    def testBaseUrl(self):
        base_url_results = self.fantasy.request_base_information(full=True)
        player_constants = [s for s in list(Player.__dict__.values()) if isinstance(s, str) and s.startswith('fantasy')]
        team_constants = [s for s in list(Team.__dict__.values()) if isinstance(s, str) and s.startswith('fantasy')]

        # not necessary to check for 'id' field as it's not part of the api, 'fantasy_id' used here instead
        game_week_constants = [s for s in list(FantasyGameWeek.__dict__.values())
                               if isinstance(s, str) and s != 'id']

        self.assertTrue('players' in base_url_results)
        self.assertTrue('teams' in base_url_results)
        self.assertTrue('game_weeks' in base_url_results)

        for player in base_url_results['players']:
            self.assertTrue(set(player_constants) <= set(player))

        for team in base_url_results['teams']:
            self.assertTrue(set(team_constants) <= set(team))

        for game_week in base_url_results['game_weeks']:
            self.assertTrue(set(game_week_constants[1:]) <= set(game_week))



