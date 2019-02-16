import requests as re
import json
import os
from ratelimit import limits, sleep_and_retry
from time import sleep
from ingest_engine.api_integration import ApiIntegration
from ingest_engine.cons import Competition, Match, Team, Standings, Player
from ingest_engine.cons import FootballDataApiFilters as fda

MINUTE = 60


class FootballData(ApiIntegration):
    """
    Wrapper for the football-data api available at https://www.football-data.org/documentation/api
    """

    def __init__(self, api_key=None):
        super().__init__(api_key=api_key)
        if not api_key:
            api_key = os.environ.get('FOOTBALL_DATA_API_KEY')
            self.session.headers.update({'X-Auth-Token': api_key})
        self.uri = 'http://api.football-data.org/v2/'
        self.api_key = api_key

    @sleep_and_retry
    @limits(calls=10, period=MINUTE)
    def perform_get(self, built_uri):
        """
        Performs GET request and deals with any issues arising from call
        Handles API rate limits
        :param built_uri: endpoint to attach to the base API url
        :return: dict result of call, {} if failed
        """

        result = self.session.get(url=self.uri + built_uri)
        try:
            result = json.loads(result.text)
            if built_uri == "matches?dateTo=2018-09-15&dateFrom=2018-09-05&":
                print("--------")
                print(f"API RESULT: {result}")
                print(f"THIS IS THE SESSION API KEY: {self.session.headers['X-Auth-Token']}")
                print(f"THIS IS THE SELF.API_KEY: {self.api_key}")
            if 'errorCode' in result:
                if result['errorCode'] == 429:
                    wait_time = [int(s) for s in result['message'].split() if s.isdigit()][0]
                    sleep(wait_time + 10)  # Wait for rate limiting to end before performing request again

                    # test get, seems API fails first request after rate limit
                    self.session.get(self.uri + 'competitions')

                    # Resume as necessary
                    self.perform_get(built_uri=built_uri)

                elif result['errorCode'] == 400:  # Buggy API endpoint results in faulty authentication
                    if 'message' in result:
                        if self.session.headers['X-Auth-Token'] != 'test':
                            sleep(5)  # Sleep and try again

                            print("IT GOT HEREEEEEEEEEE")
                            # test get, seems API fails first request after rate limit
                            # self.session.get(self.uri + 'competitions')

                            self.perform_get(built_uri=built_uri)

                        result = {}

                elif result['errorCode'] == 403:
                    result = {}

            elif 'error' in result:
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
            if comp:
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
        :rtype: list
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

    def request_competition_team(self, competition_id, season=None):
        """
        Lists team information for a particular competition
        :param competition_id: ID of the competition for which to request team information
        :param season: Available season filter
        :return: Parsed list of information for each team in competition
        :rtype: list
        """
        built_uri = f'competitions/{competition_id}/teams'

        # Check for any applied season filter
        if season:
            built_uri += f'?season={season}'

        result = self.perform_get(built_uri=built_uri)
        total_results = []
        if result:
            if 'teams' in result:
                for team in result['teams']:
                    total_results.append({
                        Team.FOOTBALL_DATA_ID: team['id'],
                        Team.NAME: team['name'],
                        Team.SHORT_NAME: team['shortName'],
                        Team.COUNTRY: team['area']['name'],
                        Team.CREST_URL: team['crestUrl'],
                        Team.ADDRESS: team['address'],
                        Team.PHONE: team['phone'],
                        Team.WEBSITE: team['website'],
                        Team.EMAIL: team['email'],
                        Team.YEAR_FOUNDED: team['founded'],
                        Team.CLUB_COLOURS: team['clubColors'],
                        Team.STADIUM: team['venue']
                    })

        return total_results

    def request_competition_standings(self, competition_id, standing_type=None):
        """
        Lists standing information for a particular competition
        :param competition_id: ID of the competition for which to request standings information
        :param standing_type: Filter available to endpoint: TOTAL | HOME | AWAY
        :return: Parsed list of information for standings in competition
        :rtype: List
        """
        built_uri = f'competitions/{competition_id}/standings'

        # Check for any applied season filter
        if standing_type:
            built_uri += f'?standingType={standing_type}'

        result = self.perform_get(built_uri=built_uri)
        total_results = []
        if result:
            if 'standings' in result:
                season_start_year = result['season']['startDate'].split("-")[0]
                season = f'{season_start_year}-{int(season_start_year)+1}'

                for standings in result['standings']:
                    data = {
                        Standings.STAGE: standings['stage'],
                        Standings.TYPE: standings['type'],
                        Standings.SEASON: season,
                        Standings.GROUP: standings['group'],
                        Standings.MATCH_DAY: result['season']['currentMatchday'],
                    }

                    table = []
                    for entry in standings['table']:
                        table.append({
                            Standings.POSITION: entry['position'],
                            Standings.TEAM_NAME: entry['team']['name'],
                            Standings.GAMES_PLAYED: entry['playedGames'],
                            Standings.GAMES_WON: entry['won'],
                            Standings.GAMES_DRAWN: entry['draw'],
                            Standings.GAMES_LOST: entry['lost'],
                            Standings.POINTS: entry['points'],
                            Standings.GOALS_FOR: entry['goalsFor'],
                            Standings.GOALS_AGAINST: entry['goalsAgainst'],
                            Standings.GOAL_DIFFERENCE: entry['goalDifference']
                        })

                    data[Standings.TABLE] = table
                    total_results.append(data)

        if result:
            return {
                Standings.COMPETITION_NAME: result['competition']['name'],
                'standings': total_results
            }

        return total_results

    def request_competition_scorers(self, competition_id, limit=None):
        """
        Lists standing information for a particular competition
        :param competition_id: ID of the competition for which to request scorer information
        :param limit: Limit result set from API (default 10)
        :return: Parsed list with scorer information for given competition
        :rtype: list
        """
        built_uri = f'competitions/{competition_id}/scorers'

        # Check for any applied season filter
        if limit:
            built_uri += f'?limit={limit}'

        result = self.perform_get(built_uri=built_uri)
        total_results = []
        if result:
            if 'scorers' in result:
                for scorer in result['scorers']:
                    player = scorer['player']
                    data = {
                        Player.NAME: player['name'],
                        Player.FIRST_NAME: player['firstName'],
                        Player.LAST_NAME: player['lastName'],
                        Player.DATE_OF_BIRTH: player['dateOfBirth'],
                        Player.COUNTRY_OF_BIRTH: player['countryOfBirth'],
                        Player.NATIONALITY: player['nationality'],
                        Player.POSITION: player['position'],
                        Player.SHIRT_NUMBER: player['shirtNumber'],
                        Player.TEAM: scorer['team']['name'],
                        Player.NUMBER_OF_GOALS: scorer['numberOfGoals']

                    }

                    if 'lastName' in player:
                        if player['lastName']:
                            data[Player.LAST_NAME] = player['lastName']

                        else:
                            data[Player.LAST_NAME] = player['name'].split(" ")[1]

                    total_results.append(data)

        return total_results

    def request_match(self, match_id=None, player_id=None, **kwargs):
        """
        Performs API request to retrieve all matches at URL -> /v2/matches
        Alternatively retrieve all matches for player at URL -> /v2/players/{id}/matches
        Retrieves matches across (a set of competitions) OR a particular ID match, or player
        :param match_id: Match id for match
        :param player_id: Player id
        :param kwargs: Dict of possible filters for the endpoint
        :return: dict result from call
        :rtype: dict
        """
        if match_id and player_id:
            raise ValueError('You cannot request a match passing match_id AND player_id')

        built_uri = f'matches?'
        if fda.ID in kwargs:
            built_uri += f'{kwargs.get(fda.ID)}'

        elif match_id:
            built_uri += f'{match_id}'

        elif player_id:
            built_uri += f'{player_id}'

        else:
            for name_filter, value in kwargs.items():
                built_uri += f'{name_filter}={value}&'

        result = self.perform_get(built_uri=built_uri)
        print(f"THIS IS THE RESULT WHEN YOU EXECUTE IT INSIDE REQUEST_MATCH(): {result}")
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
                        Match.AWAY_TEAM: match['awayTeam']['name'],
                        Match.FILTERS: result['filters']
                    }

                    refs = []
                    for ref in match['referees']:
                        refs.append(ref['name'])

                    if refs:
                        data[Match.REFEREES] = refs

                    total_results.append(data)

        return total_results

    def request_team(self, team_id):
        """
        Performs API request to retrieve specific team at URL -> v2/teams/{id}
        :param team_id: Football data ID for team
        :return: Parsed dict of team information
        :rtype: dict
        """
        built_uri = f'teams/{team_id}/'
        result = self.perform_get(built_uri=built_uri)
        data = {}

        if result:
            data = {
                Team.FOOTBALL_DATA_ID: result['id'],
                Team.NAME: result['name'],
                Team.SHORT_NAME: result['shortName'],
                Team.ACRONYM: result['tla'],
                Team.CREST_URL: result['crestUrl'],
                Team.ADDRESS: result['address'],
                Team.PHONE: result['phone'],
                Team.WEBSITE: result['website'],
                Team.EMAIL: result['email'],
                Team.YEAR_FOUNDED: result['founded'],
                Team.CLUB_COLOURS: result['clubColors'],
                Team.STADIUM: result['venue']
            }

            if 'activeCompetitions' in result:
                if result['activeCompetitions']:
                    active_competitions = []
                    for entry in result['activeCompetitions']:
                        active_competitions.append({
                            Competition.FOOTBALL_DATA_API_ID: entry['id'],
                            Competition.LOCATION: entry['area']['name'],
                            Competition.NAME: entry['name'],
                            Competition.CODE: entry['code'],
                        })

                    if active_competitions:
                        data[Team.ACTIVE_COMPETITIONS] = active_competitions

            if 'squad' in result:
                if result['squad']:
                    squad = []
                    for entry in result['squad']:
                        squad.append({
                            Player.NAME: entry['name'],
                            Player.POSITION: entry['position'],
                            Player.DATE_OF_BIRTH: entry['dateOfBirth'],
                            Player.COUNTRY_OF_BIRTH: entry['countryOfBirth'],
                            Player.NATIONALITY: entry['nationality'],
                            Player.SHIRT_NUMBER: entry['shirtNumber'],
                            Team.SQUAD_ROLE: entry['role']
                        })

                    if squad:
                        data[Team.SQUAD] = squad

        return data

    def request_player(self, player_id):
        """
        Performs API request to retrieve specific player at URL -> v2/players/{id}
        :param player_id: Football data player ID
        :return: Parsed player information
        :rtype: dict
        """
        built_uri = f'players/{player_id}/'
        result = self.perform_get(built_uri=built_uri)
        data = {}

        if result:
            data[Player.FIRST_NAME] = result['firstName']
            data[Player.DATE_OF_BIRTH] = result['dateOfBirth']
            data[Player.COUNTRY_OF_BIRTH] = result['countryOfBirth']
            data[Player.NATIONALITY] = result['nationality']
            data[Player.POSITION] = result['position']
            data[Player.SHIRT_NUMBER] = result['shirtNumber']

        if 'lastName' in result:
            if result['lastName']:
                data[Player.LAST_NAME] = result['lastName']

            elif " " in result['name']:
                data[Player.LAST_NAME] = result['name'].split(" ")[1]

            elif result['name'] != result['firstName']:
                data[Player.LAST_NAME] = result['name']

        return data


if __name__ == "__main__":
    fd = FootballData(api_key=os.getenv("FOOTBALL_DATA_API_KEY"))
    # print(fd.request_player(player_id=1))

# print(fd.request_competition_scorers(competition_id=2002))
# print(fd.request_competition_standings(competition_id=2002))
# print(fd.request_competition_team(competition_id=2002, season=2017))
# print(fd.request_match(**{fda.TO_DATE: '2018-09-15', fda.FROM_DATE: '2018-09-05'}))
# fd.session.get('http://api.football-data.org/v2/competitions')
# api_res = fd.request_competitions(2002)
# print(api_res)
# fd.parse_competitions(api_res=api_res)


