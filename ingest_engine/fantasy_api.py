from ingest_engine.cons import *
from ingest_engine.cons import FANTASY_STATUS_MAPPER as st_mapper
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
            teams = []
            game_weeks = []
            for player in result['elements']:
                players.append({
                    Player.FANTASY_ID: player['id'],
                    Player.FANTASY_PHOTO_URL: player['photo'],
                    Player.FANTASY_TEAM_CODE: player['team_code'],
                    Player.FANTASY_TEAM_ID: player['team'],
                    Player.FANTASY_CODE: player['code'],
                    Player.FIRST_NAME: player['first_name'],
                    Player.LAST_NAME: player['second_name'],
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
                    Player.FANTASY_SELECTION_PERCENTAGE: float(player['selected_by_percent']),
                    Player.FANTASY_FORM: player['form'],
                    Player.FANTASY_OVERALL_TRANSFERS_IN: player['transfers_in'],
                    Player.FANTASY_OVERALL_TRANSFERS_OUT: player['transfers_out'],
                    Player.FANTASY_WEEK_TRANSFERS_IN: player['transfers_in_event'],
                    Player.FANTASY_WEEK_TRANSFERS_OUT: player['transfers_out_event'],
                    Player.FANTASY_OVERALL_POINTS: player['total_points'],
                    Player.FANTASY_WEEK_POINTS: player['event_points'],
                    Player.FANTASY_POINT_AVERAGE: float(player['points_per_game']),
                    Player.FANTASY_ESTIMATED_WEEK_POINTS: float(player['ep_this']),
                    Player.FANTASY_ESTIMATED_NEXT_WEEK_POINTS: float(player['ep_next']),
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
                    Player.FANTASY_INFLUENCE: float(player['influence']),
                    Player.FANTASY_CREATIVITY: float(player['creativity']),
                    Player.FANTASY_THREAT: float(player['threat']),
                    Player.FANTASY_ICT_INDEX: float(player['ict_index']),
                    Player.FANTASY_WEEK: result['current-event']
                })

            if 'teams' in result:
                for team in result['teams']:
                    teams.append({
                        Team.FANTASY_CODE: team['code'],
                        Team.FANTASY_WEEK_STRENGTH: team['strength'],
                        Team.FANTASY_OVERALL_HOME_STRENGTH: team['strength_overall_home'],
                        Team.FANTASY_OVERALL_AWAY_STRENGTH: team['strength_overall_away'],
                        Team.FANTASY_ATTACK_HOME_STRENGTH: team['strength_attack_home'],
                        Team.FANTASY_ATTACK_AWAY_STRENGTH: team['strength_attack_away'],
                        Team.FANTASY_DEFENCE_HOME_STRENGTH: team['strength_defence_home'],
                        Team.FANTASY_DEFENCE_AWAY_STRENGTH: team['strength_defence_away']
                    })

            if 'events' in result:
                for game_week in result['events']:
                    game_weeks.append({
                        FantasyGameWeek.FANTASY_ID: game_week['id'],
                        FantasyGameWeek.NAME: game_week['name'],
                        FantasyGameWeek.DEADLINE_TIME: game_week['deadline_time'],
                        FantasyGameWeek.DEADLINE_TIME_EPOCH: game_week['deadline_time_epoch'],
                        FantasyGameWeek.AVERAGE_SCORE: game_week['average_entry_score'],
                        FantasyGameWeek.HIGHEST_SCORE: game_week['highest_score'],
                        FantasyGameWeek.FINISHED: game_week['finished']
                    })

            if players:
                total_result['players'] = players

            if teams:
                total_result['teams'] = teams

            if game_weeks:
                total_result['game_weeks'] = game_weeks

        return total_result


if __name__ == "__main__":
    fantasy = Fantasy()
    print(fantasy.request_base_information(full=False))







