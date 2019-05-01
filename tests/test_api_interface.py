import unittest
from api_engine import api_interface
from api_engine.api_cons import API_ENDPOINTS, API


class ApiInterfaceTest(unittest.TestCase):
    def setUp(self):
        self.api = api_interface.app.test_client()
        self.api.testing = True

    def tearDown(self):
        pass

    def testBaseUrl(self):
        true_endpoints = [e for c, e in vars(API_ENDPOINTS).items() if not c.startswith("__")]
        result = self.api.get('/').get_json()
        result_endpoints = result[API.ENDPOINTS]
        for endpoint in result_endpoints:
            self.assertTrue(endpoint[API.ENDPOINT_URL].split("v1/")[1] in true_endpoints)
            self.assertIsInstance(endpoint[API.URL_DESCRIPTION], str)
