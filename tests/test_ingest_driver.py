import unittest
import json
from ingest_engine.football_data import FootballData
from ingest_engine.ingest_driver import Driver, str_comparator
from ingest_engine.cons import Competition, Match, Season, Team, Standings, Player, FootballDataApiFilters as fdf
from ingest_engine.cons import FLSApiFilters as flsf
from ingest_engine.fantasy_api import team_mapper
import os


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.driver = Driver()

    def tearDown(self):
        pass

    def testStringComparator(self):
        hello1 = "Hello"
        hello2 = "Hello"
        self.assertTrue(str_comparator(hello1, hello2) == 1)
        champions_league1 = "Champions League"
        champions_league2 = "UEFA Champions League"
        self.assertTrue(str_comparator(champions_league1, champions_league2) >= 0.9)
        random_word1 = "altogether"
        random_word2 = "nevermind"
        self.assertTrue(str_comparator(random_word1, random_word2) <= 0.5)

    def testRequestCompetitions(self):
        competitions = self.driver.request_competitions()
        for comp in competitions:
            self.assertTrue(all(k in comp for k in (Competition.NAME,
                                                    Competition.CODE,
                                                    Competition.LOCATION,
                                                    Competition.FOOTBALL_DATA_API_ID,
                                                    Competition.FASTEST_LIVE_SCORES_API_ID)))

    def testRequestMatch(self):
        # In FLS, 2 is id for premier league, 2021 in football-data
        fls_comp_id = 2
        fd_comp_id = 2021
        game_week = 1
        season = 2018
        final_matches_result = self.driver.request_match(competition_name="test", game_week=game_week, season=season)
        fantasy_matches = self.driver.fantasy.request_matches()
        fd_matches = self.driver.fd.request_competition_match(competition_id=fd_comp_id,
                                                       **{fdf.MATCHDAY: game_week, fdf.SEASON: season})
        game_week_start = f'{fd_matches[0][Match.MATCH_UTC_DATE].split("T")[0]}T00:00:00'
        fls_matches = self.driver.fls.request_matches(**{flsf.COMPETITION_ID: fls_comp_id,
                                                         flsf.FROM_DATETIME: game_week_start})

        for match in final_matches_result:
            for fls_match in fls_matches:
                if fls_match[Match.HOME_TEAM] in match[Match.HOME_TEAM] and \
                    fls_match[Match.AWAY_TEAM] in match[Match.AWAY_TEAM] and \
                        match[Match.FULL_TIME_HOME_SCORE] == fls_match[Match.FULL_TIME_HOME_SCORE] and \
                        match[Match.FULL_TIME_AWAY_SCORE] == fls_match[Match.FULL_TIME_AWAY_SCORE]:
                    self.assertEqual(fls_match[Match.FLS_MATCH_ID], match[Match.FLS_MATCH_ID])

                self.assertTrue(all(k in match for k in fls_match))

            for f_match in fantasy_matches:
                f_home_team = team_mapper(f_match[Match.FANTASY_HOME_TEAM_ID])
                f_away_team = team_mapper(f_match[Match.FANTASY_AWAY_TEAM_ID])
                if f_match[Match.START_TIME] == match[Match.MATCH_UTC_DATE]:
                    if f_home_team in match[Match.HOME_TEAM] and f_away_team in match[Match.AWAY_TEAM] and \
                            match[Match.FULL_TIME_HOME_SCORE] == f_match[Match.FULL_TIME_HOME_SCORE] and \
                            match[Match.FULL_TIME_AWAY_SCORE] == f_match[Match.FULL_TIME_AWAY_SCORE]:
                        self.assertEqual(f_match[Match.FANTASY_MATCH_CODE], match[Match.FANTASY_MATCH_CODE])

                self.assertTrue(all(k in match for k in f_match))

            self.assertTrue(all(k in match for k in [Match.FOOTBALL_DATA_ID,
                                                     Match.SEASON_START_DATE,
                                                     Match.SEASON_END_DATE,
                                                     Match.MATCH_UTC_DATE,
                                                     Match.STATUS,
                                                     Match.MATCHDAY,
                                                     Match.FULL_TIME_HOME_SCORE,
                                                     Match.FULL_TIME_AWAY_SCORE,
                                                     Match.HALF_TIME_HOME_SCORE,
                                                     Match.HALF_TIME_AWAY_SCORE,
                                                     Match.EXTRA_TIME_HOME_SCORE,
                                                     Match.EXTRA_TIME_AWAY_SCORE,
                                                     Match.PENALTY_HOME_SCORE,
                                                     Match.PENALTY_AWAY_SCORE,
                                                     Match.WINNER,
                                                     Match.HOME_TEAM,
                                                     Match.AWAY_TEAM]))

    def testRequestTeams(self):
        teams = self.driver.request_teams(competition_name="test", season=2018)
        # Testing
        fls_comp_id = 2
        fd_comp_id = 2021
        fls_teams = self.driver.fls.request_teams(**{flsf.COMPETITION_ID: fls_comp_id})
        f_teams = self.driver.fantasy.request_base_information()['teams']

        for team in teams:
            for fls_team in fls_teams:
                if str_comparator(team[Team.NAME], fls_team[Team.NAME]) >= 0.9:
                    self.assertEqual(team[Team.FASTEST_LIVE_SCORES_API_ID], fls_team[Team.FASTEST_LIVE_SCORES_API_ID])
                    self.assertTrue(all(k in team for k in fls_team))

            for f_team in f_teams:
                if str_comparator(team[Team.NAME], f_team[Team.NAME]) >= 0.9:
                    self.assertEqual(team[Team.FANTASY_ID], f_team[Team.FANTASY_ID])
                    self.assertTrue(all(k in team for k in f_team))

            self.assertTrue(all(k in team for k in [Team.FOOTBALL_DATA_ID,
                                                    Team.NAME,
                                                    Team.SHORT_NAME,
                                                    Team.COUNTRY,
                                                    Team.CREST_URL,
                                                    Team.ADDRESS,
                                                    Team.PHONE,
                                                    Team.WEBSITE,
                                                    Team.EMAIL,
                                                    Team.YEAR_FOUNDED,
                                                    Team.CLUB_COLOURS,
                                                    Team.STADIUM]))

            if Team.ACTIVE_COMPETITIONS in team:
                for competition in team[Team.ACTIVE_COMPETITIONS]:
                    self.assertTrue(all(k in competition for k in [Competition.FOOTBALL_DATA_API_ID,
                                                                   Competition.LOCATION,
                                                                   Competition.NAME,
                                                                   Competition.CODE]))
            if Team.SQUAD in team:
                for member in team[Team.SQUAD]:
                    self.assertTrue(all(k in member for k in [Player.NAME,
                                                              Player.POSITION,
                                                              Player.DATE_OF_BIRTH,
                                                              Player.COUNTRY_OF_BIRTH,
                                                              Player.NATIONALITY,
                                                              Player.SHIRT_NUMBER,
                                                              Team.SQUAD_ROLE]))

    def testStandings(self):
        standings = self.driver.request_standings(competition_id=2021)
        self.assertIn(Standings.COMPETITION_NAME, standings)
        self.assertEqual(type(standings[Standings.COMPETITION_NAME]), str)
        self.assertGreater(len(standings["standings"]), 0)
        for standing in standings["standings"]:
            self.assertTrue(all(k in standing for k in [Standings.STAGE,
                                                        Standings.TYPE,
                                                        Standings.SEASON,
                                                        Standings.GROUP,
                                                        Standings.MATCH_DAY,
                                                        Standings.TABLE]))
            for entry in standing[Standings.TABLE]:
                self.assertTrue(all(k in entry for k in [Standings.POSITION,
                                                         Standings.TEAM_NAME,
                                                         Standings.FOOTBALL_DATA_TEAM_ID,
                                                         Standings.GAMES_PLAYED,
                                                         Standings.GAMES_WON,
                                                         Standings.GAMES_DRAWN,
                                                         Standings.GAMES_LOST,
                                                         Standings.POINTS,
                                                         Standings.GOALS_FOR,
                                                         Standings.GOALS_AGAINST,
                                                         Standings.GOAL_DIFFERENCE]))

    def testPlayerDetails(self):
        players = self.driver.request_player_details(team_fls_id=1)
        self.assertTrue(len(players) > 0)
        for player in players:
            self.assertTrue(all(k in player for k in [Player.NAME,
                                                      Player.WEIGHT,
                                                      Player.GENDER,
                                                      Player.TEAM,
                                                      Player.TEAM_FLS_ID,
                                                      Player.SHIRT_NUMBER,
                                                      Player.HEIGHT,
                                                      Player.DATE_OF_BIRTH_EPOCH,
                                                      Player.FASTEST_LIVE_SCORES_API_ID,
                                                      Player.POSITION,
                                                      Player.COMPETITION_STATS,
                                                      Player.FANTASY_ID,
                                                      Player.SEASON_SUMMARIES,
                                                      ]))

            for stat in player[Player.COMPETITION_STATS]:
                self.assertTrue(all(k in stat for k in [Competition.NAME,
                                                        Competition.FASTEST_LIVE_SCORES_API_ID,
                                                        Player.ASSISTS,
                                                        Player.NUMBER_OF_GOALS,
                                                        Player.RED_CARDS,
                                                        Player.YELLOW_CARDS]))

            for summary in player[Player.SEASON_SUMMARIES]:
                self.assertTrue(all(k in summary for k in [Season.NAME,
                                                           Player.FANTASY_CODE,
                                                           Player.FANTASY_SEASON_START_PRICE,
                                                           Player.FANTASY_OVERALL_POINTS,
                                                           Player.MINUTES_PLAYED,
                                                           Player.NUMBER_OF_GOALS,
                                                           Player.ASSISTS,
                                                           Player.CLEAN_SHEETS,
                                                           Player.GOALS_CONCEDED,
                                                           Player.OWN_GOALS,
                                                           Player.PENALTIES_SAVED,
                                                           Player.PENALTIES_MISSED,
                                                           Player.YELLOW_CARDS,
                                                           Player.RED_CARDS,
                                                           Player.SAVES,
                                                           Player.FANTASY_TOTAL_BONUS]))

            for match in player[Player.SEASON_MATCH_HISTORY]:
                self.assertTrue(all(k in match for k in [Match.START_TIME,
                                                         Match.FULL_TIME_HOME_SCORE,
                                                         Match.FULL_TIME_AWAY_SCORE,
                                                         Player.PLAYED_AT_HOME,
                                                         Player.FANTASY_WEEK_POINTS,
                                                         Player.FANTASY_SEASON_VALUE,
                                                         Player.FANTASY_TRANSFERS_BALANCE,
                                                         Player.FANTASY_SELECTION_COUNT,
                                                         Player.FANTASY_WEEK_TRANSFERS_IN,
                                                         Player.FANTASY_WEEK_TRANSFERS_OUT,
                                                         Player.MINUTES_PLAYED,
                                                         Player.NUMBER_OF_GOALS,
                                                         Player.ASSISTS,
                                                         Player.CLEAN_SHEETS,
                                                         Player.GOALS_CONCEDED,
                                                         Player.OWN_GOALS,
                                                         Player.PENALTIES_SAVED,
                                                         Player.PENALTIES_MISSED,
                                                         Player.YELLOW_CARDS,
                                                         Player.RED_CARDS,
                                                         Player.SAVES,
                                                         Player.FANTASY_WEEK_BONUS,
                                                         Player.FANTASY_INFLUENCE,
                                                         Player.FANTASY_CREATIVITY,
                                                         Player.FANTASY_THREAT,
                                                         Player.FANTASY_ICT_INDEX,
                                                         Player.OPEN_PLAY_CROSSES,
                                                         Player.BIG_CHANCES_CREATED,
                                                         Player.CLEARANCES_BLOCKS_INTERCEPTIONS,
                                                         Player.RECOVERIES,
                                                         Player.KEY_PASSES,
                                                         Player.WINNING_GOALS,
                                                         Player.ATTEMPTED_PASSES,
                                                         Player.COMPLETED_PASSES,
                                                         Player.PENALTIES_CONCEDED,
                                                         Player.BIG_CHANCES_MISSED,
                                                         Player.ERRORS_LEADING_TO_GOAL,
                                                         Player.ERRORS_LEADING_TO_GOAL_ATTEMPT,
                                                         Player.TACKLED,
                                                         Player.OFFSIDE,
                                                         Player.TARGET_MISSED,
                                                         Player.FOULS,
                                                         Player.DRIBBLES,
                                                         Player.FANTASY_OPPONENT_TEAM_ID]))
