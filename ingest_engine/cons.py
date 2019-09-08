class FootballDataApiFilters:
    '''
    https://www.football-data.org/documentation/quickstart
    '''
    ID = 'id'
    MATCHDAY = 'matchday'  # Integer 0-49
    SEASON = 'season'  # Integer for starting year e.g. 2018

    STATUS = 'status'  # SCHEDULED | LIVE | IN_PLAY | PAUSED | FINISHED | POSTPONED | SUSPENDED | CANCELLED
    STATUS_SCHEDULED = 'SCHEDULED'
    STATUS_LIVE = 'LIVE'
    STATUS_IN_PLAY = 'IN_PLAY'
    STATUS_PAUSED = 'PAUSED'
    STATUS_FINISHED = 'FINISHED'
    STATUS_POSTPONED = 'POSTPONED'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_CANCELLED = 'CANCELED'

    VENUE = 'venue'  # HOME | AWAY
    VENUE_HOME = 'HOME'
    VENUE_AWAY = 'AWAY'

    FROM_DATE = 'dateFrom'  # Date string e.g. 2018-06-22
    TO_DATE = 'dateTo'  # Date string e.g. 2018-06-22

    STAGE = 'stage'

    PLAN = 'plan'  # TIER_ONE | TIER_TWO | TIER_THREE | TIER_FOUR
    PLAN_TIER_ONE = 'TIER_ONE'
    PLAN_TIER_TWO = 'TIER_TWO'
    PLAN_TIER_THREE = 'TIER_THREE'
    PLAN_TIER_FOUR = 'TIER_FOUR'

    COMPETITIONS = 'competitions'  # Comma separated list of competition ids
    GROUPS = 'group'
    LIMIT = 'limit'  # Limit result set, default = 10

    STANDING_TYPE = 'standingType'  # TOTAL | HOME | AWAY
    STANDING_HOME = 'HOME'
    STANDING_AWAY = 'AWAY'


class FLSApiFilters:
    FROM_DATETIME = 'from'
    TO_DATETIME = 'to'
    COMPETITION_ID = 'competition_id'
    TEAM_ID = 'team_id'
    TEAM_IDS = 'team_ids'


class Match:
    ID = 'id'
    FOOTBALL_DATA_ID = 'match_fd_id'
    SEASON_FOOTBALL_DATA_ID = 'season_football_data_id'
    SEASON_START_DATE = 'season_start_date'
    SEASON_END_DATE = 'season_end_date'
    SEASON_YEAR = 'season_year'
    MATCH_UTC_DATE = 'utc_date'
    START_TIME_EPOCH = 'start_time_epoch'
    START_TIME = 'start_time'
    STATUS = 'status'
    MATCHDAY = 'match_day'
    FULL_TIME_HOME_SCORE = 'ft_home_score'
    FULL_TIME_AWAY_SCORE = 'ft_away_score'
    HALF_TIME_HOME_SCORE = 'ht_home_score'
    HALF_TIME_AWAY_SCORE = 'ht_away_score'
    EXTRA_TIME_HOME_SCORE = 'et_home_score'
    EXTRA_TIME_AWAY_SCORE = 'et_away_score'
    PENALTY_HOME_SCORE = 'p_home_score'
    PENALTY_AWAY_SCORE = 'p_away_score'
    WINNER = 'winner'
    HOME_TEAM = 'home_team'
    AWAY_TEAM = 'away_team'
    REFEREES = 'referees'
    FILTERS = 'filters'
    FLS_MATCH_ID = 'fls_match_id'
    FLS_API_COMPETITION_ID = 'fls_competition_id'
    COMPETITION = 'competition'
    EVENTS = 'events'
    HOME_SCORE_PROBABILITY = 'home_score_probability'
    HOME_CONCEDE_PROBABILITY = 'home_concede_probability'
    AWAY_SCORE_PROBABILITY = 'away_score_probability'
    AWAY_CONCEDE_PROBABILITY = 'away_concede_probability'
    HOME_SCORE_PROBABILITY_OVER_1_5 = 'home_o15_prob'  # THESE STATS ARE BASED ON THE LAST 5 GAMES
    HOME_SCORE_PROBABILITY_OVER_2_5 = 'home_o25_prob'
    HOME_SCORE_PROBABILITY_OVER_3_5 = 'home_o35_prob'
    HOME_SCORE_PROBABILITY_UNDER_1_5 = 'home_u15_prob'
    HOME_SCORE_PROBABILITY_UNDER_2_5 = 'home_u25_prob'
    HOME_SCORE_PROBABILITY_UNDER_3_5 = 'home_u35_prob'
    AWAY_SCORE_PROBABILITY_OVER_1_5 = 'away_o15_prob'
    AWAY_SCORE_PROBABILITY_OVER_2_5 = 'away_o25_prob'
    AWAY_SCORE_PROBABILITY_OVER_3_5 = 'away_o35_prob'
    AWAY_SCORE_PROBABILITY_UNDER_1_5 = 'away_u15_prob'
    AWAY_SCORE_PROBABILITY_UNDER_2_5 = 'away_u25_prob'
    AWAY_SCORE_PROBABILITY_UNDER_3_5 = 'away_u35_prob'
    HOME_FORM = 'home_form'
    AWAY_FORM = 'away_form'
    HOME_TEAM_FLS_ID = 'home_team_fls_id'
    AWAY_TEAM_FLS_ID = 'away_team_fls_id'
    PREVIOUS_ENCOUNTERS = 'previous_encounters'
    PENALTY_SHOOTOUT_SCORE = 'penalty_shootout_score'
    FINISHED = 'finished'
    FANTASY_GAME_WEEK = 'fantasy_game_week'
    FANTASY_GAME_WEEK_ID = 'fantasy_game_week_id'
    GOALS_SCORED = 'goals_scored'
    GOALS_CONCEDED = 'goals_concended'
    ASSISTS = 'assists'
    OWN_GOALS = 'own_goals'
    PENALTIES_SAVED = 'penalties_saved'
    PENALTIES_MISSED = 'penalties_missed'
    YELLOW_CARDS = 'yellow_cards'
    RED_CARDS = 'red_cards'
    SAVES = 'saves'
    BONUS = 'bonus'
    BPS = 'bps'
    HOME_TEAM_DIFFICULTY = 'home_team_difficulty'
    AWAY_TEAM_DIFFICULTY = 'away_team_difficulty'
    FANTASY_MATCH_CODE = 'fantasy_match_code'
    FANTASY_MATCH_ID = 'fantasy_match_id'
    MINUTES = 'minutes'
    FANTASY_HOME_TEAM_CODE = 'f_home_team_code'
    FANTASY_AWAY_TEAM_CODE = 'f_away_team_code'
    FANTASY_HOME_TEAM_ID = 'f_home_team_id'
    FANTASY_AWAY_TEAM_ID = 'f_away_team_id'
    SIDE = 'side'
    GOAL_AMOUNT = 'amount'


class MatchEvent:
    OCCURED_AT = 'occured_at'
    STATE = 'state'
    MINUTES_PASSED = 'minutes_passed'
    OWN_GOALS = 'own_goals'
    ADDED_TIME = 'added_time'

    HOME_GOALS = 'home_goals'
    AWAY_GOALS = 'away_goals'
    SCORER_FLS_ID = 'scorer_fls_id'
    ASSIST_FLS_ID = 'assist_fls_id'
    TYPE = 'type'
    SUBSTITUTION = 'substitution'
    CLEAN_SHEET = 'clean_sheet'


class Team:
    ID = 'id'
    FOOTBALL_DATA_ID = 'team_fd_id'
    COUNTRY = 'country'
    NAME = 'name'
    SHORT_NAME = 'short_name'
    ACRONYM = 'acronym'
    CREST_URL = 'crest_url'
    ADDRESS = 'address'
    PHONE = 'phone'
    WEBSITE = 'website'
    EMAIL = 'email'
    YEAR_FOUNDED = 'year_founded'
    CLUB_COLOURS = 'club_colours'
    STADIUM = 'stadium'
    STADIUM_LAT = 'stadium_lat'
    STADIUM_LONG = 'stadium_long'
    STADIUM_CAPACITY = 'stadium_capacity'
    ACTIVE_COMPETITIONS = 'active_competitions'
    SQUAD = 'squad'
    SQUAD_ROLE = 'squad_role'
    FASTEST_LIVE_SCORES_API_ID = 'team_fls_id'
    FANTASY_CODE = 'fantasy_code'
    FANTASY_WEEK_STRENGTH = 'fantasy_week_strength'
    FANTASY_OVERALL_HOME_STRENGTH = 'fantasy_overall_home_strength'
    FANTASY_OVERALL_AWAY_STRENGTH = 'fantasy_overall_away_strength'
    FANTASY_ATTACK_HOME_STRENGTH = 'fantasy_attack_home_strength'
    FANTASY_ATTACK_AWAY_STRENGTH = 'fantasy_attack_away_strength'
    FANTASY_DEFENCE_HOME_STRENGTH = 'fantasy_defence_home_strength'
    FANTASY_DEFENCE_AWAY_STRENGTH = 'fantasy_defence_away_strength'
    FANTASY_ID = 'fantasy_id'


class Standings:
    ID = 'id'
    COMPETITION_ID = 'competition_id'
    STANDINGS_ID = 'standings_id'
    COMPETITION_NAME = 'competition_name'
    STAGE = 'stage'
    TYPE = 'type'
    SEASON = 'season'
    MATCH_DAY = 'match_day'
    TABLE = 'table'
    GROUP = 'group'
    POSITION = 'position'
    TEAM_NAME = 'team_name'
    FOOTBALL_DATA_TEAM_ID = 'fd_team_id'
    GAMES_PLAYED = 'games_played'
    GAMES_WON = 'games_won'
    GAMES_DRAWN = 'games_drawn'
    GAMES_LOST = 'games_lost'
    POINTS = 'points'
    GOALS_FOR = 'goals_for'
    GOALS_AGAINST = 'goals_against'
    GOAL_DIFFERENCE = 'goals_difference'
    LIMIT = 'limit'


class Player:
    ID = 'id'
    NAME = 'name'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    DATE_OF_BIRTH = 'date_of_birth'
    DATE_OF_BIRTH_EPOCH = 'date_of_birth_epoch'
    COUNTRY_OF_BIRTH = 'country_of_birth'
    NATIONALITY = 'nationality'
    POSITION = 'position'
    SHIRT_NUMBER = 'shirt_number'
    TEAM = 'team'
    NUMBER_OF_GOALS = 'number_of_goals'
    WEIGHT = 'weight'
    GENDER = 'gender'
    HEIGHT = 'height'
    TEAM_FLS_ID = 'team_fls_id'
    TEAM_FD_ID = 'team_fd_id'
    ASSISTS = 'assists'
    RED_CARDS = 'red_cards'
    COMPETITION_FLS_ID = 'competition_fls_id'
    YELLOW_CARDS = 'yellow_cards'
    FOOTBALL_DATA_API_ID = 'fd_id'
    FASTEST_LIVE_SCORES_API_ID = 'fls_id'
    COMPETITION_STATS = 'competition_stats'
    PLAYED_AT_HOME = 'played_at_home'
    PLAYED = 'played'
    NOT_PLAYED = 'not_played'
    FUTURE_FIXTURES = 'future_fixtures'
    SEASON_MATCH_HISTORY = 'season_match_history'
    FANTASY_PHOTO_URL = 'photo_url'

    # Fantasy fields:
    FANTASY_WEB_NAME = 'web_name'
    FANTASY_TEAM_CODE = 'fantasy_team_code'
    FANTASY_ID = 'fantasy_id'
    FANTASY_STATUS = 'fantasy_status'
    FANTASY_CODE = 'fantasy_code'
    FANTASY_PRICE = 'fantasy_price'
    FANTASY_NEWS = 'fantasy_news'
    FANTASY_NEWS_TIMESTAMP = 'fantasy_news_timestamp'
    FANTASY_CHANCE_OF_PLAYING_THIS_WEEK = 'chance_of_playing_this_week'
    FANTASY_CHANCE_OF_PLAYING_NEXT_WEEK = 'chance_of_playing_next_week'
    FANTASY_DREAM_TEAM_MEMBER = 'fantasy_dream_team_member'
    FANTASY_SEASON_VALUE = 'season_value'
    FANTASY_WEEK_VALUE = 'week_value'
    FANTASY_WEEK_PRICE_RISE = 'fantasy_week_price_rise'
    FANTASY_OVERALL_PRICE_RISE = 'fantasy_overall_price_rise'
    FANTASY_WEEK_PRICE_FALL = 'fantasy_week_price_fall'
    FANTASY_OVERALL_PRICE_FALL = 'fantasy_overall_price_fall'
    FANTASY_WEEK = 'fantasy_week'
    FANTASY_WEEK_ID = 'fantasy_week_id'  # ID made up of season year and game week e.g. 20171801 for 2017/2018 week 1
    FANTASY_DREAM_TEAM_COUNT = 'fantasy_dream_team_count'  # No. of times in dream team
    FANTASY_SELECTION_PERCENTAGE = 'fantasy_selection_percentage'  # % of fantasy users selecting player
    FANTASY_FORM = 'fantasy_form'
    FANTASY_OVERALL_TRANSFERS_IN = 'fantasy_overall_transfers_in'
    FANTASY_WEEK_TRANSFERS_IN = 'fantasy_week_transfers_in'
    FANTASY_OVERALL_TRANSFERS_OUT = 'fantasy_overall_transfers_out'
    FANTASY_WEEK_TRANSFERS_OUT = 'fantasy_week_transfers_out'
    FANTASY_OVERALL_POINTS = 'fantasy_overall_points'
    FANTASY_WEEK_POINTS = 'fantasy_week_points'
    FANTASY_POINT_AVERAGE = 'fantasy_point_average'
    FANTASY_ESTIMATED_WEEK_POINTS = 'fantasy_estimated_week_points'
    FANTASY_ESTIMATED_NEXT_WEEK_POINTS = 'fantasy_estimated_next_week_points'
    FANTASY_SPECIAL = 'fantasy_special'
    MINUTES_PLAYED = 'minutes_played'
    CLEAN_SHEETS = 'clean_sheets'
    GOALS_CONCEDED = 'goals_conceded'
    OWN_GOALS = 'own_goals'
    PENALTIES_SAVED = 'penalties_saved'
    PENALTIES_MISSED = 'penalties_missed'
    SAVES = 'saves'
    FANTASY_WEEK_BONUS = 'fantasy_week_bonus'
    FANTASY_TOTAL_BONUS = 'fantasy_total_bonus'
    FANTASY_INFLUENCE = 'fantasy_influence'
    FANTASY_CREATIVITY = 'fantasy_creativity'
    FANTASY_THREAT = 'fantasy_threat'
    FANTASY_ICT_INDEX = 'fantasy_ict_index'  # Influence, creativity, threat index
    FANTASY_TEAM_ID = 'fantasy_team_id'
    FANTASY_SELECTED = 'fantasy_selected'

    FANTASY_SEASON_START_PRICE = 'fantasy_season_start_price'
    FANTASY_SEASON_END_PRICE = 'fantasy_season_start_price'
    FANTASY_TRANSFERS_BALANCE = 'fantasy_transfers_balance'
    FANTASY_SELECTION_COUNT = 'fantasy_selection_count'

    # match
    OPEN_PLAY_CROSSES = 'open_play_crosses'
    BIG_CHANCES_CREATED = 'big_chances_created'
    CLEARANCES_BLOCKS_INTERCEPTIONS = 'clearances_blocks_interceptions'
    RECOVERIES = 'recoveries'
    KEY_PASSES = 'key_passes'
    TACKLES = 'tackles'
    WINNING_GOALS = 'winning_goals'
    ATTEMPTED_PASSES = 'attempted_passes'
    COMPLETED_PASSES = 'completed_passes'
    PENALTIES_CONCEDED = 'penalties_conceded'
    BIG_CHANCES_MISSED = 'big_chances_missed'
    ERRORS_LEADING_TO_GOAL = 'errors_leading_to_goal'
    ERRORS_LEADING_TO_GOAL_ATTEMPT = 'errors_leading_to_goal_attempt'
    TACKLED = 'tackled'
    OFFSIDE = 'offside'
    TARGET_MISSED = 'target_missed'
    FOULS = 'fouls'
    DRIBBLES = 'dribbles'
    FANTASY_OPPONENT_TEAM_ID = 'fantasy_opponent_team_id'
    SEASON_SUMMARIES = 'season_summaries'
    WEEK_STATS = 'week_stats'


class Competition:
    ID = 'id'
    NAME = 'name'
    CODE = 'code'
    LOCATION = 'location'
    FOOTBALL_DATA_API_ID = 'fd_api_id'
    FASTEST_LIVE_SCORES_API_ID = 'fls_api_id'



class Season:
    CURRENT_MATCH_DAY = 'current_match_day'
    START_DATE = 'start_date'
    END_DATE = 'end_date'
    WINNER = 'winner'
    FOOTBALL_DATA_API_ID = 'football_data_api_id'
    NAME = 'season_name'
    FANTASY_CODE = 'season_fantasy_code'


class FLS_STATES:
    FIXTURE = 0
    FIRST_HALF = 1
    HALF_TIME = 2
    SECOND_HALF = 3
    EXTRA_TIME = 4
    EXTRA_TIME_FIRST_HALF = 5
    EXTRA_TIME_INTERVAL = 6
    EXTRA_TIME_SECOND_HALF = 7
    PENALTIES = 8
    FULL_TIME = 9
    ABANDONED = 101
    POSTPONED = 102


class FantasyGameWeek:
    ID = 'id'
    WEEK = 'game_week'
    NAME = 'name'
    FANTASY_ID = 'fantasy_id'
    DEADLINE_TIME = 'deadline_time'
    DEADLINE_TIME_EPOCH = 'deadline_time_epoch'
    AVERAGE_SCORE = 'average_score'
    FINISHED = 'finished'
    HIGHEST_SCORE = 'highest_score'


# ----- API fields ---------


class API_FANTASY_PLAYER:
    ID = 'id'
    PHOTO_URL = 'photo'
    TEAM_CODE = 'team_code'
    TEAM_ID = 'team'
    CODE = 'code'
    FIRST_NAME = 'first_name'
    LASt_NAME = 'second_name'
    SHIRT_NUMBER = 'squad_number'
    STATUS = 'status'
    NEWS = 'news'
    CHANCE_OF_PLAYING_THIS_WEEK = 'chance_of_playing_this_round'
    CHANCE_OF_PLAYING_NEXT_WEEK = 'chance_of_playing_next_round'
    SEASON_VALUE = 'value_season'
    OVERALL_PRICE_RISE = 'cost_change_start'
    WEEK_PRICE_RISE = 'cost_change_event'
    OVERALL_PRICE_FALL = 'cost_change_start_fall'
    WEEK_PRICE_FALL = 'cost_change_event_fall'
    DREAM_TEAM_MEMBER = 'in_dreamteam'
    DREAM_TEAM_COUNT = 'dreamteam_count'
    SELECTION_PERCENTAGE = 'selected_by_percent'
    FORM = 'form'
    OVERALL_TRANSFERS_IN = 'transfers_in'
    OVERALL_TRANSFERS_OUT = 'transfers_out'
    WEEK_TRANSFERS_IN = 'transfers_in_event'
    WEEK_TRANSFERS_OUT = 'transfers_out_event'
    OVERALL_POINTS = 'total_point'
    WEEK_POINTS = 'event_points'
    POINT_AVERAGE = 'points_per_game'
    ESTIMATED_WEEK_POINTS = 'ep_this'
    ESTIMATED_NEXT_WEEK_POINTS = 'ep_next'
    SPECIAL = 'special'
    MINUTES_PLAYED = 'minutes'
    NUMBER_OF_GOALS = 'goals_scored'
    ASSISTS = 'assists'
    CLEAN_SHEETS = 'clean_sheets'
    GOALS_CONCEDED = 'goals_conceded'
    OWN_GOALS = 'own_goals'
    PENALTIES_SAVED = 'penalties_saved'
    PENALTIES_MISSED = 'penalties_missed'
    YELLOW_CARDS = 'yellow_cards'
    RED_CARDS = 'red_cards'
    SAVES = 'saves'
    WEEK_BONUS = 'bonus'
    TOTAL_BONUS = 'bps'
    INFLUENCE = 'influence'
    CREATIVITY = 'creativity'
    THREAT = 'threat'
    ICT_INDEX = 'ict_index'
    CURRENT_WEEK = 'current-event'


# ----- Mappers ------
FLS_STATES_MAPPER = {
    0: "fixture",
    1: "first_half",
    2: "half_time",
    3: "second_half",
    4: "extra_time",
    5: "extra_time_first_half",
    6: "extra_time_interval",
    7: "extra_time_second_half",
    8: "penalties",
    9: "full_time",
    101: "abandoned",
    102: "postponed"
}

FANTASY_STATUS_MAPPER = {
    "a": "available",
    "d": "illness",
    "i": "injury",
    "n": "ineligible",
    "u": "unavailable",
    "s": "suspended"
}

class IGNORE:
    INSTANCE_STATE = '_sa_instance_state'