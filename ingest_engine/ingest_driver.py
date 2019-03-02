from ingest_engine.football_data import FootballData
from ingest_engine.fastest_live_scores_api import FastestLiveScores
from ingest_engine.fantasy_api import Fantasy, team_mapper
from ingest_engine.cons import Competition, Match, Team
from ingest_engine.cons import FootballDataApiFilters as fdf
from ingest_engine.cons import FLSApiFilters as flsf
from Levenshtein import ratio
import re


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

    def request_match(self, competition_name, game_week, season):
        """
        Retrieve the match details
        :param competition_name: Name of the competition for which to retrieve matches
        :param game_week: 1, 2, 3....n
        :param season: Identifier for the season e.g. 2018-2019 (for football-data API)
        :return: Matches over a given gameweek for a given competition and season
        :rtype: list
        """
        # Placeholder
        competition_id = 2002
        # In FLS, 2 is id for premier league, 2021 in football-data
        # TODO: Database query based on competition name and retrieve fd_id and fls_id
        # Testing
        fls_comp_id = 2
        fd_comp_id = 2021

        joint_matches = []
        fantasy_matches = self.fantasy.request_matches()
        fd_matches = self.fd.request_competition_match(competition_id=fd_comp_id,
                                                       **{fdf.MATCHDAY: game_week, fdf.SEASON: season})

        game_week_start = f'{fd_matches[0][Match.MATCH_UTC_DATE].split("T")[0]}T00:00:00'
        fls_matches = self.fls.request_matches(**{flsf.COMPETITION_ID: fls_comp_id,
                                                  flsf.FROM_DATETIME: game_week_start})

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
                    temp_dict2 = {**temp_dict, **adv_match_details}
                    for f_match in fantasy_matches:
                        f_home_team = team_mapper(f_match[Match.FANTASY_HOME_TEAM_ID])
                        f_away_team = team_mapper(f_match[Match.FANTASY_AWAY_TEAM_ID])
                        if f_match[Match.START_TIME] == match_start_datetime:
                            if f_home_team in home_team and f_away_team in away_team and \
                                    home_score == f_match[Match.FULL_TIME_HOME_SCORE] and \
                                    away_score == f_match[Match.FULL_TIME_AWAY_SCORE]:
                                final_dict = {**f_match, **temp_dict2}
                                joint_matches.append(final_dict)

        return joint_matches

    def request_teams(self, competition_name, season):
        """
        Retrieve team information from a given competition
        :param competition_name: name of the competition
        :param season: 4 digit integer representing the season for which to retrieve info
        :return: list of team info
        :rtype: list
        """
        # In FLS, 2 is id for premier league, 2021 in football-data
        # TODO: Database query based on competition name and retrieve fd_id and fls_id for teams
        # Testing
        fls_comp_id = 2
        fd_comp_id = 2021

        joint_teams = []
        fd_teams = self.fd.request_competition_team(competition_id=fd_comp_id, season=2018)
        for idx, team in enumerate(fd_teams):
            fd_team_extra = self.fd.request_team(team_id=team[Team.FOOTBALL_DATA_ID])
            fd_teams[idx] = {**team, **fd_team_extra}

        fls_teams = self.fls.request_teams(**{flsf.COMPETITION_ID: fls_comp_id})
        f_teams = self.fantasy.request_base_information()['teams']

        for fd_team in fd_teams:
            temp_dict = {}
            team_name = fd_team[Team.NAME]
            for fls_team in fls_teams:
                # if team_name in fls_team[Team.NAME] or fls_team[Team.NAME] in team_name:
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





    def request_player_details(self):
        """
        Join and retrieve player details from different sources
        :return:
        """
        pass


if __name__ == "__main__":
    driver = Driver()
    print(driver.request_teams("banter", 2018))
    # print(driver.request_match("banter", game_week=1, season=2018))
    # driver.request_competitions()
