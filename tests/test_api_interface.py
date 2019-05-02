import unittest
from api_engine import api_interface
from ingest_engine.cons import Competition as COMPETITION
from api_engine.api_cons import API_ENDPOINTS, API


class ApiInterfaceTest(unittest.TestCase):
    def setUp(self):
        self.api = api_interface.app.test_client()
        self.api.testing = True

    def tearDown(self):
        pass

    def testBaseUrl(self):
        true_endpoints = [e for c, e in vars(API_ENDPOINTS).items() if not c.startswith("__")]
        result = self.api.get('/v1').get_json()
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

        filter_result = self.api.get('/v1/competitions?id=1').get_json()
        self.assertEqual(filter_result[COMPETITION.ID], 1)

        # TODO: Test ?filter= (AND FILTER)

