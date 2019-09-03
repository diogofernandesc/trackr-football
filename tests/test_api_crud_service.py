import unittest
from flask_run import app
from ingest_engine.cons import Match as MATCH, Team as TEAM
from api_engine.api_cons import API, API_ERROR


class ApiInterfaceTest(unittest.TestCase):
    def setUp(self):
        self.api = app.test_client()
        self.api.testing = True

    def tearDown(self):
        pass

    def testCrudDBMatchUrl(self):
        # Whilst API is PL only
        # comp_fd_id = 2021
        # comp_fls_id = 2

        all_result = self.api.get('/v1/db/matches?limit=5', follow_redirects=True).get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (MATCH.FOOTBALL_DATA_ID,
                                                      MATCH.FLS_MATCH_ID,
                                                      MATCH.FLS_API_COMPETITION_ID,
                                                      MATCH.HOME_TEAM_FLS_ID,
                                                      MATCH.AWAY_TEAM_FLS_ID,
                                                      )))
        self.assertIsInstance(all_result, list)
        self.assertEqual(len(all_result), 5)

        single_result = self.api.get('/v1/db/match?match_day=1').get_json()
        for match in single_result:
            self.assertTrue(all(k in match for k in (MATCH.FOOTBALL_DATA_ID,
                                                     MATCH.FLS_MATCH_ID,
                                                     MATCH.FLS_API_COMPETITION_ID,
                                                     MATCH.HOME_TEAM_FLS_ID,
                                                     MATCH.AWAY_TEAM_FLS_ID
                                                     )))
            self.assertEqual(match[MATCH.MATCHDAY], 1)
            self.assertIsInstance(match, dict)

        filter_result = self.api.get('/v1/db/match?id=-1').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.MATCH_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

    def testCrudDBTeamUrl(self):
        all_result = self.api.get('v1/db/teams?limit=4', follow_redirects=True).get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (TEAM.NAME,
                                                      TEAM.FANTASY_CODE,
                                                      TEAM.FANTASY_ID,
                                                      TEAM.FANTASY_WEEK_STRENGTH,
                                                      TEAM.FANTASY_OVERALL_HOME_STRENGTH,
                                                      TEAM.FANTASY_OVERALL_AWAY_STRENGTH,
                                                      TEAM.FANTASY_ATTACK_HOME_STRENGTH,
                                                      TEAM.FANTASY_ATTACK_AWAY_STRENGTH,
                                                      TEAM.FANTASY_DEFENCE_HOME_STRENGTH,
                                                      TEAM.FANTASY_DEFENCE_AWAY_STRENGTH,
                                                      TEAM.SHORT_NAME,
                                                      TEAM.FASTEST_LIVE_SCORES_API_ID,
                                                      TEAM.FOOTBALL_DATA_ID)))

        self.assertIsInstance(all_result, list)
        self.assertEqual(len(all_result), 4)













