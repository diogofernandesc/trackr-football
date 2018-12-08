import requests as re
import os


class FootballData(object):
    '''
    Wrapper for the football-data api available at https://www.football-data.org/documentation/api
    '''

    def __init__(self):
        self.session = re.Session()
        self.session.auth = ('X-Auth-Token', os.environ.get('FOOTBALL_DATA_API_KEY'))
        self.uri = 'http://api.football-data.org/v2/'
        pass

    def get_competition(self, **kwargs):
        '''
        Performs API request to retrieve all competitions at URL -> /v2/competitions
        OR specific competitions at URL -> /v2/competitions/2000,2002,3001...
        :param kwargs: List of competition ids
        :return: Request result for competitions endpoint
        '''
        built_uri = 'competitions/'
        if 'competitions' in kwargs:
            competition_filter = kwargs.get('competitions')
            if type(competition_filter) == int:
                built_uri += str(competition_filter)

            else:
                competition_filter = list(map(str, competition_filter))
                if len(competition_filter) > 1:
                    competition_filter = ",".join(competition_filter)

                built_uri += competition_filter

        result = self.session.get(url=self.uri + built_uri)
        try:
            if result.status_code == 200:
                result = result.text
        except re.exceptions.ConnectionError:
            result = {}

        print(result)


    def get_match(self, **kwargs):
        '''

        :param kwargs: Dict of possible filters for the endpoint
        :return:
        '''
        pass

print(os.environ.get('FOOTBALL_DATA_API_KEY'))
fd = FootballData()
fd.get_competition(competitions=2002)


