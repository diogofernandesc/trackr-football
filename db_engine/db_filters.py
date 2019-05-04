from collections import namedtuple
from ingest_engine.cons import Team as TEAM, Standings as STANDINGS


"""
To add a new table filter:
 - Add a list of filters, preferably a list of string constants representing the column names that can be filtered on
 - Create a named tuple with default none fields, passing your newly defined list of filterable columns
 """

team_filter_fields = [TEAM.ID,
                      TEAM.FANTASY_ID,
                      TEAM.FOOTBALL_DATA_ID,
                      TEAM.NAME,
                      TEAM.YEAR_FOUNDED,
                      TEAM.STADIUM_CAPACITY,
                      TEAM.FASTEST_LIVE_SCORES_API_ID,
                      TEAM.FANTASY_CODE,
                      TEAM.FANTASY_OVERALL_HOME_STRENGTH,
                      TEAM.FANTASY_OVERALL_AWAY_STRENGTH,
                      TEAM.FANTASY_ATTACK_HOME_STRENGTH,
                      TEAM.FANTASY_ATTACK_AWAY_STRENGTH,
                      TEAM.FANTASY_DEFENCE_HOME_STRENGTH,
                      TEAM.FANTASY_DEFENCE_AWAY_STRENGTH,
                      ]
TeamFilters = namedtuple('team_filters', team_filter_fields, defaults=(None,) * len(team_filter_fields))


standings_filter_field = [STANDINGS.ID,
                          STANDINGS.STANDINGS_ID,
                          STANDINGS.POSITION,
                          STANDINGS.TEAM_NAME,
                          STANDINGS.TYPE,
                          STANDINGS.SEASON,
                          STANDINGS.MATCH_DAY,
                          STANDINGS.GAMES_PLAYED,
                          STANDINGS.GAMES_WON,
                          STANDINGS.GAMES_DRAWN,
                          STANDINGS.GAMES_LOST,
                          STANDINGS.POINTS,
                          STANDINGS.GOALS_FOR,
                          STANDINGS.GOALS_AGAINST,
                          STANDINGS.GOAL_DIFFERENCE]

StandingsFilters = namedtuple('standings_filters',
                              standings_filter_field, defaults=(None,) * len(standings_filter_field))


