from collections import namedtuple
from ingest_engine.cons import Team as TEAM


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
