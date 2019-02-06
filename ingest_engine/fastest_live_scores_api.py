from ratelimit import limits, sleep_and_retry
import requests as re
import os
import json
from ingest_engine.cons import Competition, Team

HOUR = 3600


class FastestLiveScores(object):
    """
    Wrapper for API available at -> https://customer.fastestlivescores.com/
    """
    def __init__(self, api_key=None):
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

    @sleep_and_retry
    @limits(calls=100, period=HOUR)
    def perform_get(self, built_uri):
        """
        Performs GET request dealing with any issues arising specific to this API
        :param built_uri: API Url to use in GET request
        :return: Parsed results or {} if failed
        """

        request = self.session.get(built_uri)
        try:
            print(built_uri)
            result = json.loads(request.text)
            if 'errorText' in result or request.status_code == 400 or request.status_code == 404:
                result = {}

        except re.exceptions.ConnectionError:
            result = {}

        except json.decoder.JSONDecodeError:
            result = {}

        return result

    def request_competitions(self):
        """
        Retrieve all the competitions the API supports
        Mainly used for mapping existing competitions in DB to the same competition in API
        :return: List of competitions, each entry with data
        """
        endpoint = self.build_endpoint(endpoint_name="competitions")
        result = self.perform_get(built_uri=endpoint)
        total_results = []

        if result:
            for competition in result:
                total_results.append({
                    Competition.NAME: competition['name'],
                    Competition.FASTEST_LIVE_SCORES_API_ID: competition['dbid'],
                })

        return total_results

    def request_teams(self):
        """
        Retrieve all the teams the API supports
        Mainly used for mapping existing teams in DB to the same team in API
        :return: List of teams
        """
        endpoint = self.build_endpoint(endpoint_name="teams")
        result = self.perform_get(built_uri=endpoint)
        total_results = []

        if result:
            for team in result:
                data = {
                    Team.NAME: team['name'],
                    Team.FASTEST_LIVE_SCORES_API_ID: team['dbid'],
                }
                if "defaultHomeVenue" in team:
                    stadium_details = team['defaultHomeVenue']
                    if stadium_details:
                        if "capacity" in stadium_details and stadium_details["capacity"]:
                            if stadium_details["capacity"] > 0:
                                data[Team.STADIUM_CAPACITY] = stadium_details["capacity"]

                        if "geolocation" in stadium_details and stadium_details["geolocation"]:
                            if "latitude" in stadium_details["geolocation"]:
                                data[Team.STADIUM_LAT] = stadium_details["geolocation"]["latitude"]

                            if "latitude" in stadium_details["geolocation"]:
                                data[Team.STADIUM_LONG] = stadium_details["geolocation"]["longitude"]

                total_results.append(data)

        return total_results



# if __name__ == "__main__":
#     fls = FastestLiveScores(api_key=os.getenv('FASTEST_LIVE_SCORES_API_KEY'))
#     print(fls.request_teams())


