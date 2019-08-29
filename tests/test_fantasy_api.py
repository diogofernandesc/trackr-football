import unittest
from ingest_engine.fantasy_api import Fantasy, ingest_historical_base_csv, ingest_historical_gameweek_csv
from ingest_engine.cons import Team, Player, Match, FantasyGameWeek, Season
from pathlib import Path
from itertools import chain
import os


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.fantasy = Fantasy()

    def tearDown(self):
        self.fantasy.session.close()

    def testApiSetUp(self):
        req = self.fantasy.session.get(self.fantasy.uri + 'fixtures')
        self.assertEqual(req.status_code, 200)

    def testBaseEndpoint(self):
        base_url_results = self.fantasy.request_base_information()
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
            self.assertTrue(set(game_week_constants[1:]) >= set(game_week))

    def testPlayerEndpoint(self):
        player_details_full = self.fantasy.request_player_data(player_id=160)
        no_season_summaries = self.fantasy.request_player_data(player_id=169, season_summaries=False)
        no_fixture_data = self.fantasy.request_player_data(player_id=273, fixture_data=False)
        no_fixture_codes = self.fantasy.request_player_data(player_id=177, fixture_codes=False)
        player_constants = [s for s in list(Player.__dict__.values()) if isinstance(s, str) and s.startswith('fantasy')]
        self.assertTrue('season_summaries' in player_details_full)
        self.assertTrue('season_match_history' in player_details_full)
        self.assertTrue('future_fixtures' in player_details_full)
        self.assertFalse('season_summaries' in no_season_summaries)
        self.assertFalse('season_match_history' in no_fixture_data)
        self.assertFalse('future_fixtures' in no_fixture_codes)
        for fixture in player_details_full['season_match_history']:
            self.assertTrue(len(set(player_constants) & set(fixture)) > 10)

    def testMatchEndpoint(self):
        matches = self.fantasy.request_matches()
        match_constants = [s for s in list(Match.__dict__.values()) if isinstance(s, str)]
        for match in matches:
            if len(match) > 11:
                self.assertTrue({Match.GOALS_SCORED,
                                 Match.ASSISTS,
                                 Match.OWN_GOALS,
                                 Match.PENALTIES_SAVED,
                                 Match.PENALTIES_MISSED,
                                 Match.YELLOW_CARDS,
                                 Match.RED_CARDS,
                                 Match.SAVES,
                                 Match.BONUS,
                                 Match.BPS}
                                <= set(match))

            self.assertTrue(len(set(match_constants) & set(match)) >= 11)

    def testHistoricalIngestGameWeek(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        current_path = "/".join(current_path.split("/")[:-1])
        gw_paths1 = Path(f'{current_path}/historical_fantasy/2016-17/gws').glob('**/*.csv')
        gw_paths2 = Path(f'{current_path}/historical_fantasy/2017-18/gws').glob('**/*.csv')
        gw_paths = chain(gw_paths1, gw_paths2)
        for gw in gw_paths:
            str_gw = str(gw)
            gw_parsed = ingest_historical_gameweek_csv(csv_file=str_gw, season='201617')
            for player_data in gw_parsed:
                self.assertTrue(len(player_data) == 48)
                self.assertTrue(Player.NAME in player_data)
                self.assertTrue(Player.YELLOW_CARDS in player_data)

    def testHistoricalIngestSeason(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        current_path = "/".join(current_path.split("/")[:-1])

        season1 = ingest_historical_base_csv(
            csv_file=f'{current_path}/historical_fantasy/2016-17/cleaned_players.csv', season='201617')

        season2 = ingest_historical_base_csv(
            csv_file=f'{current_path}/historical_fantasy/2017-18/cleaned_players.csv', season='201718')

        seasons = season1 + season2
        field_names = (
            Player.FIRST_NAME,
            Player.LAST_NAME,
            Player.NUMBER_OF_GOALS,
            Player.ASSISTS,
            Player.FANTASY_OVERALL_POINTS,
            Player.MINUTES_PLAYED,
            Player.GOALS_CONCEDED,
            Player.FANTASY_CREATIVITY,
            Player.FANTASY_INFLUENCE,
            Player.FANTASY_THREAT,
            Player.FANTASY_TOTAL_BONUS,
            Player.FANTASY_ICT_INDEX,
            Player.CLEAN_SHEETS,
            Player.RED_CARDS,
            Player.YELLOW_CARDS,
            Player.FANTASY_SELECTION_PERCENTAGE,
        )
        for player in seasons:
            self.assertEqual(len(player), 18)
            for field_name in field_names:
                self.assertTrue(field_name in player)
            self.assertTrue(Season.NAME in player)








