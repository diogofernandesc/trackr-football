import unittest
from flask_run import application
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ingest_engine.cons import Competition as COMPETITION, Standings as STANDINGS, Match as MATCH, Team as TEAM,\
    Player as PLAYER, FantasyGameWeek as FANTASY_GAME_WEEK, MatchEvent as MATCH_EVENT
from api_engine.api_cons import API_ENDPOINTS, API, API_ERROR, DB_QUERY_FIELD


class ApiInterfaceTest(unittest.TestCase):
    def setUp(self):
        application.config["SERVER_NAME"] = "localhost:5000"
        limiter = application.config["limiter"]
        limiter.enabled = False
        self.api = application.test_client()
        self.api.testing = True

    def tearDown(self):
        pass

    def testBaseUrl(self):
        true_endpoints = [e for c, e in vars(API_ENDPOINTS).items() if not c.startswith("__")]
        # result = self.api.get('/v1').get_json()
        result = self.api.get('http://api.localhost:5000/v1', follow_redirects=True).get_json()
        result_endpoints = result[API.ENDPOINTS]
        for endpoint in result_endpoints:
            self.assertTrue(endpoint[API.ENDPOINT_URL].split("v1/")[1] in true_endpoints)
            self.assertIsInstance(endpoint[API.URL_DESCRIPTION], str)

    def testCompetitionUrl(self):
        all_result = self.api.get('http://api.localhost:5000/v1/competitions').get_json()

        self.assertTrue(all(k in all_result for k in (COMPETITION.ID,
                                                      COMPETITION.NAME,
                                                      COMPETITION.LOCATION,
                                                      COMPETITION.CODE,
                                                      COMPETITION.FASTEST_LIVE_SCORES_API_ID,
                                                      COMPETITION.FOOTBALL_DATA_API_ID)))

        filter_result = self.api.get('http://api.localhost:5000/v1/competition?id=1').get_json()
        self.assertEqual(filter_result[COMPETITION.ID], 1)

        filter_result = self.api.get('http://api.localhost:5000/v1/competition?code=PL').get_json()
        self.assertEqual(filter_result[COMPETITION.CODE], 'PL')

    def testStandingsUrl(self):

        def filter_test(filter_str, filter_val):
            filter_result = self.api.\
                get(f'http://api.localhost:5000/v1/standings?{filter_str}={filter_val}').get_json()
            if not isinstance(filter_result, list):
                filter_result = [filter_result]

            for result in filter_result:
                for entry in result[STANDINGS.TABLE]:
                    self.assertTrue(entry[filter_str], filter_val)

        def filter_test_adv(filter_str, filter_val, op):
            filter_result = self.api.\
                get(f'http://api.localhost:5000/v1/standings/all?{filter_str}=${op}:{filter_val}').get_json()
            if not isinstance(filter_result, list):
                filter_result = [filter_result]  # Handle returns as dict or list

            for result in filter_result:
                for entry in result[STANDINGS.TABLE]:
                    if op == "lt":
                        self.assertLess(entry[filter_str], filter_val)

                    elif op == "lte":
                        self.assertLessEqual(entry[filter_str], filter_val)

                    elif op == "gt":
                        self.assertGreater(entry[filter_str], filter_val)

                    elif op == "gte":
                        self.assertGreaterEqual(entry[filter_str], filter_val)

        all_result = self.api.get('http://api.localhost:5000/v1/standings/all').get_json()
        self.assertEqual(len(all_result), 3)

        for result in all_result:
            self.assertTrue(all(k in result for k in (STANDINGS.ID,
                                                      STANDINGS.COMPETITION_ID,
                                                      STANDINGS.TYPE,
                                                      STANDINGS.SEASON,
                                                      STANDINGS.MATCH_DAY)))

            self.assertEqual(len(result[STANDINGS.TABLE]), 20)
            for entry in result[STANDINGS.TABLE]:
                self.assertTrue(STANDINGS.ID in entry)
                self.assertTrue(STANDINGS.STANDINGS_ID in entry)
                self.assertTrue(STANDINGS.POSITION in entry)
                self.assertTrue(STANDINGS.TEAM_NAME in entry)
                self.assertTrue(STANDINGS.FOOTBALL_DATA_TEAM_ID in entry)
                self.assertTrue(STANDINGS.GAMES_PLAYED in entry)
                self.assertTrue(STANDINGS.GAMES_WON in entry)
                self.assertTrue(STANDINGS.GAMES_DRAWN in entry)
                self.assertTrue(STANDINGS.GAMES_LOST in entry)
                self.assertTrue(STANDINGS.POINTS in entry)
                self.assertTrue(STANDINGS.GOALS_FOR in entry)
                self.assertTrue(STANDINGS.GOALS_AGAINST in entry)
                self.assertTrue(STANDINGS.GOAL_DIFFERENCE in entry)

        all_result = self.api.get('http://api.localhost:5000/v1/standings').get_json()
        self.assertTrue(len(all_result), 10)

        filter_test(filter_str=STANDINGS.POSITION, filter_val=5)

        filter_test_adv(filter_str=STANDINGS.POSITION, filter_val=10, op="lt")
        filter_test_adv(filter_str=STANDINGS.GAMES_PLAYED, filter_val=3, op="lte")
        filter_test_adv(filter_str=STANDINGS.GAMES_WON, filter_val=1, op="gte")
        filter_test_adv(filter_str=STANDINGS.GOAL_DIFFERENCE, filter_val=0, op="gt")

        filter_result = self.api.get('http://api.localhost:5000/v1/standings?points=$lt:0').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.STANDINGS_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

        filter_result = self.api.get('http://api.localhost:5000/v1/standings?id=1&limit=astring').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.INTEGER_LIMIT_400)
        self.assertEqual(filter_result[API.STATUS_CODE], 400)

        limit_result = self.api.get('http://api.localhost:5000/v1/standings?limit=33').get_json()
        self.assertEqual(limit_result[API.MESSAGE], API_ERROR.STANDINGS_MAX_LIMIT_400)
        self.assertEqual(limit_result[API.STATUS_CODE], 400)

    def testDBMatchUrl(self):
        # Whilst API is PL only
        # comp_fd_id = 2021
        # comp_fls_id = 2

        all_result = self.api.get('http://api.localhost:5000/v1/match/all?limit=5').get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (MATCH.ID,
                                                      MATCH.FOOTBALL_DATA_ID,
                                                      MATCH.FLS_MATCH_ID,
                                                      MATCH.FLS_API_COMPETITION_ID,
                                                      MATCH.HOME_TEAM_FLS_ID,
                                                      MATCH.AWAY_TEAM_FLS_ID,
                                                      )))
        self.assertIsInstance(all_result, list)
        self.assertEqual(len(all_result), 5)

        match_day_result = self.api.get('http://api.localhost:5000/v1/match?match_day=1').get_json()
        for match in match_day_result:
            self.assertTrue(all(k in match for k in (MATCH.ID,
                                                     MATCH.FOOTBALL_DATA_ID,
                                                     MATCH.FLS_MATCH_ID,
                                                     MATCH.FLS_API_COMPETITION_ID,
                                                     MATCH.HOME_TEAM_FLS_ID,
                                                     MATCH.AWAY_TEAM_FLS_ID
                                                     )))
            self.assertEqual(match[MATCH.MATCHDAY], 1)

        single_result = self.api.get('http://api.localhost:5000/v1/match?id=1').get_json()
        self.assertIsInstance(single_result, dict)
        self.filter_test_adv(filter_str=MATCH.HOME_SCORE_PROBABILITY, filter_val=100, op="lt", endpoint="match")
        self.filter_test_adv(filter_str=MATCH.AWAY_SCORE_PROBABILITY, filter_val=20, op="gt", endpoint="match")
        self.filter_test_adv(filter_str=MATCH.HOME_SCORE_PROBABILITY_OVER_1_5,
                             filter_val=10,
                             op="gte",
                             endpoint="match")

        self.filter_test_adv(filter_str=MATCH.AWAY_SCORE_PROBABILITY_UNDER_3_5,
                             filter_val=90,
                             op="lte",
                             endpoint="match")

        self.filter_test_adv(filter_str=MATCH.FULL_TIME_AWAY_SCORE,
                             filter_val=2,
                             op="gte",
                             endpoint="match")

        filter_result = self.api.get('http://api.localhost:5000/v1/match?id=-1').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.MATCH_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

        error_result = self.api.get('http://api.localhost:5000/v1/match?match_day=$ltr:3').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.FILTER_PROBLEM_400)
        self.assertEqual(error_result[API.STATUS_CODE], 400)

        error_result = self.api.get('http://api.localhost:5000/v1/match/all?hdas=1').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.RESOURCE_NOT_FOUND_404)
        self.assertEqual(error_result[API.STATUS_CODE], 404)

    def testDBTeamUrl(self):
        # Whilst API is PL only
        # comp_fd_id = 2021
        # comp_fls_id = 2

        all_result = self.api.get('http://api.localhost:5000/v1/team/all?limit=5').get_json()
        for result in all_result:
            self.assertTrue(all(k in result for k in (TEAM.NAME,
                                                      TEAM.ID,
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
        self.assertEqual(len(all_result), 5)

        fantasy_id_result = self.api.get('http://api.localhost:5000/v1/team?fantasy_id=1').get_json()
        self.assertTrue(all(k in fantasy_id_result for k in (TEAM.NAME,
                                                             TEAM.ID,
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
        self.assertEqual(fantasy_id_result[TEAM.FANTASY_ID], 1)

        single_result = self.api.get('http://api.localhost:5000//v1/team?id=1').get_json()
        self.assertIsInstance(single_result, dict)

        self.filter_test(TEAM.FOOTBALL_DATA_ID, 61, "team")
        self.filter_test(TEAM.FANTASY_ID, 2, "team")
        self.filter_test(TEAM.NAME, "Chelsea", "team")

        self.filter_test_adv(filter_str=TEAM.YEAR_FOUNDED, filter_val=1875, op="lt", endpoint="team")
        self.filter_test_adv(filter_str=TEAM.FANTASY_OVERALL_HOME_STRENGTH, filter_val=1330, op="gt", endpoint="team")
        self.filter_test_adv(filter_str=TEAM.FANTASY_OVERALL_AWAY_STRENGTH,
                             filter_val=1200,
                             op="gte",
                             endpoint="team")

        self.filter_test_adv(filter_str=TEAM.FANTASY_ATTACK_HOME_STRENGTH,
                             filter_val=1240,
                             op="lte",
                             endpoint="team")

        self.filter_test_adv(filter_str=TEAM.FANTASY_DEFENCE_AWAY_STRENGTH, filter_val=1100, op="gte", endpoint="team")

        filter_result = self.api.get('http://api.localhost:5000/v1/team?id=-1').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.TEAM_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

        error_result = self.api.get('http://api.localhost:5000/v1/team?fantasy_id=$ltr:3').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.FILTER_PROBLEM_400)
        self.assertEqual(error_result[API.STATUS_CODE], 400)

        error_result = self.api.get('http://api.localhost:5000/v1/team/all?hdas=1').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.RESOURCE_NOT_FOUND_404)
        self.assertEqual(error_result[API.STATUS_CODE], 404)

    def testDBPlayerUrl(self):
        # Whilst API is PL only
        # comp_fd_id = 2021
        # comp_fls_id = 2

        player_result = self.api.get('http://api.localhost:5000/v1/player?fantasy_id=141').get_json()

        self.assertTrue(all(k in player_result for k in (PLAYER.FANTASY_CHANCE_OF_PLAYING_NEXT_WEEK,
                                                         PLAYER.FANTASY_CHANCE_OF_PLAYING_THIS_WEEK,
                                                         PLAYER.FANTASY_CODE,
                                                         PLAYER.FANTASY_DREAM_TEAM_COUNT,
                                                         PLAYER.FANTASY_DREAM_TEAM_MEMBER,
                                                         PLAYER.FANTASY_FORM,
                                                         PLAYER.FANTASY_ID,
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
                                                         PLAYER.FANTASY_TOTAL_BONUS,
                                                         PLAYER.FANTASY_WEEK_PRICE_FALL,
                                                         PLAYER.FANTASY_WEEK_PRICE_RISE,
                                                         PLAYER.FIRST_NAME,
                                                         PLAYER.LAST_NAME,
                                                         PLAYER.NAME,
                                                         PLAYER.NUMBER_OF_GOALS,
                                                         PLAYER.FANTASY_PHOTO_URL,
                                                         PLAYER.SHIRT_NUMBER,
                                                         PLAYER.FANTASY_WEB_NAME,
                                                         PLAYER.WEEK_STATS)))

        for stat in player_result[PLAYER.WEEK_STATS]:
            self.assertTrue(all(k in stat for k in (PLAYER.FANTASY_SELECTION_COUNT,
                                                    PLAYER.FANTASY_TRANSFERS_BALANCE,
                                                    PLAYER.FANTASY_WEEK_TRANSFERS_IN,
                                                    PLAYER.FANTASY_WEEK_TRANSFERS_OUT,
                                                    PLAYER.FANTASY_WEEK_BONUS,
                                                    PLAYER.FANTASY_WEEK_POINTS,
                                                    FANTASY_GAME_WEEK.WEEK,
                                                    FANTASY_GAME_WEEK.ID,
                                                    PLAYER.FANTASY_SEASON_VALUE)))

        self.assertIsInstance(player_result, dict)
        self.assertTrue(player_result[PLAYER.FANTASY_ID] == 141)

        team_result = self.api.get('http://api.localhost:5000/v1/player?fantasy_team_id=1').get_json()
        for player_ in team_result:
            self.assertEqual(player_[PLAYER.FANTASY_TEAM_ID], 1)

        player_stat_result = self.api.get('http://api.localhost:5000/v1/player?name=kane&game_week=1').get_json()
        self.assertTrue(len(player_stat_result[PLAYER.WEEK_STATS]) == 1)
        self.assertTrue(player_stat_result[PLAYER.WEEK_STATS][0][FANTASY_GAME_WEEK.WEEK] == 1)

        self.filter_test(PLAYER.FANTASY_FORM, 4, "player")
        self.filter_test(PLAYER.POSITION, "Goalkeeper", "player")

        self.filter_test_adv(filter_str=PLAYER.FANTASY_PRICE, filter_val=50, op="lt", endpoint="player")
        self.filter_test_adv(filter_str=PLAYER.FANTASY_OVERALL_PRICE_RISE, filter_val=0, op="gt", endpoint="player")
        self.filter_test_adv(filter_str=PLAYER.NUMBER_OF_GOALS, filter_val=2, op="gte", endpoint="player")
        self.filter_test_adv(filter_str=PLAYER.FANTASY_POINT_AVERAGE, filter_val=3.5, op="lte", endpoint="player")

        filter_result = self.api.get('http://api.localhost:5000/v1/player?id=-1').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.PLAYER_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

        error_result = self.api.get('http://api.localhost:5000/v1/player?fantasy_id=$ltr:3').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.FILTER_PROBLEM_400)
        self.assertEqual(error_result[API.STATUS_CODE], 400)

        error_result = self.api.get('http://api.localhost:5000/v1/player/all?hdas=1').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.RESOURCE_NOT_FOUND_404)
        self.assertEqual(error_result[API.STATUS_CODE], 404)

        error_result = self.api.get('http://api.localhost:5000/v1/player').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.MISSING_FILTER_400)
        self.assertEqual(error_result[API.STATUS_CODE], 400)

    def testDBStatsUrl(self):
        # Whilst API is PL only
        # comp_fd_id = 2021
        # comp_fls_id = 2

        stat_result = self.api.get('http://api.localhost:5000/v1/stats?player_id=1152&limit=2').get_json()
        for stat in stat_result:
            self.assertTrue(all(k in stat for k in (PLAYER.ASSISTS,
                                                    MATCH.BONUS,
                                                    MATCH_EVENT.CLEAN_SHEET,
                                                    PLAYER.FANTASY_CREATIVITY,
                                                    PLAYER.FANTASY_ICT_INDEX,
                                                    PLAYER.FANTASY_INFLUENCE,
                                                    MATCH.FANTASY_MATCH_ID,
                                                    PLAYER.FANTASY_THREAT,
                                                    PLAYER.GOALS_CONCEDED,
                                                    MATCH.GOALS_SCORED,
                                                    MATCH.ID,
                                                    PLAYER.MINUTES_PLAYED,
                                                    PLAYER.OWN_GOALS,
                                                    PLAYER.PENALTIES_MISSED,
                                                    PLAYER.PENALTIES_SAVED,
                                                    PLAYER.PLAYED_AT_HOME,
                                                    PLAYER.RED_CARDS,
                                                    PLAYER.SAVES,
                                                    PLAYER.YELLOW_CARDS)))

            self.assertIsInstance(stat, dict)
            self.assertTrue(stat[DB_QUERY_FIELD.PLAYER_ID] == 1152)
            self.assertTrue(len(stat_result) == 2)

        self.filter_test_adv(filter_str=PLAYER.ASSISTS, filter_val=1, op="lte", endpoint="stats")
        self.filter_test_adv(filter_str=PLAYER.FANTASY_INFLUENCE, filter_val=10, op="gte", endpoint="stats")
        self.filter_test_adv(filter_str=PLAYER.MINUTES_PLAYED, filter_val=25, op="gt", endpoint="stats")
        self.filter_test_adv(filter_str=PLAYER.YELLOW_CARDS, filter_val=5, op="lt", endpoint="stats")

        filter_result = self.api.get('http://api.localhost:5000/v1/stats?player_id=-1').get_json()
        self.assertEqual(filter_result[API.MESSAGE], API_ERROR.STATS_404)
        self.assertEqual(filter_result[API.STATUS_CODE], 404)

        error_result = self.api.get('http://api.localhost:5000/v1/stats?player_id=$ltr:3').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.FILTER_PROBLEM_400)
        self.assertEqual(error_result[API.STATUS_CODE], 400)

        error_result = self.api.get('http://api.localhost:5000/v1/stats?player_id=1152&hdas=1').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.RESOURCE_NOT_FOUND_404)
        self.assertEqual(error_result[API.STATUS_CODE], 404)

        error_result = self.api.get('http://api.localhost:5000/v1/stats').get_json()
        self.assertEqual(error_result[API.MESSAGE], API_ERROR.MISSING_FILTER_400)
        self.assertEqual(error_result[API.STATUS_CODE], 400)

    def filter_test(self, filter_str, filter_val, endpoint):
        filter_result = self.api.get(f'http://api.localhost:5000/v1/{endpoint}?{filter_str}={filter_val}').get_json()
        if not isinstance(filter_result, list):
            filter_result = [filter_result]

        for result in filter_result:
            self.assertTrue(result[filter_str], filter_val)

    def filter_test_adv(self, filter_str, filter_val, op, endpoint):
        filter_result = self.api.get(
            f'http://api.localhost:5000/v1/{endpoint}/all?{filter_str}=${op}:{filter_val}').get_json()
        if endpoint == "stats":
            filter_result = self.api.get(
                f'http://api.localhost:5000/v1/{endpoint}?player_id=1152&{filter_str}=${op}:{filter_val}').get_json()

        if not isinstance(filter_result, list):
            filter_result = [filter_result]  # Handle returns as dict or list

        for result in filter_result:
            if op == "lt":
                self.assertLess(result[filter_str], filter_val)

            elif op == "lte":
                self.assertLessEqual(result[filter_str], filter_val)

            elif op == "gt":
                self.assertGreater(result[filter_str], filter_val)

            elif op == "gte":
                self.assertGreaterEqual(result[filter_str], filter_val)















