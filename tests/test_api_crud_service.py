import unittest
from flask_run import application
from ingest_engine.cons import Match as MATCH, Team as TEAM, Player as PLAYER
from api_engine.api_cons import API, API_ERROR


class ApiInterfaceTest(unittest.TestCase):
    def setUp(self):
        application.config["SERVER_NAME"] = "localhost:5000"
        self.api = application.test_client()
        self.api.allow_subdomain_redirects = True
        self.api.testing = True

    def tearDown(self):
        pass

    def testCrudDBMatchUrl(self):
        # Whilst API is PL only
        # comp_fd_id = 2021
        # comp_fls_id = 2

        single_result = self.api.get('http://api.localhost:5000/v1/db/match?match_day=1').get_json()
        for match in single_result:
            self.assertTrue(all(k in match for k in (MATCH.FOOTBALL_DATA_ID,
                                                     MATCH.FLS_MATCH_ID,
                                                     MATCH.FLS_API_COMPETITION_ID,
                                                     MATCH.HOME_TEAM_FLS_ID,
                                                     MATCH.AWAY_TEAM_FLS_ID
                                                     )))
            self.assertEqual(match[MATCH.MATCHDAY], 1)
            self.assertIsInstance(match, dict)

        filter_result = self.api.get('http://api.localhost:5000/v1/db/match?id=-1').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.MATCH_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

    def testCrudDBTeamUrl(self):
        all_result = self.api.get('http://api.localhost:5000/v1/db/teams?limit=4', follow_redirects=True).get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (TEAM.NAME,
                                                      TEAM.FANTASY_CODE,
                                                      TEAM.FANTASY_ID,
                                                      TEAM.FANTASY_WEEK_STRENGTH,
                                                      TEAM.FANTASY_OVERALL_HOME_STRENGTH,
                                                      TEAM.FANTASY_OVERALL_AWAY_STRENGTH,
                                                      TEAM.FANTASY_ATTACK_HOME_STRENGTH,
                                                      TEAM.FANTASY_ATTACK_AWAY_STRENGTH,
                                                      TEAM.FANTASY_DEFENCE_HOME_STRENGTH,
                                                      TEAM.FANTASY_DEFENCE_AWAY_STRENGTH,
                                                      TEAM.SHORT_NAME,
                                                      TEAM.FASTEST_LIVE_SCORES_API_ID,
                                                      TEAM.FOOTBALL_DATA_ID)))

        self.assertIsInstance(all_result, list)
        self.assertEqual(len(all_result), 4)

    def testCrudDBPlayerUrl(self):
        fantasy_team_id = 20
        all_result = self.api.get(f'http://api.localhost:5000/v1/db/player?fantasy_team_id={fantasy_team_id}'
                                  ,follow_redirects=True).get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (PLAYER.ASSISTS,
                                                      PLAYER.FANTASY_CHANCE_OF_PLAYING_NEXT_WEEK,
                                                      PLAYER.FANTASY_CHANCE_OF_PLAYING_THIS_WEEK,
                                                      PLAYER.CLEAN_SHEETS,
                                                      PLAYER.FANTASY_CODE,
                                                      PLAYER.FANTASY_CREATIVITY,
                                                      PLAYER.FANTASY_DREAM_TEAM_COUNT,
                                                      PLAYER.FANTASY_DREAM_TEAM_MEMBER,
                                                      PLAYER.FANTASY_ESTIMATED_WEEK_POINTS,
                                                      PLAYER.FANTASY_FORM,
                                                      PLAYER.FANTASY_ID,
                                                      PLAYER.FANTASY_ICT_INDEX,
                                                      PLAYER.FANTASY_INFLUENCE,
                                                      PLAYER.FANTASY_NEWS,
                                                      PLAYER.FANTASY_NEWS_TIMESTAMP,
                                                      PLAYER.FANTASY_OVERALL_POINTS,
                                                      PLAYER.FANTASY_OVERALL_PRICE_FALL,
                                                      PLAYER.FANTASY_OVERALL_PRICE_RISE,
                                                      PLAYER.FANTASY_OVERALL_TRANSFERS_IN,
                                                      PLAYER.FANTASY_OVERALL_TRANSFERS_OUT,
                                                      PLAYER.FANTASY_POINT_AVERAGE,
                                                      PLAYER.FANTASY_PRICE,
                                                      PLAYER.FANTASY_SELECTION_PERCENTAGE,
                                                      PLAYER.FANTASY_SPECIAL,
                                                      PLAYER.FANTASY_STATUS,
                                                      PLAYER.FANTASY_TEAM_CODE,
                                                      PLAYER.FANTASY_TEAM_ID,
                                                      PLAYER.FANTASY_THREAT,
                                                      PLAYER.FANTASY_TOTAL_BONUS,
                                                      PLAYER.FANTASY_WEEK_TRANSFERS_OUT,
                                                      PLAYER.FANTASY_WEEK,
                                                      PLAYER.FANTASY_WEEK_BONUS,
                                                      PLAYER.FANTASY_WEEK_POINTS,
                                                      PLAYER.FANTASY_WEEK_PRICE_FALL,
                                                      PLAYER.FANTASY_WEEK_PRICE_RISE,
                                                      PLAYER.FANTASY_WEEK_TRANSFERS_IN,
                                                      PLAYER.FIRST_NAME,
                                                      PLAYER.GOALS_CONCEDED,
                                                      PLAYER.LAST_NAME,
                                                      PLAYER.MINUTES_PLAYED,
                                                      PLAYER.NAME,
                                                      PLAYER.NUMBER_OF_GOALS,
                                                      PLAYER.OWN_GOALS,
                                                      PLAYER.PENALTIES_SAVED,
                                                      PLAYER.PENALTIES_MISSED,
                                                      PLAYER.FANTASY_PHOTO_URL,
                                                      PLAYER.RED_CARDS,
                                                      PLAYER.SAVES,
                                                      PLAYER.FANTASY_SEASON_VALUE,
                                                      PLAYER.SHIRT_NUMBER,
                                                      PLAYER.FANTASY_WEB_NAME,
                                                      PLAYER.YELLOW_CARDS)))

            self.assertTrue(result[PLAYER.FANTASY_TEAM_ID] == fantasy_team_id)













