import unittest
from flask_run import app
from ingest_engine.cons import Competition as COMPETITION, Standings as STANDINGS, Match as MATCH
from api_engine.api_cons import API_ENDPOINTS, API, API_ERROR



class ApiInterfaceTest(unittest.TestCase):
    def setUp(self):
        self.api = app.test_client()
        self.api.testing = True

    def tearDown(self):
        pass

    def testBaseUrl(self):
        true_endpoints = [e for c, e in vars(API_ENDPOINTS).items() if not c.startswith("__")]
        # result = self.api.get('/v1').get_json()
        result = self.api.get('/v1', follow_redirects=True).get_json()
        result_endpoints = result[API.ENDPOINTS]
        for endpoint in result_endpoints:
            self.assertTrue(endpoint[API.ENDPOINT_URL].split("v1/")[1] in true_endpoints)
            self.assertIsInstance(endpoint[API.URL_DESCRIPTION], str)

    def testCompetitionUrl(self):
        all_result = self.api.get('/v1/competitions').get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (COMPETITION.ID,
                                                      COMPETITION.NAME,
                                                      COMPETITION.LOCATION,
                                                      COMPETITION.CODE,
                                                      COMPETITION.FASTEST_LIVE_SCORES_API_ID,
                                                      COMPETITION.FOOTBALL_DATA_API_ID)))

        filter_result = self.api.get('/v1/competition?id=1').get_json()
        self.assertEqual(filter_result[COMPETITION.ID], 1)
        filter_result = self.api.get('/v1/competitions?id=1,11').get_json()
        for result in filter_result:
            self.assertTrue(result[COMPETITION.ID] in [1, 11])

        # AND query - no one competition with id 1 AND also id 2
        filter_result = self.api.get('/v1/competition?id=1,2').get_json()
        self.assertEqual(filter_result, {
            'message': API_ERROR.COMPETITION_404,
            'status_code': 404
        })

        filter_result = self.api.get('/v1/competition?name=La Liga').get_json()
        self.assertEqual(filter_result[COMPETITION.NAME], "La Liga")

        filter_result = self.api.get('/v1/competition?code=PL').get_json()
        self.assertEqual(filter_result[COMPETITION.CODE], 'PL')

        filter_result = self.api.get('/v1/competition?location=spain').get_json()
        self.assertEqual(filter_result[COMPETITION.LOCATION], "Spain")

        filter_result = self.api.get('/v1/competition?fd_api_id=2002').get_json()
        self.assertEqual(filter_result[COMPETITION.FOOTBALL_DATA_API_ID], 2002)

        filter_result = self.api.get('/v1/competition?fls_api_id=81').get_json()
        self.assertEqual(filter_result[COMPETITION.FASTEST_LIVE_SCORES_API_ID], 81)

    def testStandingsUrl(self):

        def filter_test(filter_str, filter_val):
            filter_result = self.api.get(f'/v1/standings?{filter_str}={filter_val}').get_json()
            if not isinstance(filter_result, list):
                filter_result = [filter_result]

            for result in filter_result:
                for entry in result[STANDINGS.TABLE]:
                    self.assertTrue(entry[filter_str], filter_val)

        def filter_test_adv(filter_str, filter_val, op):
            filter_result = self.api.get(f'/v1/standings/all?{filter_str}=${op}:{filter_val}').get_json()
            if not isinstance(filter_result, list):
                filter_result = [filter_result]  # Handle returns as dict or list

            for result in filter_result:
                for entry in result[STANDINGS.TABLE]:
                    if op == "lt":
                        self.assertLess(entry[filter_str], filter_val)

                    elif op == "lte":
                        self.assertLessEqual(entry[filter_str], filter_val)

                    elif op == "gt":
                        self.assertGreater(entry[filter_str], filter_val)

                    elif op == "gte":
                        self.assertGreaterEqual(entry[filter_str], filter_val)

        all_result = self.api.get('/v1/standings/all').get_json()
        self.assertTrue(len(all_result), 10)
        for result in all_result:
            self.assertTrue(all(k in result for k in (STANDINGS.ID,
                                                      STANDINGS.COMPETITION_ID,
                                                      STANDINGS.TYPE,
                                                      STANDINGS.SEASON,
                                                      STANDINGS.MATCH_DAY)))

            for entry in result[STANDINGS.TABLE]:
                self.assertTrue(STANDINGS.ID in entry)
                self.assertTrue(STANDINGS.STANDINGS_ID in entry)
                self.assertTrue(STANDINGS.POSITION in entry)
                self.assertTrue(STANDINGS.TEAM_NAME in entry)
                self.assertTrue(STANDINGS.FOOTBALL_DATA_TEAM_ID in entry)
                self.assertTrue(STANDINGS.GAMES_PLAYED in entry)
                self.assertTrue(STANDINGS.GAMES_WON in entry)
                self.assertTrue(STANDINGS.GAMES_DRAWN in entry)
                self.assertTrue(STANDINGS.GAMES_LOST in entry)
                self.assertTrue(STANDINGS.POINTS in entry)
                self.assertTrue(STANDINGS.GOALS_FOR in entry)
                self.assertTrue(STANDINGS.GOALS_AGAINST in entry)
                self.assertTrue(STANDINGS.GOAL_DIFFERENCE in entry)

        all_result = self.api.get('/v1/standings').get_json()
        self.assertTrue(len(all_result), 10)

        filter_result = self.api.get('/v1/standings?id=1').get_json()
        self.assertFalse(isinstance(filter_result, list))
        self.assertEqual(filter_result[STANDINGS.ID], 1)

        filter_result = self.api.get('/v1/standings/all?id=1,2').get_json()
        self.assertTrue(isinstance(filter_result, list))
        for result in filter_result:
            self.assertTrue(result[STANDINGS.ID] in [1, 2])

        self.assertTrue(filter_result[0][STANDINGS.ID] != filter_result[1][STANDINGS.ID])

        filter_test(filter_str=STANDINGS.POSITION, filter_val=5)
        filter_test(filter_str=STANDINGS.TEAM_NAME, filter_val="chapecoense")
        filter_test(filter_str=STANDINGS.GAMES_PLAYED, filter_val=3)
        filter_test(filter_str=STANDINGS.GAMES_WON, filter_val=1)
        filter_test(filter_str=STANDINGS.GAMES_DRAWN, filter_val=2)
        filter_test(filter_str=STANDINGS.GAMES_LOST, filter_val=5)
        filter_test(filter_str=STANDINGS.POINTS, filter_val=20)
        filter_test(filter_str=STANDINGS.GOALS_FOR, filter_val=15)
        filter_test(filter_str=STANDINGS.GOALS_AGAINST, filter_val=5)
        filter_test(filter_str=STANDINGS.GOAL_DIFFERENCE, filter_val=5)

        filter_test_adv(filter_str=STANDINGS.POSITION, filter_val=10, op="lt")
        filter_test_adv(filter_str=STANDINGS.GAMES_PLAYED, filter_val=3, op="lte")
        filter_test_adv(filter_str=STANDINGS.GAMES_WON, filter_val=10, op="gte")
        filter_test_adv(filter_str=STANDINGS.GAMES_DRAWN, filter_val=5, op="gt")

        filter_result = self.api.get('/v1/standings?points=$lt:0').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.STANDINGS_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

        filter_result = self.api.get('/v1/standings?id=1&limit=astring').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.INTEGER_LIMIT_400)
        self.assertEqual(filter_result[API.STATUS_CODE], 400)

    def testDBMatchUrl(self):
        # Whilst API is PL only
        # comp_fd_id = 2021
        # comp_fls_id = 2

        all_result = self.api.get('/v1/matches&limit=5').get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (MATCH.ID,
                                                      MATCH.FOOTBALL_DATA_ID,
                                                      MATCH.FLS_MATCH_ID,
                                                      MATCH.FLS_API_COMPETITION_ID,
                                                      MATCH.HOME_TEAM_FLS_ID,
                                                      MATCH.AWAY_TEAM_FLS_ID,
                                                      )))
        self.assertIsInstance(all_result, list)
        self.assertEqual(len(all_result), 5)

        single_result = self.api.get('/v1/match?match_day=1').get_json()
        self.assertTrue(all(k in single_result for k in (MATCH.ID,
                                                         MATCH.FOOTBALL_DATA_ID,
                                                         MATCH.FLS_MATCH_ID,
                                                         MATCH.FLS_API_COMPETITION_ID,
                                                         MATCH.HOME_TEAM_FLS_ID,
                                                         MATCH.AWAY_TEAM_FLS_ID
                                                         )))
        self.assertEqual(single_result[MATCH.MATCHDAY], 1)
        self.assertIsInstance(single_result, dict)

        filter_result = self.api.get('/v1/match?id=-1').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.MATCH_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)














