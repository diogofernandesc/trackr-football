class API:
    ENDPOINTS = 'endpoints'
    ENDPOINT_URL = 'url'
    ENDPOINT_FILTERS = 'filters'
    URL_DESCRIPTION = 'description'


class API_ERROR:
    COMPETITION_404 = 'There is no competition with those filters'

class API_ENDPOINTS:
    TEAMS = 'teams'
    COMPETITIONS = 'competitions'
    MATCH = 'match'
    PLAYER = 'player'
    STANDINGS = 'standings'
    STATS = 'stats'


ENDPOINT_DESCRIPTION = {
    API_ENDPOINTS.TEAMS: "Details about each team",
    API_ENDPOINTS.COMPETITIONS: "Base information about competitions",
    API_ENDPOINTS.MATCH: "Details of a specific match",
    API_ENDPOINTS.PLAYER: "Retrieve specific player details",
    API_ENDPOINTS.STANDINGS: "Get standings for a specific competition",
    API_ENDPOINTS.STATS: "Get different stats based on different things"
}
