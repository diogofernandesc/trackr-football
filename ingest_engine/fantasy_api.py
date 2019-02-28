from ingest_engine.cons import *
from ingest_engine.cons import FANTASY_STATUS_MAPPER as st_mapper
from ingest_engine.api_integration import ApiIntegration
import os
import pandas as pd


def ingest_historical_gameweek_csv(csv_file, season):
    """
    Parse historical CSVs to json
    :param csv_file: CSV file with player or fixture information
    :param season: season description for historical ingest e.g. 201617 for 2016/2017
    :return: parsed json file
    """
    player_data = []
    gw_df = pd.read_csv(csv_file, encoding='utf-8')
    columns_to_drop = ['bonus', 'fixture', 'id', 'kickoff_time', 'ea_index',
                       'kickoff_time_formatted', 'loaned_in', 'loaned_out',
                       'team_a_score', 'team_h_score']

    for column in columns_to_drop:
        gw_df.drop(column, axis=1, inplace=True)

    field_names = (
        Player.NAME,
        Player.ASSISTS,
        Player.ATTEMPTED_PASSES,
        Player.BIG_CHANCES_CREATED,
        Player.BIG_CHANCES_MISSED,
        Player.FANTASY_TOTAL_BONUS,
        Player.CLEAN_SHEETS,
        Player.CLEARANCES_BLOCKS_INTERCEPTIONS,
        Player.COMPLETED_PASSES,
        Player.FANTASY_CREATIVITY,
        Player.DRIBBLES,
        Player.FANTASY_ID,
        Player.ERRORS_LEADING_TO_GOAL,
        Player.ERRORS_LEADING_TO_GOAL_ATTEMPT,
        Player.FOULS,
        Player.GOALS_CONCEDED,
        Player.NUMBER_OF_GOALS,
        Player.FANTASY_ICT_INDEX,
        Player.FANTASY_INFLUENCE,
        Player.KEY_PASSES,
        Player.MINUTES_PLAYED,
        Player.OFFSIDE,
        Player.OPEN_PLAY_CROSSES,
        Player.FANTASY_OPPONENT_TEAM_ID,
        Player.OWN_GOALS,
        Player.PENALTIES_CONCEDED,
        Player.PENALTIES_MISSED,
        Player.PENALTIES_SAVED,
        Player.RECOVERIES,
        Player.RED_CARDS,
        Player.FANTASY_WEEK,
        Player.SAVES,
        Player.FANTASY_SELECTION_COUNT,
        Player.TACKLED,
        Player.TACKLES,
        Player.TARGET_MISSED,
        Player.FANTASY_THREAT,
        Player.FANTASY_OVERALL_POINTS,
        Player.FANTASY_TRANSFERS_BALANCE,
        Player.FANTASY_WEEK_TRANSFERS_IN,
        Player.FANTASY_WEEK_TRANSFERS_OUT,
        Player.FANTASY_WEEK_VALUE,
        Player.PLAYED_AT_HOME,
        Player.WINNING_GOALS,
        Player.YELLOW_CARDS
    )
    gw_df.columns = field_names  # re-naming of columns
    gw_df = gw_df.transpose().to_dict()

    for player in gw_df.values():
        name = player[Player.NAME].split("_")
        player[Player.NAME] = " ".join(name)
        player[Player.FIRST_NAME] = name[0]
        player[Player.LAST_NAME] = name[1]
        player[Player.FANTASY_WEEK_ID] = int(f'{season}{str(player[Player.FANTASY_WEEK]).zfill(2)}')
        player_data.append(player)

    return player_data


def ingest_historical_base_csv(csv_file, season):
    """
    The equivalent to retrieving the base information at /bootstrap/ endpoint
    :param csv_file: csv file with the base information
    :param season: season string indicator
    :return: parsed CSV into json
    """
    player_data = []
    season_df = pd.read_csv(csv_file, encoding='utf-8')
    columns_to_drop = ['bonus']
    if season == '201718':
        columns_to_drop.append('now_cost')

    for column in columns_to_drop:
        season_df.drop(column, axis=1, inplace=True)

    field_names = (
        Player.FIRST_NAME,
        Player.LAST_NAME,
        Player.NUMBER_OF_GOALS,
        Player.ASSISTS,
        Player.FANTASY_OVERALL_POINTS,
        Player.MINUTES_PLAYED,
        Player.GOALS_CONCEDED,
        Player.FANTASY_CREATIVITY,
        Player.FANTASY_INFLUENCE,
        Player.FANTASY_THREAT,
        Player.FANTASY_TOTAL_BONUS,
        Player.FANTASY_ICT_INDEX,
        Player.CLEAN_SHEETS,
        Player.RED_CARDS,
        Player.YELLOW_CARDS,
        Player.FANTASY_SELECTION_PERCENTAGE,
    )

    season_df.columns = field_names
    season_df = season_df.transpose().to_dict()
    for player in season_df.values():
        player[Season.NAME] = season
        player_data.append(player)

    return player_data


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

    def request_player_data(self, player_id, season_summaries=True, fixture_data=True, fixture_codes=True):
        """
        Returns stats tracked by fantasy football for the footballer given by the player_id param
        :param player_id: ID of the player for which to retrieve fantasy football data
        :param season_summaries: Indicator of whether to retrieve historical summary season data for player
        :param fixture_data: Indicator of whether to retrieve player match data for their fixtures this season
        :param fixture_codes: Indicator of whether to output a list of fixture codes for player future fixtures
        :return: Parsed results for player info
        :rtype: dict
        """
        built_uri = f'element-summary/{player_id}'
        dict_result = {}
        result = self.perform_get(built_uri=self.uri+built_uri)
        if result:
            dict_result[Player.FANTASY_ID] = player_id
            if season_summaries:
                if "history_past" in result:
                    season_history = []
                    for entry in result['history_past']:
                        season_history.append({
                            Season.NAME: entry['season_name'],
                            Season.FANTASY_CODE: entry['season'],
                            Player.FANTASY_SEASON_START_PRICE: entry['start_cost'],
                            Player.FANTASY_SEASON_END_PRICE: entry['end_cost'],
                            Player.FANTASY_OVERALL_POINTS: entry['total_points'],
                            Player.MINUTES_PLAYED: entry['minutes'],
                            Player.NUMBER_OF_GOALS: entry['goals_scored'],
                            Player.ASSISTS: entry['assists'],
                            Player.CLEAN_SHEETS: entry['clean_sheets'],
                            Player.GOALS_CONCEDED: entry['goals_conceded'],
                            Player.OWN_GOALS: entry['own_goals'],
                            Player.PENALTIES_SAVED: entry['penalties_saved'],
                            Player.PENALTIES_MISSED: entry['penalties_missed'],
                            Player.YELLOW_CARDS: entry['yellow_cards'],
                            Player.RED_CARDS: entry['red_cards'],
                            Player.SAVES: entry['saves'],
                            Player.FANTASY_TOTAL_BONUS: entry['bps'],
                        })

                    dict_result['season_summaries'] = season_history

            if fixture_data:
                if 'history' in result:
                    match_history = []
                    for match in result['history']:
                        match_history.append({
                            Match.START_TIME: match['kickoff_time'],
                            Match.FULL_TIME_HOME_SCORE: match['team_h_score'],
                            Match.FULL_TIME_AWAY_SCORE: match['team_a_score'],
                            Player.PLAYED_AT_HOME: match['was_home'],
                            Player.FANTASY_WEEK_POINTS: match['total_points'],
                            Player.FANTASY_SEASON_VALUE: match['value'],
                            Player.FANTASY_TRANSFERS_BALANCE: match['transfers_balance'],
                            Player.FANTASY_SELECTION_COUNT: match['selected'],
                            Player.FANTASY_WEEK_TRANSFERS_IN: match['transfers_in'],
                            Player.FANTASY_WEEK_TRANSFERS_OUT: match['transfers_out'],
                            Player.MINUTES_PLAYED: match['minutes'],
                            Player.NUMBER_OF_GOALS: match['goals_scored'],
                            Player.ASSISTS: match['assists'],
                            Player.CLEAN_SHEETS: match['clean_sheets'],
                            Player.GOALS_CONCEDED: match['goals_conceded'],
                            Player.OWN_GOALS: match['own_goals'],
                            Player.PENALTIES_SAVED: match['penalties_saved'],
                            Player.PENALTIES_MISSED: match['penalties_missed'],
                            Player.YELLOW_CARDS: match['yellow_cards'],
                            Player.RED_CARDS: match['red_cards'],
                            Player.SAVES: match['saves'],
                            Player.FANTASY_WEEK_BONUS: match['bps'],
                            Player.FANTASY_INFLUENCE: match['influence'],
                            Player.FANTASY_CREATIVITY: match['creativity'],
                            Player.FANTASY_THREAT: match['threat'],
                            Player.FANTASY_ICT_INDEX: match['ict_index'],
                            Player.OPEN_PLAY_CROSSES: match['open_play_crosses'],
                            Player.BIG_CHANCES_CREATED: match['big_chances_created'],
                            Player.CLEARANCES_BLOCKS_INTERCEPTIONS: match['clearances_blocks_interceptions'],
                            Player.RECOVERIES: match['recoveries'],
                            Player.KEY_PASSES: match['key_passes'],
                            Player.TACKLES: match['tackles'],
                            Player.WINNING_GOALS: match['winning_goals'],
                            Player.ATTEMPTED_PASSES: match['attempted_passes'],
                            Player.COMPLETED_PASSES: match['completed_passes'],
                            Player.PENALTIES_CONCEDED: match['penalties_conceded'],
                            Player.BIG_CHANCES_MISSED: match['big_chances_missed'],
                            Player.ERRORS_LEADING_TO_GOAL: match['errors_leading_to_goal'],
                            Player.ERRORS_LEADING_TO_GOAL_ATTEMPT: match['errors_leading_to_goal_attempt'],
                            Player.TACKLED: match['tackled'],
                            Player.OFFSIDE: match['offside'],
                            Player.TARGET_MISSED: match['target_missed'],
                            Player.FOULS: match['fouls'],
                            Player.DRIBBLES: match['dribbles'],
                            Player.FANTASY_OPPONENT_TEAM_ID: match['opponent_team']
                        })

                    dict_result['season_match_history'] = match_history

            if fixture_codes:
                if 'fixtures' in result:
                    not_played = []
                    for fixture in result['fixtures']:
                        not_played.append(fixture["code"])

                    dict_result[Player.FUTURE_FIXTURES] = not_played

            return dict_result

    def request_matches(self):
        """
        Returns fixture (match) information from https://fantasy.premierleague.com/drf/fixtures/
        :return: Parsed list of fixtures from API endpoint
        :rtype: list
        """
        built_uri = 'fixtures'
        total_result = []
        result = self.perform_get(built_uri=self.uri + built_uri)
        if result:
            for match in result:
                if "kickoff_time" in match and match["kickoff_time"]:  # Filter for actual matches
                    match_data = {
                        Match.START_TIME: match["kickoff_time"],
                        Match.FINISHED: match['started'],
                        Match.FANTASY_GAME_WEEK: match["event"],
                        Match.FANTASY_HOME_TEAM_DIFFICULTY: match["team_h_difficulty"],
                        Match.FANTASY_AWAY_TEAM_DIFFICULTY: match["team_a_difficulty"],
                        Match.FANTASY_MATCH_CODE: match["code"],
                        Match.FULL_TIME_HOME_SCORE: match["team_h_score"],
                        Match.FULL_TIME_AWAY_SCORE: match["team_a_score"],
                        Match.MINUTES: match["minutes"],
                        Match.FANTASY_HOME_TEAM_CODE: match["team_h"],
                        Match.FANTASY_AWAY_TEAM_CODE: match["team_a"]
                    }

                    stats = match["stats"]
                    for stat in stats:
                        for stat_name, value in stat.items():
                            if stat_name not in match_data:
                                match_data[stat_name] = []

                            for side, side_value in value.items():
                                for entry in side_value:
                                    stat_result = {
                                        Match.GOAL_AMOUNT: entry["value"],
                                        Player.FANTASY_CODE: entry["element"],
                                        Match.SIDE: 'home' if side == 'h' else 'away'
                                    }
                                    match_data[stat_name].append(stat_result)

                    total_result.append(match_data)

        return total_result


if __name__ == "__main__":
    fantasy = Fantasy()
    current_path = os.path.dirname(os.path.abspath(__file__))
    current_path = "/".join(current_path.split("/")[:-1])

    # Extracting week by week player data
    for week_i in range(1, 38):
        # Season 2016-2017
        ingest_historical_gameweek_csv(csv_file=f'{current_path}/historical_fantasy/2016-17/gw{week_i}.csv',
                                       season='201617')

        # Season 2017-2018
        ingest_historical_gameweek_csv(csv_file=f'{current_path}/historical_fantasy/2017-18/gw{week_i}.csv',
                                       season='201718')

    # Extracting historical player information (GIVEN SEASON DETAILED SUMMARY INFORMATION - cleaned_players.csv)
    # This is equivalent to base information
    for season in ['2016-17', '2017-18']:
        ingest_historical_base_csv(csv_file=f'{current_path}/historical_fantasy/{season}/cleaned_players.csv',
                                   season="".join(season.split("-")))















