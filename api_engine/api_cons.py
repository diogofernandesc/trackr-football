class API:
    ENDPOINTS = 'endpoints'
    ENDPOINT_URL = 'url'
    ENDPOINT_FILTERS = 'filters'
    URL_DESCRIPTION = 'description'
    MESSAGE = 'message'
    STATUS_CODE = 'status_code'


class API_ERROR:
    COMPETITION_404 = 'There is no competition with those filters'
    TEAM_404 = 'There is no team with those filters'
    MATCH_404 = 'There is no matches with those filters'
    STANDINGS_404 = 'There is no standings with those filters'
    PLAYER_404 = 'There is no players with those filters'
    STATS_404 = 'There is no stats with those filters'
    INTEGER_LIMIT_400 = 'Limit must be an integer'
    NO_COMPETITION_400 = 'You need to provide a competition id to query this endpoint'
    MISSING_COMPETITION_404 = 'No competition could be found'
    FILTER_PROBLEM_400 = 'Invalid filter applied'
    MISSING_FILTER_400 = 'You have not specified a filter to this endpoint'
    RESOURCE_NOT_FOUND_404 = "The resource you're looking for could not be found"
    STANDINGS_MAX_LIMIT_400 = 'Invalid limit, the limit per table is 20'


class API_ENDPOINTS:
    TEAMS = 'teams'
    COMPETITIONS = 'competitions'
    MATCH = 'match'
    PLAYER = 'player'
    STANDINGS = 'standings'
    STATS = 'stats'

class DB_QUERY_FIELD:
    PLAYER_ID = 'player_id'
    MATCH_ID = 'match_id'

ENDPOINT_DESCRIPTION = {
    API_ENDPOINTS.TEAMS: "Details about each team",
    API_ENDPOINTS.COMPETITIONS: "Base information about competitions",
    API_ENDPOINTS.MATCH: "Details of a specific match",
    API_ENDPOINTS.PLAYER: "Retrieve specific player details",
    API_ENDPOINTS.STANDINGS: "Get standings for a specific competition",
    API_ENDPOINTS.STATS: "Get different match stats for different players"
}
