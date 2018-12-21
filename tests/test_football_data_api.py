import unittest
import json
from ingest_engine.football_data import FootballData
from ingest_engine.cons import Competition, FootballDataApiFilters as fda


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

    def testPerformGet(self):
        test_fd = FootballData(api_key='test')
        comps = self.fd.request_competitions(2002)
        comps_locked = self.fd.request_competitions(2004)
        self.assertEqual(test_fd.request_competitions(), {})
        self.assertEqual(comps_locked, {})
        self.assertEqual(comps['id'], 2002)
        test_fd.session.close()

    def testCompetitionEndPoint(self):
        test_fd = FootballData(api_key='test')
        comps = self.fd.request_competitions(competition_id=2002)
        self.assertEqual(test_fd.request_competitions(), {})
        self.assertEqual(comps['id'], 2002)
        test_fd.session.close()

    def testCompetitionMatchEndPoint(self):
        test_fd = FootballData(api_key='test')
        comp_matches = self.fd.request_competition_match(competition_id=2003, **{fda.MATCHDAY: 11})
        self.assertEqual(test_fd.request_competition_match(competition_id=2003), {})
        self.assertEqual(comp_matches['matches'][0][fda.MATCHDAY], 11)

    def testMatchEndPoint(self):
        test_fd = FootballData(api_key='test')
        matches = self.fd.request_match(**{fda.TO_DATE: '2018-09-15', fda.FROM_DATE: '2018-09-05'})
        self.assertEqual(matches['filters'][fda.FROM_DATE], '2018-09-05')
        self.assertEqual(test_fd.request_match(match_id=204998), {})

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
        



