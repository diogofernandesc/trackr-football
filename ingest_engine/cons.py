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





class Competition:
    NAME = 'name'
    CODE = 'code'
    LOCATION = 'location'
    FOOTBALL_DATA_API_ID = 'football_data_api_id'


class Season:
    CURRENT_MATCH_DAY = 'current_match_day'
    START_DATE = 'start_date'
    END_DATE = 'end_date'
    WINNER = 'winner'
    FOOTBALL_DATA_API_ID = 'football_data_api_id'


