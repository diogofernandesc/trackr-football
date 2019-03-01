from ingest_engine.football_data import FootballData
from ingest_engine.fastest_live_scores_api import FastestLiveScores
from ingest_engine.fantasy_api import Fantasy
from ingest_engine.cons import Competition
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
    stopwords = ['fifa', 'uefa']

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


    def request_player_details(self):
        """
        Join and retrieve player details from different sources
        :return:
        """

if __name__ == "__main__":
    driver = Driver()
    driver.request_competitions()