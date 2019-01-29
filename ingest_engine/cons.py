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
    MATCH_UTC_DATE = 'utc_date'
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
    COUNTRY_OF_BIRTH = 'country_of_birth'
    NATIONALITY = 'nationality'
    POSITION = 'position'
    SHIRT_NUMBER = 'shirt_number'
    TEAM = 'team'
    NUMBER_OF_GOALS = 'number_of_goals'


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


