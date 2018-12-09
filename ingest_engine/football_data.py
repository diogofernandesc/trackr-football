import requests as re
import json
import os
from ingest_engine.cons import Competition


class FootballData(object):
    '''
    Wrapper for the football-data api available at https://www.football-data.org/documentation/api
    '''

    def __init__(self, api_key=None):
        self.session = re.Session()
        if not api_key:
            api_key = os.environ.get('FOOTBALL_DATA_API_KEY')
        self.session.headers.update({'X-Auth-Token': api_key})
        self.uri = 'http://api.football-data.org/v2/'

    def request_competitions(self, competition_id=None):
        '''
        Performs API request to retrieve all competitions at URL -> /v2/competitions
        OR specific competitions at URL -> /v2/competitions/2000,2002,3001...
        :rtype dict
        :param kwargs: List of competition ids 
        :return: Request result for competitions endpoint
        '''
        built_uri = 'competitions/'
        if competition_id:
            built_uri += str(competition_id)

        result = self.session.get(url=self.uri + built_uri)
        try:
            result = json.loads(result.text)
            if 'errorCode' in result:
                result = {}
        except re.exceptions.ConnectionError:
            result = {}

        return result

    def parse_competitions(self, api_res):
        '''
        Parse competition results from API request ready for database insertion/update/other
        :rtype: list
        :param api_res: The dict result from API call to the competitions endpoint
        :return: Parsed results from API in list of dicts format
        '''
        total_results = []
        if 'competitions' in api_res:
            api_res = api_res['competitions']

        else:
            api_res = [api_res]

        for comp in api_res:
            dict_result = {
                Competition.NAME: comp['name'],
                Competition.CODE: comp['code'],
                Competition.LOCATION: comp['area']['name'],
                Competition.FOOTBALL_DATA_API_ID: comp['id']
            }
            total_results.append(dict_result)

        return total_results

    def get_match(self, **kwargs):
        '''

        :param kwargs: Dict of possible filters for the endpoint
        :return:
        '''
        pass

# print(os.environ.get('FOOTBALL_DATA_API_KEY'))
# fd = FootballData()
# fd.session.get('http://api.football-data.org/v2/competitions')
# api_res = fd.request_competitions(2002)
# print(api_res)
# fd.parse_competitions(api_res=api_res)


