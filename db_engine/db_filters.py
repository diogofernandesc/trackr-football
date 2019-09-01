from collections import namedtuple
from ingest_engine.cons import Team as TEAM, Standings as STANDINGS, Competition as COMPETITION, Match as MATCH

"""
To add a new table filter:
 - Add a list of filters, preferably a list of string constants representing the column names that can be filtered on
 - Create a named tuple with default none fields, passing your newly defined list of filterable columns
"""

comp_filter_fields = [COMPETITION.ID,
                      COMPETITION.NAME,
                      COMPETITION.CODE,
                      COMPETITION.LOCATION,
                      COMPETITION.FASTEST_LIVE_SCORES_API_ID,
                      COMPETITION.FOOTBALL_DATA_API_ID]
CompFilters = namedtuple('comp_filters', comp_filter_fields, defaults=(None,) * len(comp_filter_fields))

team_filter_fields = [TEAM.ID,
                      TEAM.FANTASY_ID,
                      TEAM.FOOTBALL_DATA_ID,
                      TEAM.NAME,
                      TEAM.YEAR_FOUNDED,
                      TEAM.STADIUM_CAPACITY,
                      TEAM.FASTEST_LIVE_SCORES_API_ID,
                      TEAM.FANTASY_OVERALL_HOME_STRENGTH,
                      TEAM.FANTASY_OVERALL_AWAY_STRENGTH,
                      TEAM.FANTASY_ATTACK_HOME_STRENGTH,
                      TEAM.FANTASY_ATTACK_AWAY_STRENGTH,
                      TEAM.FANTASY_DEFENCE_HOME_STRENGTH,
                      TEAM.FANTASY_DEFENCE_AWAY_STRENGTH,
                      ]
TeamFilters = namedtuple('team_filters', team_filter_fields, defaults=(None,) * len(team_filter_fields))


standings_base_filter_field = [STANDINGS.ID,
                               STANDINGS.COMPETITION_ID,
                               STANDINGS.TYPE,
                               STANDINGS.SEASON,
                               STANDINGS.MATCH_DAY]

StandingsBaseFilters = namedtuple('standings_base_filters',
                                  standings_base_filter_field, defaults=(None,) * len(standings_base_filter_field))

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
                          STANDINGS.GOAL_DIFFERENCE,
                          STANDINGS.LIMIT]

StandingsFilters = namedtuple('standings_filters',
                              standings_filter_field, defaults=(None,) * len(standings_filter_field))


match_filter_field = [MATCH.ID,
                      MATCH.FOOTBALL_DATA_ID,
                      MATCH.SEASON_START_DATE,
                      MATCH.SEASON_END_DATE,
                      MATCH.SEASON_YEAR,
                      MATCH.MATCH_UTC_DATE,
                      MATCH.START_TIME_EPOCH,
                      MATCH.START_TIME,
                      MATCH.STATUS,
                      MATCH.MATCHDAY,
                      MATCH.FULL_TIME_HOME_SCORE,
                      MATCH.FULL_TIME_AWAY_SCORE,
                      MATCH.HALF_TIME_HOME_SCORE,
                      MATCH.HALF_TIME_AWAY_SCORE,
                      MATCH.EXTRA_TIME_HOME_SCORE,
                      MATCH.EXTRA_TIME_AWAY_SCORE,
                      MATCH.PENALTY_HOME_SCORE,
                      MATCH.PENALTY_AWAY_SCORE,
                      MATCH.WINNER,
                      MATCH.HOME_TEAM,
                      MATCH.AWAY_TEAM,
                      MATCH.FLS_MATCH_ID,
                      MATCH.FLS_API_COMPETITION_ID,
                      MATCH.HOME_SCORE_PROBABILITY,
                      MATCH.AWAY_SCORE_PROBABILITY,
                      MATCH.HOME_CONCEDE_PROBABILITY,
                      MATCH.AWAY_CONCEDE_PROBABILITY,
                      MATCH.HOME_SCORE_PROBABILITY_OVER_1_5,
                      MATCH.HOME_SCORE_PROBABILITY_OVER_2_5,
                      MATCH.HOME_SCORE_PROBABILITY_OVER_3_5,
                      MATCH.HOME_SCORE_PROBABILITY_UNDER_1_5,
                      MATCH.HOME_SCORE_PROBABILITY_UNDER_2_5,
                      MATCH.HOME_SCORE_PROBABILITY_UNDER_3_5,
                      MATCH.AWAY_SCORE_PROBABILITY_OVER_1_5,
                      MATCH.AWAY_SCORE_PROBABILITY_OVER_2_5,
                      MATCH.AWAY_SCORE_PROBABILITY_OVER_3_5,
                      MATCH.AWAY_SCORE_PROBABILITY_UNDER_1_5,
                      MATCH.AWAY_SCORE_PROBABILITY_UNDER_2_5,
                      MATCH.AWAY_SCORE_PROBABILITY_UNDER_3_5,
                      MATCH.HOME_FORM,
                      MATCH.AWAY_FORM,
                      MATCH.HOME_TEAM_FLS_ID,
                      MATCH.AWAY_TEAM_FLS_ID,
                      MATCH.PENALTY_SHOOTOUT_SCORE,
                      MATCH.FINISHED,
                      MATCH.FANTASY_GAME_WEEK,
                      MATCH.HOME_TEAM_DIFFICULTY,
                      MATCH.AWAY_TEAM_DIFFICULTY,
                      MATCH.FANTASY_MATCH_CODE,
                      MATCH.FANTASY_HOME_TEAM_CODE,
                      MATCH.FANTASY_AWAY_TEAM_CODE,
                      MATCH.MINUTES,
                      MATCH.FANTASY_HOME_TEAM_ID,
                      MATCH.FANTASY_AWAY_TEAM_ID]

MatchFilters = namedtuple('match_filters', match_filter_field, defaults=(None,) * len(match_filter_field))

