from ratelimit import limits
import requests as re
import os
import json

HOUR = 3600


class FastestLiveScores(object):
    """
    Wrapper for API available at -> https://customer.fastestlivescores.com/
    """
    def __init__(self, api_key):
        self.session = re.session()
        self.api_key = api_key
        if not api_key:
            self.api_key = os.environ.get('FASTEST_LIVE_SCORES_API_KEY')

    def build_endpoint(self, endpoint_name):
        '''
        Create endpoint url used in API call based on endpoint name
        :param endpoint_name: the API resource path e.g. /competitions
        :return: Endpoint string
        '''
        return f'https://api.crowdscores.com/v1/{endpoint_name}?api_key={self.api_key}'

    @limits(calls=100, period=HOUR)
    def perform_get(self, built_uri):
        """
        Performs GET request dealing with any issues arising specific to this API
        :param built_uri: API Url to use in GET request
        :return: Parsed results or {} if failed
        """

        request = self.session.get(built_uri)
        try:
            result = json.loads(request.text)
            if 'errorText' in result or request.status_code == 400 or request.status_code == 404:
                result = {}

        except re.exceptions.ConnectionError:
            result = {}

        return result

    def request_competitions(self):
        """
        Retrieve all the competitions the API supports
        :return: List of competitions, each entry with data
        """
        endpoint = self.build_endpoint(endpoint_name="competitions")
        result = self.perform_get(built_uri=endpoint)
        



if __name__ == "__main__":
    fls = FastestLiveScores(api_key=os.getenv('FASTEST_LIVE_SCORES_API_KEY'))
    fls.request_competitions()


