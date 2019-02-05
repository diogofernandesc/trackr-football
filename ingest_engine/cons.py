class FootballDataApiFilters:
    '''
    https://www.football-data.org/documentation/quickstart
    '''
    ID = 'id'
    MATCHDAY = 'matchday'  # Integer 0-49
    SEASON = 'season'  # Integer for year e.g. 2018

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


class Match:
    ID = 'id'
    SEASON_FOOTBALL_DATA_ID = 'season_football_data_id'
    SEASON_START_DATE = 'season_start_date'
    SEASON_END_DATE = 'season_end_date'
    SEASON_YEAR = 'season_year'
    MATCH_UTC_DATE = 'utc_date'
    START_TIME_EPOCH = 'start_time_epoch'
    STATUS = 'status'
    MATCHDAY = 'matchday'
    FULL_TIME_HOME_SCORE = 'full_time_home_score'
    FULL_TIME_AWAY_SCORE = 'full_time_away_score'
    HALF_TIME_HOME_SCORE = 'half_time_home_score'
    HALF_TIME_AWAY_SCORE = 'half_time_away_score'
    EXTRA_TIME_HOME_SCORE = 'extra_time_home_score'
    EXTRA_TIME_AWAY_SCORE = 'extra_time_away_score'
    PENALTY_HOME_SCORE = 'penalty_home_score'
    PENALTY_AWAY_SCORE = 'penalty_away_score'
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
    HOME_SCORE_PROBABILITY_OVER_1_5 = 'home_score_probability_over_1_5'  # THESE STATS ARE BASED ON THE LAST 5 GAMES
    HOME_SCORE_PROBABILITY_OVER_2_5 = 'home_score_probability_over_2_5'
    HOME_SCORE_PROBABILITY_OVER_3_5 = 'home_score_probability_over_3_5'
    HOME_SCORE_PROBABILITY_UNDER_1_5 = 'home_score_probability_under_1_5'
    HOME_SCORE_PROBABILITY_UNDER_2_5 = 'home_score_probability_under_2_5'
    HOME_SCORE_PROBABILITY_UNDER_3_5 = 'home_score_probability_under_3_5'
    AWAY_SCORE_PROBABILITY_OVER_1_5 = 'away_score_probability_over_1_5'
    AWAY_SCORE_PROBABILITY_OVER_2_5 = 'away_score_probability_over_2_5'
    AWAY_SCORE_PROBABILITY_OVER_3_5 = 'away_score_probability_over_3_5'
    AWAY_SCORE_PROBABILITY_UNDER_1_5 = 'away_score_probability_under_1_5'
    AWAY_SCORE_PROBABILITY_UNDER_2_5 = 'away_score_probability_under_2_5'
    AWAY_SCORE_PROBABILITY_UNDER_3_5 = 'away_score_probability_under_3_5'
    HOME_FORM = 'home_form'
    AWAY_FORM = 'away_form'
    HOME_TEAM_FLS_ID = 'home_team_fls_id'
    AWAY_TEAM_FLS_ID = 'away_team_fls_id'
    PREVIOUS_ENCOUNTERS = 'previous_encounters'
    PENALTY_SHOOTOUT_SCORE = 'penalty_shootout_score'

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


class Team:
    FOOTBALL_DATA_ID = 'football_data_id'
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
    FASTEST_LIVE_SCORES_API_ID = 'fls_api_id'


class Standings:
    COMPETITION_NAME = 'competition_name'
    STAGE = 'stage'
    TYPE = 'type'
    SEASON = 'season'
    MATCH_DAY = 'match_day'
    TABLE = 'table'
    GROUP = 'group'
    POSITION = 'position'
    TEAM_NAME = 'team_name'
    GAMES_PLAYED = 'games_played'
    GAMES_WON = 'games_won'
    GAMES_DRAWN = 'games_drawn'
    GAMES_LOST = 'games_lost'
    POINTS = 'points'
    GOALS_FOR = 'goals_for'
    GOALS_AGAINST = 'goals_against'
    GOAL_DIFFERENCE = 'goal_difference'



class Player:
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




class Competition:
    NAME = 'name'
    CODE = 'code'
    LOCATION = 'location'
    FOOTBALL_DATA_API_ID = 'football_data_api_id'
    FASTEST_LIVE_SCORES_API_ID = 'fls_api_id'



class Season:
    CURRENT_MATCH_DAY = 'current_match_day'
    START_DATE = 'start_date'
    END_DATE = 'end_date'
    WINNER = 'winner'
    FOOTBALL_DATA_API_ID = 'football_data_api_id'


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

