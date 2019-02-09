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

    def testBaseEndpoint(self):
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
            self.assertTrue(len(set(player_constants) & set(player)) > 10)

        for team in base_url_results['teams']:
            self.assertTrue(set(team_constants) <= set(team))

        for game_week in base_url_results['game_weeks']:
            self.assertTrue(set(game_week_constants[1:]) <= set(game_week))

    def testPlayerEndpoint(self):
        player_details_full = self.fantasy.request_player_data(player_id=160)
        no_season_summaries = self.fantasy.request_player_data(player_id=160, season_summaries=False)
        no_fixture_data = self.fantasy.request_player_data(player_id=160, fixture_data=False)
        no_fixture_codes = self.fantasy.request_player_data(player_id=160, fixture_codes=False)
        player_constants = [s for s in list(Player.__dict__.values()) if isinstance(s, str) and s.startswith('fantasy')]
        self.assertTrue('season_summaries' in player_details_full)
        self.assertTrue('season_match_history' in player_details_full)
        self.assertTrue('future_fixtures' in player_details_full)
        self.assertFalse('season_summaries' in no_season_summaries)
        self.assertFalse('season_match_history' in no_fixture_data)
        self.assertFalse('future_fixtures' in no_fixture_codes)
        for fixture in player_details_full['season_match_history']:
            self.assertTrue(len(set(player_constants) & set(fixture)) > 10)





