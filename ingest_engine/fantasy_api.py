from ratelimit import limits, sleep_and_retry
import requests as re
import os
import json
from ingest_engine.cons import Competition, Player, Team, Match, MatchEvent, FANTASY_STATUS_MAPPER as st_mapper
from ingest_engine.api_integration import ApiIntegration


class Fantasy(ApiIntegration):
    """
    Wrapper for API available at -> https://fantasy.premierleague.com/drf/
    """
    def __init__(self):
        super().__init__()
        self.uri = 'https://fantasy.premierleague.com/drf/'

    def request_base_information(self, full=False):
        """
        Base information from /bootstrap/ or /bootstrap-static/ endpoint
        /bootstrap/ call should only be run at database migration or export
        /bootstrap-static/ called per week for latest updates
        :param full: Determines whether or not to provide extra info e.g. team codes & field information
        :return: Player, team, field etc information
        :rtype: List
        """
        built_uri = 'bootstrap-static'
        if full:
            built_uri = 'bootstrap'

        total_result = {}

        result = self.perform_get(built_uri=self.uri+built_uri)
        if result:
            players = []
            for player in result['elements']:
                players.append({
                    Player.FANTASY_ID: player['id'],
                    Player.FANTASY_PHOTO_URL: player['photo'],
                    Player.FANTASY_TEAM_CODE: player['team_code'],
                    Player.FANTASY_TEAM_ID: player['team'],
                    Player.FANTASY_CODE: player['code'],
                    Player.FIRST_NAME: player['first_name'],
                    Player.LAST_NAME: player['last_name'],
                    Player.SHIRT_NUMBER: player['squad_number'],
                    Player.FANTASY_STATUS: st_mapper.get(player['status']),
                    Player.FANTASY_NEWS: player['news'],
                    Player.FANTASY_PRICE: player['now_cost'],
                    Player.FANTASY_NEWS_TIMESTAMP: player['news_added'],
                    Player.FANTASY_CHANCE_OF_PLAYING_THIS_WEEK: player['chance_of_playing_this_round'],
                    Player.FANTASY_CHANCE_OF_PLAYING_NEXT_WEEK: player['chance_of_playing_next_round'],
                    Player.FANTASY_SEASON_VALUE: player['value_season'],
                    Player.FANTASY_OVERALL_PRICE_RISE: player['cost_change_start'],
                    Player.FANTASY_WEEK_PRICE_RISE: player['cost_change_event'],
                    Player.FANTASY_OVERALL_PRICE_FALL: player['cost_change_start_fall'],
                    Player.FANTASY_WEEK_PRICE_FALL: player['cost_change_event_fall'],
                    Player.FANTASY_DREAM_TEAM_MEMBER: player['in_dreamteam'],
                    Player.FANTASY_DREAM_TEAM_COUNT: player['dreamteam_count'],
                    Player.FANTASY_SELECTION_PERCENTAGE: player['selected_by_percent'],
                    Player.FANTASY_FORM: player['form'],
                    Player.FANTASY_OVERALL_TRANSFERS_IN: player['transfers_in'],
                    Player.FANTASY_OVERALL_TRANSFERS_OUT: player['transfers_out'],
                    Player.FANTASY_WEEK_TRANSFERS_IN: player['transfers_in_event'],
                    Player.FANTASY_WEEK_TRANSFERS_OUT: player['transfers_out_event'],
                    Player.FANTASY_OVERALL_POINTS: player['total_points'],
                    Player.FANTASY_WEEK_POINTS: player['event_points'],
                    Player.FANTASY_POINT_AVERAGE: player['points_per_page'],
                    Player.FANTASY_ESTIMATED_WEEK_POINTS: player['ep_this'],
                    Player.FANTASY_ESTIMATED_NEXT_WEEK_POINTS: player['ep_next'],
                    Player.FANTASY_SPECIAL: player['special'],
                    Player.MINUTES_PLAYED: player['minutes'],
                    Player.NUMBER_OF_GOALS: player['goals_scored'],
                    Player.ASSISTS: player['assists'],
                    Player.CLEAN_SHEETS: player['clean_sheets'],
                    Player.GOALS_CONCEDED: player['goals_conceded'],
                    Player.OWN_GOALS: player['own_goals'],
                    Player.PENALTIES_SAVED: player['penalties_saved'],
                    Player.PENALTIES_MISSED: player['penalties_missed'],
                    Player.YELLOW_CARDS: player['yellow_cards'],
                    Player.RED_CARDS: player['red_cards'],
                    Player.SAVES: player['saves'],
                    Player.FANTASY_WEEK_BONUS: player['bonus'],
                    Player.FANTASY_TOTAL_BONUS: player['bps'],
                    Player.FANTASY_INFLUENCE: player['influence'],
                    Player.FANTASY_CREATIVITY: player['creativity'],
                    Player.FANTASY_THREAT: player['threat'],
                    Player.FANTASY_ICT_INDEX: player['ict_index'],
                })





if __name__ == "__main__":
    fantasy = Fantasy()
    fantasy.request_base_information(full=True)







