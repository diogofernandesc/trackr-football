from datetime import datetime, timedelta
from itertools import filterfalse

from ingest_engine.football_data import FootballData
from ingest_engine.fastest_live_scores_api import FastestLiveScores
from ingest_engine.fantasy_api import Fantasy, team_mapper, ingest_historical_base_csv, ingest_historical_gameweek_csv
from ingest_engine.cons import Competition, Match, Team, Player
from ingest_engine.cons import FootballDataApiFilters as fdf
from ingest_engine.cons import FLSApiFilters as flsf
from Levenshtein import ratio
import re
import os


def str_comparator(str1, str2):
    """
    Implements levenshtein distance algorithm to calculate similarity between two strings
    :param str1: first string to compare against
    :param str2: second string to compare against
    :return: Whether str1 and str2 are the same
    """

    # Clean strings for stop words
    stopwords = ['fifa', 'uefa', 'afc', 'fc', 'cf', 'sl']
    str1 = ' '.join([word.lower() for word in str1.split() if word.lower() not in stopwords])
    str2 = ' '.join([word.lower() for word in str2.split() if word.lower() not in stopwords])

    pattern = re.compile(r'^{%s}$' % str2)

    similarity = str1 == str2
    if similarity:
        return 1

    elif pattern.match(str1):
        return 0.99

    else:
        similarity = ratio(str1, str2)
        return similarity


class Driver(object):
    """
    Class responsible for handling the merger of different sources into seperate methods that are called for ingest
    """

    def __init__(self):
        self.fd = FootballData()
        self.fls = FastestLiveScores()
        self.fantasy = Fantasy()

        # Indicator of whether or not historical fantasy data has been collected
        self.historical_player_data_collected = False
        self.historical_fantasy_gameweek_data = []
        self.historical_fantasy_base_data = []

    def request_competitions(self):
        """
        Joins competition information from Football-data and FLS together
        :return: Competition info from both APIs
        :rtype: list
        """
        comp_comparator = {}  # keep track of 1 - 1 matching of competitions
        fd_competitions = self.fd.request_competitions()
        fls_competitions = self.fls.request_competitions()
        for comp in fd_competitions:
            comp_name = comp[Competition.NAME]
            location = comp[Competition.LOCATION]
            for fls_comp in fls_competitions:
                comp_name_comparison_score = str_comparator(comp_name, fls_comp[Competition.NAME])
                comp_loc_comparison_score = str_comparator(location, fls_comp[Competition.LOCATION])
                if comp_name_comparison_score >= 0.9 and comp_loc_comparison_score >= 0.9:
                    if comp[Competition.FOOTBALL_DATA_API_ID] not in comp_comparator:
                        comp_comparator[comp[Competition.FOOTBALL_DATA_API_ID]] = (fls_comp, comp_name_comparison_score)

                    else:
                        if comp_comparator[comp[Competition.FOOTBALL_DATA_API_ID]][1] < comp_name_comparison_score:
                            comp_comparator[comp[Competition.FOOTBALL_DATA_API_ID]] = \
                                (fls_comp, comp_name_comparison_score)

        joint_competition_info = []
        for fd_comp_id, fls_comp_info in comp_comparator.items():
            for comp in fd_competitions:
                if comp[Competition.FOOTBALL_DATA_API_ID] == fd_comp_id:
                    # Atm, just extraction the API ID for the competition and nothing else
                    comp[Competition.FASTEST_LIVE_SCORES_API_ID] = \
                        fls_comp_info[0][Competition.FASTEST_LIVE_SCORES_API_ID]

                    joint_competition_info.append(comp)

        return joint_competition_info

    def request_standings(self, competition_id, standing_type=None):
        """
        Retrieves standings for a given competition
        :param competition_id: football-data competition id for which to retrieve standings
        :param standing_type: TOTAL | HOME | AWAY - different standings depending on this
        :return: standings information
        :rtype: dict
        """
        return self.fd.request_competition_standings(competition_id=competition_id, standing_type=standing_type)

    def request_match(self, fls_comp_id, fd_comp_id, game_week, season):
        """
        Retrieve the match details
        :param fls_comp_id: FLS comp id
        :param fd_comp_id: footballdata comp id
        :param game_week: 1, 2, 3....n
        :param season: Identifier for the season e.g. 2018-2019 (for football-data API)
        :return: Matches over a given gameweek for a given competition and season
        :rtype: list
        """
        # Placeholder
        # competition_id = 2002
        # In FLS, 2 is id for premier league, 2021 in football-data
        # fls_comp_id = 2
        # fd_comp_id = 2021

        if type(season) == str:
            season = int(season.split("-")[0])

        joint_matches = []
        # fantasy_matches = self.fantasy.request_matches()
        fd_matches = self.fd.request_competition_match(competition_id=fd_comp_id,
                                                       **{fdf.MATCHDAY: game_week, fdf.SEASON: season})

        game_week_start = datetime.strptime(fd_matches[0][Match.MATCH_UTC_DATE], '%Y-%m-%dT%H:%M:%SZ')
        game_week_end = game_week_start + timedelta(days=4)  # 4 days per game week
        fls_matches = self.fls.request_matches(**{flsf.FROM_DATETIME: game_week_start,
                                                  flsf.TO_DATETIME: game_week_end})

        fls_matches = list(filterfalse(lambda x: x[Match.FLS_API_COMPETITION_ID] != fls_comp_id, fls_matches))

        for match in fd_matches:
            match_start_datetime = match[Match.MATCH_UTC_DATE]
            home_team = match[Match.HOME_TEAM]
            away_team = match[Match.AWAY_TEAM]
            home_score = match[Match.FULL_TIME_HOME_SCORE]
            away_score = match[Match.FULL_TIME_AWAY_SCORE]
            for fls_match in fls_matches:
                if fls_match[Match.HOME_TEAM] in home_team and fls_match[Match.AWAY_TEAM] in away_team and \
                        home_score == fls_match[Match.FULL_TIME_HOME_SCORE] and \
                        away_score == fls_match[Match.FULL_TIME_AWAY_SCORE]:
                    temp_dict = {**match, **fls_match}
                    adv_match_details = self.fls.request_match_details(match_id=fls_match[Match.FLS_MATCH_ID])
                    final_dict = {**temp_dict, **adv_match_details}
                    joint_matches.append(final_dict)
                    # for f_match in fantasy_matches:
                    #     f_home_team = team_mapper(f_match[Match.FANTASY_HOME_TEAM_ID])
                    #     f_away_team = team_mapper(f_match[Match.FANTASY_AWAY_TEAM_ID])
                    #     if f_match[Match.START_TIME] == match_start_datetime:
                    #         if f_home_team in home_team and f_away_team in away_team and \
                    #                 home_score == f_match[Match.FULL_TIME_HOME_SCORE] and \
                    #                 away_score == f_match[Match.FULL_TIME_AWAY_SCORE]:
                    #             final_dict = {**f_match, **temp_dict2}
                    #             # final_dict = {**f_match, **temp_dict}
                    #             joint_matches.append(final_dict)

        return joint_matches

    def request_teams(self, fd_comp_id, fls_comp_id, season):
        """
        Retrieve team information from a given competition
        :param fls_comp_id: Competition id from FLS
        :param fd_comp_id: Competition id from FootballData.org
        :param season: season for which to retrieve info
        :return: list of team info
        :rtype: list
        """
        # In FLS, 2 is id for premier league, 2021 in football-data
        #   TODO: Database query based on competition name and retrieve fd_id and fls_id for teams
        # Testing
        # fls_comp_id = 2
        # fd_comp_id = 2021

        joint_teams = []
        fd_teams = self.fd.request_competition_team(competition_id=fd_comp_id, season=season)
        for idx, team in enumerate(fd_teams):
            fd_team_extra = self.fd.request_team(team_id=team[Team.FOOTBALL_DATA_ID])
            fd_teams[idx] = {**team, **fd_team_extra}

        fls_teams = self.fls.request_teams(**{flsf.COMPETITION_ID: fls_comp_id})
        f_teams = self.fantasy.request_base_information()['teams']

        for fd_team in fd_teams:
            temp_dict = {}
            team_name = fd_team[Team.NAME]
            for fls_team in fls_teams:
                if str_comparator(team_name, fls_team[Team.NAME]) >= 0.9:
                    temp_dict = {**fls_team, **fd_team}
                    break

            for f_team in f_teams:
                # if team_name in f_team[Team.NAME] or f_team[Team.NAME] in team_name:
                f_team[Team.NAME] = team_mapper(f_team[Team.FANTASY_ID])
                if str_comparator(team_name, f_team[Team.NAME]) >= 0.9:
                    final_dict = {**f_team, **temp_dict}

                    joint_teams.append(final_dict)
                    break

        return joint_teams

    def get_historical_fantasy_data(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        current_path = "/".join(current_path.split("/")[:-1])
        for week_i in range(1, 38):
            # Season 2016-2017
            temp_list = self.historical_fantasy_gameweek_data

            # Merge the current record of historical gameweek data with this one
            self.historical_fantasy_gameweek_data =\
                ingest_historical_gameweek_csv(csv_file=f'{current_path}/historical_fantasy/2016-17/gw{week_i}.csv',
                                               season='201617') + temp_list

            temp_list = self.historical_fantasy_gameweek_data
            # Season 2017-2018
            self.historical_fantasy_gameweek_data = \
                ingest_historical_gameweek_csv(csv_file=f'{current_path}/historical_fantasy/2017-18/gw{week_i}.csv',
                                               season='201718') + temp_list

        for season in ['2016-17', '2017-18']:
            temp_list = self.historical_fantasy_base_data
            self.historical_fantasy_base_data =  ingest_historical_base_csv(
                csv_file=f'{current_path}/historical_fantasy/{season}/cleaned_players.csv',
                season="".join(season.split("-"))) + temp_list

    def request_player_details(self, team_fls_id):
        """
        Join and retrieve player details from different sources, parsing and joining same player info
        :param team_fls_id: fastest-live-scores-api ID for the team the player plays for
        :return: List of player details from a given team
        :rtype: list
        """
        total_players = []

        # Liverpool example
        # Liverpool FD id = 64, FLS = 1
        # In FLS, 2 is id for premier league, 2021 in football-data
        # Testing
        # fls_comp_id = 2
        # fd_comp_id = 2021
        fls_players = self.fls.request_player_details(**{flsf.TEAM_IDS: team_fls_id})
        f_players_base = self.fantasy.request_base_information()['players']

        # Join together data from fantasy football
        for idx, player in enumerate(f_players_base):
            extra_player_data = self.fantasy.request_player_data(player_id=player[Player.FANTASY_ID])
            f_players_base[idx] = {**extra_player_data, **player}

        for player in fls_players:
            for f_player in f_players_base:
                if str_comparator(player[Player.NAME], f_player[Player.NAME]) >= 0.8:
                    final_dict = {**player, **f_player}
                    total_players.append(final_dict)

                elif str_comparator(player[Player.NAME].split(" ")[0], f_player[Player.FIRST_NAME]) >= 0.8 or \
                        str_comparator(player[Player.NAME].split(" ")[0], f_player[Player.FANTASY_WEB_NAME]) >= 0.8:
                    if str_comparator(player[Player.TEAM], team_mapper(f_player[Player.FANTASY_TEAM_ID])) >= 0.8:
                        final_dict = {**player, **f_player}
                        total_players.append(final_dict)

        return total_players


if __name__ == "__main__":
    driver = Driver()
    # print(driver.request_standings(competition_id=2021))
    # print(driver.request_player_details(team_fls_id=1))
    # print(driver.request_player_details(team_name="Liverpool", competition_name="test"))
    # print(driver.request_teams("banter", 2018))
    print(driver.request_match(fls_comp_id=2,fd_comp_id=2021,game_week=37,season='2018-2019'))
    # print(driver.request_match("banter", game_week=1, season=2018))
    # print(driver.request_competitions())


    # Ingesting competition data into DB

