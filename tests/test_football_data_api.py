import unittest
import json
from ingest_engine.football_data import FootballData
from ingest_engine.cons import Competition


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.fd = FootballData()

    def tearDown(self):
        self.fd.session.close()

    def testApiSetUp(self):
        test_fd = FootballData(api_key='test')
        req = test_fd.session.get('http://api.football-data.org/v2/competitions').text
        req = json.loads(req)
        self.assertEqual(req['errorCode'], 400)
        test_fd.session.close()

    def testCompetitionEndPoint(self):
        test_fd = FootballData(api_key='test')
        comps = self.fd.request_competitions(2002)
        self.assertEqual(test_fd.request_competitions(), {})
        self.assertEqual(comps['id'], 2002)
        test_fd.session.close()

    def testCompetitionParse(self):
        test_req = json.loads(
            '''
            {
                  "id":2002,
                  "area":{
                    "id":2088,
                    "name":"Germany"
                  },
                  "name":"Bundesliga",
                  "code":"BL1",
                  "emblemUrl":null,
                  "plan":"TIER_ONE",
                  "currentSeason":{
                    "id":155,
                    "startDate":"2018-08-24",
                    "endDate":"2019-05-18",
                    "currentMatchday":14,
                    "winner":null
                  }
            }
            '''
        )
        test_res = {
            Competition.NAME: 'Bundesliga',
            Competition.FOOTBALL_DATA_API_ID: 2002,
            Competition.LOCATION: 'Germany',
            Competition.CODE: 'BL1',
        }
        self.assertEqual(self.fd.parse_competitions(api_res=test_req), [test_res])
        



