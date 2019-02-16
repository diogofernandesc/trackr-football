from ratelimit import limits, sleep_and_retry
import requests as re
import os
import json
from ingest_engine.api_integration import ApiIntegration
from ingest_engine.cons import Competition, Player, Team, Match, MatchEvent, FLS_STATES_MAPPER as state_mapper

HOUR = 3600


class FastestLiveScores(ApiIntegration):
    """
    Wrapper for API available at -> https://customer.fastestlivescores.com/
    """
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key
        if not api_key:
            self.api_key = os.environ.get('FASTEST_LIVE_SCORES_API_KEY')

    def build_endpoint(self, endpoint_name, **kwargs):
        """
        Create endpoint url used in API call based on endpoint name
        :param endpoint_name: the API resource path e.g. /competitions
        :return: Endpoint string
        """
        built_uri = f'https://api.crowdscores.com/v1/{endpoint_name}?api_key={self.api_key}'
        if kwargs:
            built_uri += '?'
            for name_filter, value in kwargs.items():
                built_uri += f'&{name_filter}={value}'

        return built_uri

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
            result = json.loads(request.text)
            if request.status_code == 400 or request.status_code == 404:
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

    def request_matches(self, **kwargs):
        """
        Request basic match information, max time interval is 7 days unless looking at specific team
        :param team_id: FLS team id for which to retrieve matches
        :param competition_id: FLS competition id for which to retrieve matches
        :param from_date: Matches started after this time Example: 2014-11-19T12:00:00-03:00
        :param to_date: Matches started before this time
        :return:
        """
        endpoint = self.build_endpoint(**kwargs, endpoint_name="matches")
        result = self.perform_get(built_uri=endpoint)
        total_result = []

        if result:
            for match in result:
                total_result.append({
                    Match.HOME_TEAM: match["homeTeam"]["name"],
                    Match.AWAY_TEAM: match["awayTeam"]["name"],
                    Match.FULL_TIME_HOME_SCORE: match["homeGoals"],
                    Match.FULL_TIME_AWAY_SCORE: match["awayGoals"],
                    Match.COMPETITION: match["competition"]["name"],
                    Match.FLS_API_COMPETITION_ID: match["competition"]["dbid"],
                    Match.SEASON_YEAR: match["season"]["name"],
                    Match.FLS_MATCH_ID: match["dbid"]
                })

        return total_result

    def request_match_details(self, match_id):
        """
        Gets specific information per match half, parsed
        :param match_id: MANDATORY FLS match id for which to retrieve details
        :return: Parsed match events and detailed for given match id
        :rtype: dict
        """
        endpoint = self.build_endpoint(endpoint_name=f"matches/{match_id}")
        result = self.perform_get(built_uri=endpoint)
        additional_data_endpoint = self.build_endpoint(endpoint_name=f"matches/{match_id}/additional-data")
        additional_data = self.perform_get(built_uri=additional_data_endpoint)
        match_events = []
        dict_result = {}

        if additional_data:
            if "additionalStats" in additional_data:
                additional_stats = additional_data["additionalStats"]
                dict_result[Match.HOME_SCORE_PROBABILITY] = additional_stats["home"]["probabilityToScore"]
                dict_result[Match.HOME_CONCEDE_PROBABILITY] = additional_stats["home"]["probabilityToConcede"]
                dict_result[Match.AWAY_SCORE_PROBABILITY] = additional_stats["away"]["probabilityToScore"]
                dict_result[Match.AWAY_CONCEDE_PROBABILITY] = additional_stats["away"]["probabilityToConcede"]
                dict_result[Match.HOME_FORM] = additional_stats["home"]["form"]
                dict_result[Match.AWAY_FORM] = additional_stats["away"]["form"]

                if "scoreBracketRecord" in additional_stats["home"]:
                    dict_result[Match.HOME_SCORE_PROBABILITY_OVER_1_5] = \
                        additional_stats["home"]["scoreBracketRecord"]["1.5"]["over"]

                    dict_result[Match.HOME_SCORE_PROBABILITY_OVER_2_5] = \
                        additional_stats["home"]["scoreBracketRecord"]["2.5"]["over"]

                    dict_result[Match.HOME_SCORE_PROBABILITY_OVER_3_5] = \
                        additional_stats["home"]["scoreBracketRecord"]["3.5"]["over"]

                    dict_result[Match.HOME_SCORE_PROBABILITY_UNDER_1_5] = \
                        additional_stats["home"]["scoreBracketRecord"]["1.5"]["under"]

                    dict_result[Match.HOME_SCORE_PROBABILITY_UNDER_2_5] = \
                        additional_stats["home"]["scoreBracketRecord"]["2.5"]["under"]

                    dict_result[Match.HOME_SCORE_PROBABILITY_UNDER_3_5] = \
                        additional_stats["home"]["scoreBracketRecord"]["3.5"]["under"]

                if "scoreBracketRecord" in additional_stats["away"]:
                    dict_result[Match.AWAY_SCORE_PROBABILITY_OVER_1_5] = \
                        additional_stats["away"]["scoreBracketRecord"]["1.5"]["over"]

                    dict_result[Match.AWAY_SCORE_PROBABILITY_OVER_2_5] = \
                        additional_stats["away"]["scoreBracketRecord"]["2.5"]["over"]

                    dict_result[Match.AWAY_SCORE_PROBABILITY_OVER_1_5] = \
                        additional_stats["away"]["scoreBracketRecord"]["3.5"]["over"]

                    dict_result[Match.AWAY_SCORE_PROBABILITY_UNDER_1_5] = \
                        additional_stats["away"]["scoreBracketRecord"]["1.5"]["under"]

                    dict_result[Match.AWAY_SCORE_PROBABILITY_UNDER_2_5] = \
                        additional_stats["away"]["scoreBracketRecord"]["2.5"]["under"]

                    dict_result[Match.AWAY_SCORE_PROBABILITY_UNDER_3_5] = \
                        additional_stats["away"]["scoreBracketRecord"]["3.5"]["under"]

            if "headToHead" in additional_data:
                head_to_head = additional_data["headToHead"]
                previous_encounters = []
                for encounter in head_to_head:
                    previous_encounters.append({
                        Match.HOME_TEAM_FLS_ID: encounter["homeTeam"]["dbid"],
                        Match.AWAY_TEAM_FLS_ID: encounter["awayTeam"]["dbid"],
                        Match.HOME_TEAM: encounter["homeTeam"]["name"],
                        Match.AWAY_TEAM: encounter["awayTeam"]["name"],
                        Match.START_TIME_EPOCH: encounter["start"],
                        Match.FULL_TIME_HOME_SCORE: encounter["homeGoals"],
                        Match.FULL_TIME_AWAY_SCORE: encounter["awayGoals"],
                        Match.WINNER: encounter["outcome"]["winner"],
                        Match.PENALTY_SHOOTOUT_SCORE: encounter["penaltyShootoutScore"]
                    })

                if previous_encounters:
                    dict_result[Match.PREVIOUS_ENCOUNTERS] = previous_encounters

        if result:
            if "matchevents" in result:
                result = result["matchevents"]

                for event in result:
                    match_time = event['matchTime']
                    data = {
                        MatchEvent.STATE: state_mapper.get(match_time['state']),
                        MatchEvent.MINUTES_PASSED: match_time['minutes'],
                        MatchEvent.ADDED_TIME: match_time['extra'],
                        Match.HOME_TEAM_FLS_ID: event['homeTeam']['dbid'],
                        Match.AWAY_TEAM_FLS_ID: event['awayTeam']['dbid'],
                        Match.FLS_MATCH_ID: event['matchId'],
                        MatchEvent.OCCURED_AT: event['happenedAt'],
                        MatchEvent.TYPE: event['type']
                    }

                    if Match.HOME_TEAM_FLS_ID not in dict_result:
                        dict_result[Match.HOME_TEAM_FLS_ID] = event['homeTeam']['dbid']

                    if Match.AWAY_TEAM_FLS_ID not in dict_result:
                        dict_result[Match.AWAY_TEAM_FLS_ID] = event['awayTeam']['dbid']

                    if 'scoringPlayer' in event:
                        if event['scoringPlayer']:
                            data[MatchEvent.SCORER_FLS_ID] = event['scoringPlayer']['dbid']

                    if 'assistingPlayer' in event:
                        if event['assistingPlayer']:
                            data[MatchEvent.ASSIST_FLS_ID] = event['assistingPlayer']['dbid']

                    match_events.append(data)

        if match_events:
            dict_result[Match.EVENTS] = match_events

        return dict_result

    def request_player_details(self, **kwargs):
        """
        Gets specific player information, given a number of filters from:
        Team_ids, round_ids, competition_ids, season_ids
        :param kwargs: Potential filters (as comma separated lists)
        :return: List of player details
        :rtype: list
        """
        endpoint = self.build_endpoint(**kwargs, endpoint_name="playerstats")
        result = self.perform_get(built_uri=endpoint)
        total_result = []

        if result:
            for detail in result:
                data = {
                    Player.NAME: detail['name'],
                    Player.WEIGHT: detail['weight'],
                    Player.GENDER: detail['gender'],
                    Player.TEAM: detail['team']['name'],
                    Player.TEAM_FLS_ID: detail['team']['dbid'],
                    Player.SHIRT_NUMBER: detail['number'],
                    Player.HEIGHT: detail['height'],
                    Player.DATE_OF_BIRTH_EPOCH: detail['dateOfBirth'],
                    Player.FASTEST_LIVE_SCORES_API_ID: detail['dbid'],
                    Player.POSITION: detail['position'],
                }

                if 'playerstats' in detail:
                    comp_stats = []
                    for stats in detail['playerstats']:
                        comp_stats.append({
                            Competition.NAME: stats['competitionName'],
                            Competition.FASTEST_LIVE_SCORES_API_ID: stats['competitionId'],
                            Player.ASSISTS: stats['assists'],
                            Player.NUMBER_OF_GOALS: stats['goals'],
                            Player.RED_CARDS: stats['redCards'],
                            Player.YELLOW_CARDS: stats['yellowCards']
                        })
                    data[Player.COMPETITION_STATS] = comp_stats

                total_result.append(data)

        return total_result


if __name__ == "__main__":
    fls = FastestLiveScores(api_key=os.getenv('FASTEST_LIVE_SCORES_API_KEY'))



