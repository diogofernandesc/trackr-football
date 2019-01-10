import requests as re
import json
import os
from ingest_engine.cons import Competition, Match
from ingest_engine.cons import FootballDataApiFilters as fda


class FootballData(object):
    """
    Wrapper for the football-data api available at https://www.football-data.org/documentation/api
    """

    def __init__(self, api_key=None):
        self.session = re.Session()
        if not api_key:
            api_key = os.environ.get('FOOTBALL_DATA_API_KEY')
        self.session.headers.update({'X-Auth-Token': api_key})
        self.uri = 'http://api.football-data.org/v2/'

    def perform_get(self, built_uri):
        '''
        Performs GET request and deals with any issues arising from call
        :param built_uri: endpoint to attach to the base API url
        :return: dict result of call, {} if failed
        '''
        result = self.session.get(url=self.uri + built_uri)
        try:
            result = json.loads(result.text)
            if 'errorCode' in result or 'error' in result:
                result = {}
        except re.exceptions.ConnectionError:
            result = {}

        return result

    def request_competitions(self, competition_id=None):
        """
        Performs API request to retrieve all competitions at URL -> /v2/competitions
        OR specific competitions at URL -> /v2/competitions/2000,2002,3001...
        :rtype dict
        :param competition_id: Id of competition when getting specific competition results
        :return: Request result for competitions endpoint
        """
        built_uri = 'competitions/'
        if competition_id:
            built_uri += str(competition_id)

        result = self.perform_get(built_uri=built_uri)

        total_results = []
        if 'competitions' in result:
            api_res = result['competitions']

        else:
            api_res = [result]

        for comp in api_res:
            dict_result = {
                Competition.NAME: comp['name'],
                Competition.CODE: comp['code'],
                Competition.LOCATION: comp['area']['name'],
                Competition.FOOTBALL_DATA_API_ID: comp['id']
            }
            total_results.append(dict_result)

        return total_results

    def request_competition_match(self, competition_id, **kwargs):
        """
        Requests matches belonging to a competition (with mandatory ID passed)
        :param competition_id: REQUIRED competition id to retrieves matches for
        :param kwargs: All possible filters applicable to this endpoint /v2/competitions/{id}/matches
        :return: Request result for match competitions endpoint
        :rtype: dict
        """
        built_uri = f'competitions/{competition_id}/matches'

        # Check for any applied filters
        if kwargs:
            built_uri += '?'
            for name_filter, value in kwargs.items():
                built_uri += f'{name_filter}={value}&'

        result = self.perform_get(built_uri=built_uri)
        total_results = []
        if result:
            if 'matches' in result:
                for match in result['matches']:
                    data = {
                        Match.SEASON_FOOTBALL_DATA_ID: match[Match.ID],
                        Match.SEASON_START_DATE: match['season']['startDate'],
                        Match.SEASON_END_DATE: match['season']['endDate'],
                        Match.MATCH_UTC_DATE: match['utcDate'],
                        Match.STATUS: match['status'],
                        Match.MATCHDAY: match['matchday'],
                        Match.FULL_TIME_HOME_SCORE: match['score']['fullTime']['homeTeam'],
                        Match.FULL_TIME_AWAY_SCORE: match['score']['fullTime']['awayTeam'],
                        Match.HALF_TIME_HOME_SCORE: match['score']['halfTime']['homeTeam'],
                        Match.HALF_TIME_AWAY_SCORE: match['score']['halfTime']['awayTeam'],
                        Match.EXTRA_TIME_HOME_SCORE: match['score']['extraTime']['homeTeam'],
                        Match.EXTRA_TIME_AWAY_SCORE: match['score']['extraTime']['awayTeam'],
                        Match.PENALTY_HOME_SCORE: match['score']['penalties']['homeTeam'],
                        Match.PENALTY_AWAY_SCORE: match['score']['penalties']['awayTeam'],
                        Match.WINNER: match['score']['winner'],
                        Match.HOME_TEAM: match['homeTeam']['name'],
                        Match.AWAY_TEAM: match['awayTeam']['name']
                    }

                    refs = []
                    for ref in match['referees']:
                        refs.append(ref['name'])

                    if refs:
                        data[Match.REFEREES] = refs

                    total_results.append(data)

        return total_results

    def request_match(self, match_id=None,  **kwargs):
        """
        Performs API request to retrieve all matches at URL -> /v2/matches
        Retrieves matches across (a set of competitions) OR a particular ID match
        :param match_id: Match id for match
        :param kwargs: Dict of possible filters for the endpoint
        :return: dict result from call
        :rtype: dict
        """
        built_uri = f'matches?'
        if fda.ID in kwargs:
            built_uri += f'{kwargs.get(fda.ID)}'

        elif match_id:
            built_uri += f'{match_id}'

        else:
            for name_filter, value in kwargs.items():
                built_uri += f'{name_filter}={value}&'

        return self.perform_get(built_uri=built_uri)

    def parse_competitions(self, api_res):
        """
        Parse competition results from API request ready for database insertion/update/other
        :rtype: list
        :param api_res: The dict result from API call to the competitions endpoint
        :return: Parsed results from API in list of dicts format
        """
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



fd = FootballData()

print(fd.request_competition_match(competition_id=2002))
# print(fd.request_match(**{fda.TO_DATE: '2018-09-15', fda.FROM_DATE: '2018-09-05'}))
# fd.session.get('http://api.football-data.org/v2/competitions')
# api_res = fd.request_competitions(2002)
# print(api_res)
# fd.parse_competitions(api_res=api_res)


