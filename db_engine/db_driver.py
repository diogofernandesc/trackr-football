from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.exc import IntegrityError
import logging
from ingest_engine.ingest_driver import Driver, str_comparator
from ingest_engine.cons import Competition as COMP, \
    Standings as STANDINGS, Team as TEAM, Match as MATCH, Player as PLAYER, MatchEvent as MATCH_EVENT, \
    FantasyGameWeek as FANTASY_GAME_WEEK

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

driver = Driver()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_TEST_CONNECTION_STR')  # For debugging/testing
db = SQLAlchemy(app)


# Used for the many-many relationship between competition and team
comp_team_table = db.Table('competitions',
                           db.Column('competition_id', db.Integer, db.ForeignKey('competition.id'), primary_key=True),
                           db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
                           )

# Used for the many-many relationship between team and match
team_match_table = db.Table('matches',
                            db.Column('match_id', db.Integer, db.ForeignKey('match.id'), primary_key=True),
                            db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
                            )

# Used for the many-many relationship between player and match
player_match_table = db.Table('player_matches',
                              db.Column('match_id', db.Integer, db.ForeignKey('match.id'), primary_key=True),
                              db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key=True)
                              )


class Competition(db.Model):
    id = db.Column(COMP.ID, db.Integer, primary_key=True)
    standings = db.relationship('Standings', backref='competition', lazy=True)
    name = db.Column(COMP.NAME, db.String(80), unique=False, nullable=False)
    code = db.Column(COMP.CODE, db.String(20), unique=False, nullable=True)
    location = db.Column(COMP.LOCATION, db.String(80), unique=False, nullable=False)
    fd_api_id = db.Column(COMP.FOOTBALL_DATA_API_ID, db.Integer, unique=True, nullable=False)
    fls_api_id = db.Column(COMP.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=True, nullable=False)


class Standings(db.Model):
    id = db.Column(STANDINGS.ID, db.Integer, primary_key=True)
    # standings_entries = db.relationship('StandingsEntry', backpopulates="standings")
    standings_entries = db.relationship('StandingsEntry', backref='standings', lazy='dynamic')
                                        # primaryjoin="standings.id==standings_entry.standings_id")
    competition_id = db.Column(STANDINGS.COMPETITION_ID, db.Integer, db.ForeignKey('competition.id'), nullable=False)
    type = db.Column(STANDINGS.TYPE, db.String(20), unique=False, nullable=True)
    season = db.Column(STANDINGS.SEASON, db.String(20), unique=False, nullable=True)
    match_day = db.Column(STANDINGS.MATCH_DAY, db.Integer, unique=False, nullable=True)
    group = db.Column(STANDINGS.GROUP, db.String, unique=False, nullable=True)


class StandingsEntry(db.Model):
    id = db.Column(STANDINGS.ID, db.Integer, primary_key=True)
    standings_id = db.Column(STANDINGS.STANDINGS_ID, db.Integer, db.ForeignKey('standings.id'), nullable=False)
    position = db.Column(STANDINGS.POSITION, db.Integer, unique=False, nullable=False)
    team_name = db.Column(STANDINGS.TEAM_NAME, db.String(80), unique=False, nullable=False)
    fd_team_id = db.Column(STANDINGS.FOOTBALL_DATA_TEAM_ID, db.Integer, unique=False, nullable=False)
    games_played = db.Column(STANDINGS.GAMES_PLAYED, db.Integer, unique=False, nullable=False)
    games_won = db.Column(STANDINGS.GAMES_WON, db.Integer, unique=False, nullable=False)
    games_drawn = db.Column(STANDINGS.GAMES_DRAWN, db.Integer, unique=False, nullable=False)
    games_lost = db.Column(STANDINGS.GAMES_LOST, db.Integer, unique=False, nullable=False)
    points = db.Column(STANDINGS.POINTS, db.Integer, unique=False, nullable=False)
    goals_for = db.Column(STANDINGS.GOALS_FOR, db.Integer, unique=False, nullable=False)
    goals_against = db.Column(STANDINGS.GOALS_AGAINST, db.Integer, unique=False, nullable=False)
    goals_difference = db.Column(STANDINGS.GOAL_DIFFERENCE, db.Integer, unique=False, nullable=False)


class Match(db.Model):
    id = db.Column(MATCH.ID, db.Integer, primary_key=True)
    stats = db.relationship('MatchStats', uselist=False, backref='match')
    fd_id = db.Column(MATCH.FOOTBALL_DATA_ID, db.Integer, unique=True, nullable=False)
    season_start_date = db.Column(MATCH.SEASON_START_DATE, db.Date, unique=False, nullable=True)
    season_end_date = db.Column(MATCH.SEASON_END_DATE, db.Date, unique=False, nullable=True)
    season_year = db.Column(MATCH.SEASON_YEAR,db.String, unique=False, nullable=True)
    utc_date = db.Column(MATCH.MATCH_UTC_DATE, db.Date, unique=False, nullable=True)
    start_time_epoch = db.Column(MATCH.START_TIME_EPOCH, db.Time, unique=False, nullable=True)
    start_time = db.Column(MATCH.START_TIME, db.DateTime, unique=False, nullable=True)
    status = db.Column(MATCH.STATUS, db.String(20), unique=False, nullable=True)
    match_day = db.Column(MATCH.MATCHDAY, db.Integer, unique=False, nullable=True)
    ft_home_score = db.Column(MATCH.FULL_TIME_HOME_SCORE, db.Integer, unique=False, nullable=True)
    ft_away_score = db.Column(MATCH.FULL_TIME_AWAY_SCORE, db.Integer, unique=False, nullable=True)
    ht_home_score = db.Column(MATCH.HALF_TIME_HOME_SCORE, db.Integer, unique=False, nullable=True)
    ht_away_score = db.Column(MATCH.HALF_TIME_AWAY_SCORE, db.Integer, unique=False, nullable=True)
    et_home_score = db.Column(MATCH.EXTRA_TIME_HOME_SCORE, db.Integer, unique=False, nullable=True)
    et_away_score = db.Column(MATCH.EXTRA_TIME_AWAY_SCORE, db.Integer, unique=False, nullable=True)
    p_home_score = db.Column(MATCH.PENALTY_HOME_SCORE, db.Integer, unique=False, nullable=True)
    p_away_score = db.Column(MATCH.PENALTY_AWAY_SCORE, db.Integer, unique=False, nullable=True)
    winner = db.Column(MATCH.WINNER, db.String(10), unique=False, nullable=True)
    home_team = db.Column(MATCH.HOME_TEAM, db.String(80), unique=False, nullable=True)
    away_team = db.Column(MATCH.AWAY_TEAM, db.String(80), unique=False, nullable=True)
    referees = db.Column(MATCH.REFEREES, db.ARRAY(db.String), unique=False, nullable=True)
    fls_match_id = db.Column(MATCH.FLS_MATCH_ID, db.Integer, unique=True, nullable=False)
    fls_competition_id = db.Column(MATCH.FLS_API_COMPETITION_ID, db.Integer, unique=False, nullable=False)
    competition = db.Column(MATCH.COMPETITION, db.String, unique=False, nullable=True)
    home_score_probability = db.Column(MATCH.HOME_SCORE_PROBABILITY, db.Float, unique=False, nullable=True)
    away_score_probability = db.Column(MATCH.AWAY_SCORE_PROBABILITY, db.Float, unique=False, nullable=True)
    home_concede_probability = db.Column(MATCH.HOME_CONCEDE_PROBABILITY, db.Float, unique=False, nullable=True)
    away_concede_probability = db.Column(MATCH.AWAY_CONCEDE_PROBABILITY, db.Float, unique=False, nullable=True)
    home_o15_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_OVER_1_5, db.Float, unique=False, nullable=True)
    home_o25_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_OVER_2_5, db.Float, unique=False, nullable=True)
    home_o35_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_OVER_3_5, db.Float, unique=False, nullable=True)
    home_u15_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_UNDER_1_5, db.Float, unique=False, nullable=True)
    home_u25_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_UNDER_2_5, db.Float, unique=False, nullable=True)
    home_u35_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_UNDER_3_5, db.Float, unique=False, nullable=True)
    away_o15_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_OVER_1_5, db.Float, unique=False, nullable=True)
    away_o25_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_OVER_2_5, db.Float, unique=False, nullable=True)
    away_o35_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_OVER_3_5, db.Float, unique=False, nullable=True)
    away_u15_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_UNDER_1_5, db.Float, unique=False, nullable=True)
    away_u25_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_UNDER_2_5, db.Float, unique=False, nullable=True)
    away_u35_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_UNDER_3_5, db.Float, unique=False, nullable=True)
    home_form = db.Column(MATCH.HOME_FORM, db.ARRAY(db.String), unique=False, nullable=True)
    away_form = db.Column(MATCH.AWAY_FORM, db.ARRAY(db.String), unique=False, nullable=True)
    h_fls_id = db.Column(MATCH.HOME_TEAM_FLS_ID, db.Integer, unique=False, nullable=False)
    a_fls_id = db.Column(MATCH.AWAY_TEAM_FLS_ID, db.Integer, unique=False, nullable=False)
    psc = db.Column(MATCH.PENALTY_SHOOTOUT_SCORE, db.String, unique=False, nullable=True)
    finished = db.Column(MATCH.FINISHED, db.Boolean, unique=False, nullable=True)
    fantasy_game_week = db.Column(MATCH.FANTASY_GAME_WEEK, db.Integer, unique=False, nullable=True)
    home_team_difficulty = db.Column(MATCH.FANTASY_HOME_TEAM_DIFFICULTY, db.Integer, unique=False, nullable=True)
    away_team_difficulty = db.Column(MATCH.FANTASY_AWAY_TEAM_DIFFICULTY, db.Integer, unique=False, nullable=True)
    fantasy_match_code = db.Column(MATCH.FANTASY_MATCH_CODE, db.Integer, unique=True, nullable=True)
    minutes = db.Column(MATCH.MINUTES, db.Integer, unique=False, nullable=True)
    f_home_team_code = db.Column(MATCH.FANTASY_HOME_TEAM_CODE, db.Integer, unique=False, nullable=True)
    f_away_team_code = db.Column(MATCH.FANTASY_AWAY_TEAM_CODE, db.Integer, unique=False, nullable=True)
    f_home_team_id = db.Column(MATCH.FANTASY_HOME_TEAM_ID, db.Integer, unique=False, nullable=True)
    f_away_team_id = db.Column(MATCH.FANTASY_AWAY_TEAM_ID, db.Integer, unique=False, nullable=True)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matches = db.relationship('Match', secondary=player_match_table, lazy='subquery',
                              backref=db.backref('player_teams', lazy=True))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    match_stats = db.relationship('MatchStats', backref='stats_player')
    week_stats = db.relationship('FantasyWeekStats', backref='week_stats_player', lazy=True)
    name = db.Column(PLAYER.NAME, db.String(200), unique=False, nullable=False)
    first_name = db.Column(PLAYER.FIRST_NAME, db.String(80), unique=False, nullable=True)
    last_name = db.Column(PLAYER.LAST_NAME, db.String(80), unique=False, nullable=True)
    date_of_birth = db.Column(PLAYER.DATE_OF_BIRTH, db.Date, unique=False, nullable=True)
    date_of_birth_epoch = db.Column(PLAYER.DATE_OF_BIRTH_EPOCH, db.BigInteger, unique=False, nullable=True)
    country_of_birth = db.Column(PLAYER.COUNTRY_OF_BIRTH, db.String(80), unique=False, nullable=True)
    nationality = db.Column(PLAYER.NATIONALITY, db.String(80), unique=False, nullable=True)
    position = db.Column(PLAYER.POSITION, db.String(80), unique=False, nullable=False)
    shirt_number = db.Column(PLAYER.SHIRT_NUMBER, db.Integer, unique=False, nullable=False)
    team = db.Column(PLAYER.TEAM, db.String(80), unique=False, nullable=False)
    number_of_goals = db.Column(PLAYER.NUMBER_OF_GOALS, db.Integer, unique=False, nullable=False)
    weight = db.Column(PLAYER.WEIGHT, db.Float, unique=False, nullable=True)
    gender = db.Column(PLAYER.GENDER, db.String(20), unique=False, nullable=True)
    height = db.Column(PLAYER.HEIGHT, db.Float, unique=False, nullable=True)
    team_fls_id = db.Column(PLAYER.TEAM_FLS_ID, db.Integer, unique=False, nullable=False)
    fd_api_id = db.Column(PLAYER.FOOTBALL_DATA_API_ID, db.Integer, unique=False, nullable=True)
    fls_api_id = db.Column(PLAYER.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=False, nullable=False)
    web_name = db.Column(PLAYER.FANTASY_WEB_NAME, db.String(80), unique=False, nullable=True)
    f_team_code = db.Column(PLAYER.FANTASY_TEAM_CODE, db.Integer, unique=False, nullable=True)
    f_id = db.Column(PLAYER.FANTASY_ID, db.Integer, unique=False, nullable=True)
    fantasy_status = db.Column(PLAYER.FANTASY_STATUS, db.String(80), unique=False, nullable=True)
    fantasy_code = db.Column(PLAYER.FANTASY_CODE, db.Integer, unique=False, nullable=True)
    fantasy_price = db.Column(PLAYER.FANTASY_PRICE, db.Float, unique=False, nullable=True)
    fantasy_news = db.Column(PLAYER.FANTASY_NEWS, db.String(200), unique=False, nullable=True)
    fantasy_news_timestamp = db.Column(PLAYER.FANTASY_NEWS_TIMESTAMP, db.TIMESTAMP, unique=False, nullable=True)
    photo_url = db.Column(PLAYER.FANTASY_PHOTO_URL, db.String(200), unique=False, nullable=True)
    fantasy_team_id = db.Column(PLAYER.FANTASY_TEAM_ID, db.Integer, unique=False, nullable=True)


class MatchStats(db.Model):
    id = db.Column(MATCH.ID, db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    occurred_timestamp = db.Column(MATCH_EVENT.OCCURED_AT, db.TIMESTAMP, unique=False, nullable=True)
    goals_scored = db.Column(MATCH.GOALS_SCORED, db.Integer, unique=False, nullable=True)
    goals_conceded = db.Column(MATCH.GOALS_CONCEDED, db.Integer, unique=False, nullable=True)
    assists = db.Column(MATCH.ASSISTS, db.Integer, unique=False, nullable=True)
    own_goals = db.Column(MATCH.OWN_GOALS, db.Integer, unique=False, nullable=True)
    penalties_saved = db.Column(MATCH.PENALTIES_SAVED, db.Integer, unique=False, nullable=True)
    penalties_missed = db.Column(MATCH.PENALTIES_MISSED, db.Integer, unique=False, nullable=True)
    yellow_cards = db.Column(MATCH.YELLOW_CARDS, db.Integer, unique=False, nullable=True)
    red_cards = db.Column(MATCH.RED_CARDS, db.Integer, unique=False, nullable=True)
    saves = db.Column(MATCH.SAVES, db.Integer, unique=False, nullable=True)
    bonus = db.Column(MATCH.BONUS, db.Integer, unique=False, nullable=True)
    bps = db.Column(MATCH.BPS, db.Integer, unique=False, nullable=True)
    substitution = db.Column(MATCH_EVENT.SUBSTITUTION, db.Integer, unique=False, nullable=True)
    clean_sheet = db.Column(MATCH_EVENT.CLEAN_SHEET, db.Boolean, unique=False, nullable=True)
    fantasy_influence = db.Column(PLAYER.FANTASY_INFLUENCE, db.Float, unique=False, nullable=True)
    fantasy_creativity = db.Column(PLAYER.FANTASY_CREATIVITY, db.Float, unique=False, nullable=True)
    fantasy_threat = db.Column(PLAYER.FANTASY_THREAT, db.Float, unique=False, nullable=True)
    fantasy_ict_index = db.Column(PLAYER.FANTASY_ICT_INDEX, db.Float, unique=False, nullable=True)
    open_play_crosses = db.Column(PLAYER.OPEN_PLAY_CROSSES, db.Integer, unique=False, nullable=True)
    big_chances_created = db.Column(PLAYER.BIG_CHANCES_CREATED, db.Integer, unique=False, nullable=True)
    big_chances_missed = db.Column(PLAYER.BIG_CHANCES_MISSED, db.Integer, unique=False, nullable=True)
    clearances_blocks_interceptions = db.Column(PLAYER.CLEARANCES_BLOCKS_INTERCEPTIONS, db.Integer, unique=False, nullable=True)
    recoveries = db.Column(PLAYER.RECOVERIES, db.Integer, unique=False, nullable=True)
    key_passes = db.Column(PLAYER.KEY_PASSES, db.Integer, unique=False, nullable=True)
    tackles = db.Column(PLAYER.TACKLES, db.Integer, unique=False, nullable=True)
    winning_goals = db.Column(PLAYER.WINNING_GOALS, db.Integer, unique=False, nullable=True)
    attempted_passes = db.Column(PLAYER.ATTEMPTED_PASSES, db.Integer, unique=False, nullable=True)
    completed_passes = db.Column(PLAYER.COMPLETED_PASSES, db.Integer, unique=False, nullable=True)
    penalties_conceded = db.Column(PLAYER.PENALTIES_CONCEDED, db.Integer, unique=False, nullable=True)
    errors_leading_to_goal = db.Column(PLAYER.ERRORS_LEADING_TO_GOAL, db.Integer, unique=False, nullable=True)
    errors_leading_to_goal_attempt = db.Column(PLAYER.ERRORS_LEADING_TO_GOAL_ATTEMPT, db.Integer, unique=False, nullable=True)
    tackled = db.Column(PLAYER.TACKLED, db.Integer, unique=False, nullable=True)
    offside = db.Column(PLAYER.OFFSIDE, db.Integer, unique=False, nullable=True)
    target_missed = db.Column(PLAYER.TARGET_MISSED, db.Integer, unique=False, nullable=True)
    fouls = db.Column(PLAYER.FOULS, db.Integer, unique=False, nullable=True)
    dribbles = db.Column(PLAYER.DRIBBLES, db.Integer, unique=False, nullable=True)
    played_at_home = db.Column(PLAYER.PLAYED_AT_HOME, db.Boolean, unique=False, nullable=True)


class FantasyWeekStats(db.Model):
    id = db.Column(FANTASY_GAME_WEEK.ID, db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_week = db.Column(FANTASY_GAME_WEEK.WEEK, db.Integer, unique=False, nullable=True)
    fantasy_price = db.Column(PLAYER.FANTASY_PRICE, db.Integer, unique=False, nullable=True)
    season_value = db.Column(PLAYER.FANTASY_SEASON_VALUE, db.Integer, unique=False, nullable=True)  # Fantasy value
    week_points = db.Column(PLAYER.FANTASY_WEEK_POINTS, db.Integer, unique=False, nullable=True)
    transfers_balance = db.Column(PLAYER.FANTASY_TRANSFERS_BALANCE, db.Integer, unique=False, nullable=True)
    selection_count = db.Column(PLAYER.FANTASY_SELECTION_COUNT, db.Integer, unique=False, nullable=True)
    transfers_in = db.Column(PLAYER.FANTASY_WEEK_TRANSFERS_IN, db.Integer, unique=False, nullable=True)
    transfers_out = db.Column(PLAYER.FANTASY_WEEK_TRANSFERS_OUT, db.Integer, unique=False, nullable=True)
    fantasy_overall_price_rise = db.Column(PLAYER.FANTASY_OVERALL_PRICE_RISE, db.Float, unique=False, nullable=True)
    fantasy_overall_price_fall = db.Column(PLAYER.FANTASY_OVERALL_PRICE_FALL, db.Float, unique=False, nullable=True)
    fantasy_week_price_rise = db.Column(PLAYER.FANTASY_WEEK_PRICE_RISE, db.Integer, unique=False, nullable=True)
    fantasy_week_price_fall = db.Column(PLAYER.FANTASY_WEEK_PRICE_FALL, db.Integer, unique=False, nullable=True)
    fantasy_overall_transfers_in = db.Column(PLAYER.FANTASY_OVERALL_TRANSFERS_IN, db.Integer, unique=False, nullable=True)
    fantasy_overall_transfers_out = db.Column(PLAYER.FANTASY_OVERALL_TRANSFERS_OUT, db.Integer, unique=False, nullable=True)
    fantasy_overall_points = db.Column(PLAYER.FANTASY_OVERALL_POINTS, db.Integer, unique=False, nullable=True)
    fantasy_point_average = db.Column(PLAYER.FANTASY_POINT_AVERAGE, db.Float, unique=False, nullable=True)
    fantasy_total_bonus = db.Column(PLAYER.FANTASY_TOTAL_BONUS, db.Float, unique=False, nullable=True)
    week_bonus = db.Column(PLAYER.FANTASY_WEEK_BONUS, db.Integer, unique=False, nullable=True)
    chance_of_playing_this_week = db.Column(PLAYER.FANTASY_CHANCE_OF_PLAYING_THIS_WEEK, db.Integer, unique=False, nullable=True)
    chance_of_playing_next_week = db.Column(PLAYER.FANTASY_CHANCE_OF_PLAYING_NEXT_WEEK, db.Integer, unique=False, nullable=True)
    fantasy_dream_team_member = db.Column(PLAYER.FANTASY_DREAM_TEAM_MEMBER, db.Boolean, unique=False, nullable=True)
    dream_team_count = db.Column(PLAYER.FANTASY_DREAM_TEAM_COUNT, db.Integer, unique=False, nullable=True)
    selection_percentage = db.Column(PLAYER.FANTASY_SELECTION_PERCENTAGE, db.Integer, unique=False, nullable=True)
    fantasy_form = db.Column(PLAYER.FANTASY_FORM, db.Integer, unique=False, nullable=True)
    fantasy_special = db.Column(PLAYER.FANTASY_SPECIAL, db.Boolean, unique=False, nullable=True)
    total_minutes_played = db.Column(PLAYER.MINUTES_PLAYED, db.Integer, unique=False, nullable=True)


class Team(db.Model):
    id = db.Column(TEAM.ID, db.Integer, primary_key=True)
    competitions = db.relationship('Competition', secondary=comp_team_table, lazy='subquery',
                                   backref=db.backref('comp_teams', lazy=True))
    matches = db.relationship('Match', secondary=team_match_table, lazy='subquery',
                              backref=db.backref('match_teams', lazy=True))
    squad = db.relationship('Player', backref='player_team', lazy=True)
    fantasy_id = db.Column(TEAM.FANTASY_ID, db.Integer, unique=True, nullable=False)
    fd_id = db.Column(TEAM.FOOTBALL_DATA_ID, db.Integer, unique=False, nullable=False)
    name = db.Column(TEAM.NAME, db.String(80), unique=False, nullable=False)
    country = db.Column(TEAM.COUNTRY, db.String(80), unique=False, nullable=False)
    short_name = db.Column(TEAM.SHORT_NAME, db.String(80), unique=False, nullable=False)
    acronym = db.Column(TEAM.ACRONYM, db.String(20), unique=False, nullable=False)
    crest_url = db.Column(TEAM.CREST_URL, db.String(120), unique=True, nullable=False)
    address = db.Column(TEAM.ADDRESS, db.String(120), unique=True, nullable=False)
    phone = db.Column(TEAM.PHONE, db.String, unique=True, nullable=False)
    website = db.Column(TEAM.WEBSITE, db.String(120), unique=True, nullable=False)
    email = db.Column(TEAM.EMAIL, db.String(80), unique=True, nullable=False)
    year_founded = db.Column(TEAM.YEAR_FOUNDED, db.Integer, unique=False, nullable=False)
    club_colours = db.Column(TEAM.CLUB_COLOURS, db.String(40), unique=False, nullable=False)
    stadium = db.Column(TEAM.STADIUM, db.String(120), unique=False, nullable=False)
    stadium_lat = db.Column(TEAM.STADIUM_LAT, db.Float, unique=False, nullable=False)
    stadium_long = db.Column(TEAM.STADIUM_LONG, db.Float, unique=False, nullable=False)
    stadium_capacity = db.Column(TEAM.STADIUM_CAPACITY, db.Integer, unique=False, nullable=False)
    fls_api_id = db.Column(TEAM.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=True, nullable=False)
    fantasy_code = db.Column(TEAM.FANTASY_CODE, db.Integer, unique=True, nullable=False)
    home_strength = db.Column(TEAM.FANTASY_OVERALL_HOME_STRENGTH, db.Integer, unique=False, nullable=False)
    away_strength = db.Column(TEAM.FANTASY_OVERALL_AWAY_STRENGTH, db.Integer, unique=False, nullable=False)
    attack_home_strength = db.Column(TEAM.FANTASY_ATTACK_HOME_STRENGTH, db.Integer, unique=False, nullable=False)
    attack_away_strength = db.Column(TEAM.FANTASY_ATTACK_AWAY_STRENGTH, db.Integer, unique=False, nullable=False)
    defense_home_strength = db.Column(TEAM.FANTASY_DEFENCE_HOME_STRENGTH, db.Integer, unique=False, nullable=False)
    defense_away_strength = db.Column(TEAM.FANTASY_DEFENCE_AWAY_STRENGTH, db.Integer, unique=False, nullable=False)


# db.create_all()
def ingest_competitions():
    """
    Ingest ingest_engine competition result into DB
    :return: Records in DB
    """
    competitions = driver.request_competitions()
    for comp in competitions:
        db_comp = Competition(**comp)
        # db_comp = Competition(name=comp[COMP.NAME],
        #                       code=comp[COMP.CODE],
        #                       location=comp[COMP.LOCATION],
        #                       fd_api_id=comp[COMP.FOOTBALL_DATA_API_ID],
        #                       fls_api_id=comp[COMP.FASTEST_LIVE_SCORES_API_ID]
        #                       )
        standings = driver.request_standings(competition_id=comp[COMP.FOOTBALL_DATA_API_ID])
        if standings:
            for stan in standings['standings']:
                table = stan.pop(STANDINGS.TABLE, [])
                db_standing = Standings(**stan)

                for entry in table:
                    se = StandingsEntry(**entry)
                    db_standing.standings_entries.append(se)

                db_comp.standings.append(db_standing)

            db.session.add(db_comp)
            db.session.commit()


def ingest_players(team_fls_id):
    """
    Parse players result into db
    :param team_fls_id: the team id for players to request
    :return: Player records in DB
    """
    players = driver.request_player_details(team_fls_id=team_fls_id)
    for player in players:
        db_player = Player(
            name=player[PLAYER.NAME],
            position=player[PLAYER.POSITION],
            shirt_number=player[PLAYER.SHIRT_NUMBER],
            team=player[PLAYER.TEAM],
            number_of_goals=player[PLAYER.NUMBER_OF_GOALS],
            weight=player[PLAYER.WEIGHT],
            gender=player[PLAYER.GENDER],
            height=player[PLAYER.HEIGHT],
            team_fls_id=player[PLAYER.TEAM_FLS_ID],
            fls_api_id=player[PLAYER.FASTEST_LIVE_SCORES_API_ID]
        )

        if PLAYER.FOOTBALL_DATA_API_ID in player:
            db_player.fd_api_id = player[PLAYER.FOOTBALL_DATA_API_ID]

        if PLAYER.NATIONALITY in player:
            db_player.nationality = player[PLAYER.NATIONALITY],

        if PLAYER.COUNTRY_OF_BIRTH in player:
            db_player.country_of_birth = player[PLAYER.COUNTRY_OF_BIRTH]

        if PLAYER.DATE_OF_BIRTH_EPOCH in player:
            db_player.date_of_birth_epoch = player[PLAYER.DATE_OF_BIRTH_EPOCH]

        if PLAYER.DATE_OF_BIRTH in player:
            db_player.date_of_birth = player[PLAYER.DATE_OF_BIRTH]

        if PLAYER.FIRST_NAME in player:
            db_player.first_name = player[PLAYER.FIRST_NAME]

        if PLAYER.LAST_NAME in player:
            db_player.last_name = player[PLAYER.LAST_NAME]

        if PLAYER.FANTASY_WEB_NAME in player:
            db_player.web_name = player[PLAYER.FANTASY_WEB_NAME]

        if PLAYER.FANTASY_TEAM_CODE in player:
            db_player.f_team_code = player[PLAYER.FANTASY_TEAM_CODE]

        if PLAYER.FANTASY_ID in player:
            db_player.f_id = player[PLAYER.FANTASY_ID]

        if PLAYER.FANTASY_STATUS in player:
            db_player.fantasy_status = player[PLAYER.FANTASY_STATUS]

        if PLAYER.FANTASY_CODE in player:
            db_player.fantasy_code = player[PLAYER.FANTASY_CODE]

        if PLAYER.FANTASY_PRICE in player:
            db_player.fantasy_price = player[PLAYER.FANTASY_PRICE]

        if PLAYER.FANTASY_NEWS in player:
            db_player.fantasy_news = player[PLAYER.FANTASY_NEWS]

        if PLAYER.FANTASY_NEWS_TIMESTAMP in player:
            db_player.fantasy_news_timestamp = player[PLAYER.FANTASY_NEWS_TIMESTAMP]

        if PLAYER.FANTASY_PHOTO_URL in player:
            db_player.photo_url = player[PLAYER.FANTASY_PHOTO_URL]

        if PLAYER.FANTASY_TEAM_ID in player:
            db_player.fantasy_team_id = player[PLAYER.FANTASY_TEAM_ID]

        db.session.add(db_player)
        db.session.commit()


def ingest_teams(fls_comp_id, fd_comp_id, season):
    """
    Parsed ingest_engine result into database
    :param db_id: Postgres ID for the competition for which team belongs
    :param fls_comp_id: Competition id from FLS
    :param fd_comp_id: Competition id from FootballData.org
    :param season: season for which the data belongs
    :return: Team records in DB
    """
    teams = driver.request_teams(fd_comp_id=fd_comp_id, fls_comp_id=fls_comp_id, season=season)

    for team in teams[:1]:
        team_players = driver.request_player_details(team_fls_id=team[TEAM.FASTEST_LIVE_SCORES_API_ID])
        db_team = Team(fantasy_id=team[TEAM.FANTASY_ID],
                       fd_id=team[TEAM.FOOTBALL_DATA_ID],
                       name=team[TEAM.NAME],
                       country=team[TEAM.COUNTRY],
                       short_name=team[TEAM.SHORT_NAME],
                       acronym=team[TEAM.ACRONYM],
                       crest_url=team[TEAM.CREST_URL],
                       address=team[TEAM.ADDRESS],
                       phone=team[TEAM.PHONE],
                       website=team[TEAM.WEBSITE],
                       email=team[TEAM.EMAIL],
                       year_founded=team[TEAM.YEAR_FOUNDED],
                       club_colours=team[TEAM.CLUB_COLOURS],
                       stadium=team[TEAM.STADIUM],
                       stadium_lat=team[TEAM.STADIUM_LAT],
                       stadium_long=team[TEAM.STADIUM_LONG],
                       stadium_capacity=team[TEAM.STADIUM_CAPACITY],
                       fls_api_id=team[TEAM.FASTEST_LIVE_SCORES_API_ID],
                       fantasy_code=team[TEAM.FANTASY_CODE],
                       home_strength=team[TEAM.FANTASY_OVERALL_HOME_STRENGTH],
                       away_strength=team[TEAM.FANTASY_OVERALL_AWAY_STRENGTH],
                       attack_home_strength=team[TEAM.FANTASY_ATTACK_HOME_STRENGTH],
                       attack_away_strength=team[TEAM.FANTASY_ATTACK_AWAY_STRENGTH],
                       defense_home_strength=team[TEAM.FANTASY_DEFENCE_HOME_STRENGTH],
                       defense_away_strength=team[TEAM.FANTASY_DEFENCE_AWAY_STRENGTH]
                       )
        for player in team[TEAM.SQUAD]:
            for pl in team_players:
                if str_comparator(player[Player.NAME].split(" ")[0], pl[Player.FIRST_NAME]) >= 0.8 or \
                        str_comparator(player[Player.NAME].split(" ")[0], pl[Player.FANTASY_WEB_NAME]) >= 0.8:
                    full_player = {**player, **pl}
                    db_player = Player(
                        first_name=full_player[PLAYER.FIRST_NAME],
                        last_name=full_player[PLAYER.LAST_NAME],
                        name=full_player[PLAYER.NAME],
                        date_of_birth=full_player[PLAYER.DATE_OF_BIRTH],
                        date_of_birth_epoch=full_player[PLAYER.DATE_OF_BIRTH_EPOCH],
                        country_of_birth=full_player[PLAYER.COUNTRY_OF_BIRTH],
                        nationality=full_player[PLAYER.NATIONALITY],
                        position=full_player[PLAYER.POSITION],
                        shirt_number=full_player[PLAYER.SHIRT_NUMBER],
                        team=full_player[PLAYER.TEAM],
                        number_of_goals=full_player[PLAYER.NUMBER_OF_GOALS],
                        weight=full_player[PLAYER.WEIGHT],
                        gender=full_player[PLAYER.GENDER],
                        height=full_player[PLAYER.HEIGHT],
                        team_fls_id=full_player[PLAYER.TEAM_FLS_ID],
                        fd_api_id=full_player[PLAYER.FOOTBALL_DATA_API_ID],
                        fls_api_id=full_player[PLAYER.FASTEST_LIVE_SCORES_API_ID],
                        web_name=full_player[PLAYER.FANTASY_WEB_NAME],
                        f_team_code=full_player[PLAYER.FANTASY_TEAM_CODE],
                        f_id=full_player[PLAYER.FANTASY_ID],
                        fantasy_status=full_player[PLAYER.FANTASY_STATUS],
                        fantasy_code=full_player[PLAYER.FANTASY_CODE],
                        fantasy_price=full_player[PLAYER.FANTASY_PRICE],
                        fantasy_news=full_player[PLAYER.FANTASY_NEWS],
                        fantasy_news_timestamp=full_player[PLAYER.FANTASY_NEWS_TIMESTAMP],
                        photo_url=full_player[PLAYER.FANTASY_PHOTO_URL],
                        fantasy_team_id=full_player[PLAYER.FANTASY_TEAM_ID]
                    )

                    if PLAYER.SEASON_MATCH_HISTORY in full_player:
                        week_count = 1
                        week_list = []
                        for week in full_player[PLAYER.SEASON_MATCH_HISTORY]:
                            week_stats = FantasyWeekStats(
                                game_week=week_count,
                                season_value=week[PLAYER.FANTASY_SEASON_VALUE],
                                week_points=week[PLAYER.FANTASY_WEEK_POINTS],
                                transfers_balance=week[PLAYER.FANTASY_TRANSFERS_BALANCE],
                                selection_count=week[PLAYER.FANTASY_SELECTION_COUNT],
                                transfers_in=week[PLAYER.FANTASY_WEEK_TRANSFERS_IN],
                                transfers_out=week[PLAYER.FANTASY_WEEK_TRANSFERS_OUT],
                            )
                            week_list.append(week_stats)
                            week_count += 1

                        if PLAYER.FANTASY_WEEK in full_player:
                            current_week = full_player[PLAYER.FANTASY_WEEK]
                            current_week_stats = FantasyWeekStats()
                            current_week_stats.game_week = current_week
                            current_week_stats.season_value = full_player[PLAYER.FANTASY_SEASON_VALUE]
                            current_week_stats.week_points = full_player[PLAYER.FANTASY_WEEK_POINTS]
                            current_week_stats.fantasy_price = full_player[PLAYER.FANTASY_PRICE]
                            current_week_stats.selection_percentage = full_player[PLAYER.FANTASY_SELECTION_PERCENTAGE]
                            current_week_stats.transfers_in = full_player[PLAYER.FANTASY_WEEK_TRANSFERS_IN]
                            current_week_stats.transfers_out = full_player[PLAYER.FANTASY_WEEK_TRANSFERS_OUT]
                            current_week_stats.fantasy_overall_price_rise = \
                                full_player[PLAYER.FANTASY_OVERALL_PRICE_RISE]
                            current_week_stats.fantasy_overall_price_fall = \
                                full_player[PLAYER.FANTASY_OVERALL_PRICE_FALL]
                            current_week_stats.fantasy_week_price_rise = full_player[PLAYER.FANTASY_WEEK_PRICE_RISE]
                            current_week_stats.fantasy_week_price_fall = full_player[PLAYER.FANTASY_WEEK_PRICE_FALL]
                            current_week_stats.fantasy_overall_transfers_in = \
                                full_player[PLAYER.FANTASY_OVERALL_TRANSFERS_IN]
                            current_week_stats.fantasy_overall_transfers_out = \
                                full_player[PLAYER.FANTASY_OVERALL_TRANSFERS_OUT]
                            current_week_stats.fantasy_overall_points = full_player[PLAYER.FANTASY_OVERALL_POINTS]
                            current_week_stats.fantasy_point_average = full_player[PLAYER.FANTASY_POINT_AVERAGE]
                            current_week_stats.fantasy_total_bonus = full_player[PLAYER.FANTASY_TOTAL_BONUS]
                            current_week_stats.week_bonus = full_player[PLAYER.FANTASY_WEEK_BONUS]
                            current_week_stats.chance_of_playing_this_week = \
                                full_player[PLAYER.FANTASY_CHANCE_OF_PLAYING_THIS_WEEK]
                            current_week_stats.chance_of_playing_next_week = \
                                full_player[PLAYER.FANTASY_CHANCE_OF_PLAYING_NEXT_WEEK]
                            current_week_stats.fantasy_dream_team_member = full_player[PLAYER.FANTASY_DREAM_TEAM_MEMBER]
                            current_week_stats.dream_team_count = full_player[PLAYER.FANTASY_DREAM_TEAM_COUNT]
                            current_week_stats.fantasy_form = full_player[PLAYER.FANTASY_FORM]
                            current_week_stats.fantasy_special = full_player[PLAYER.FANTASY_SPECIAL]
                            current_week_stats.total_minutes_played = full_player[PLAYER.MINUTES_PLAYED]
                            week_list.append(current_week_stats)
                            db_player.week_stats = week_list

                    db_team.squad.append(db_player)
                    db.session.add(db_team)
                    try:
                        db.session.commit()
                    except IntegrityError as e:
                        logging.error(e)
                        db.session.rollback()


if __name__ == "__main__":
    db.create_all()
    ingest_competitions()

    # teams = db.session\
    #     .query(func.max(StandingsEntry.points),
    #            StandingsEntry.team_name, StandingsEntry.team).filter_by(standings_id=8).group_by(StandingsEntry.team_name).all()
    # teams = driver.request_teams(fd_comp_id=2021, fls_comp_id=2, season=2018)  # PREMIER LEAGUE
    # for team in teams:
    #     ingest_players(team_fls_id=team[TEAM.FASTEST_LIVE_SCORES_API_ID])
    # db.session.commit()
    # competitions = Competition.query.all()
    # ingest_competitions()

    # ingest_teams(fls_comp_id=2, fd_comp_id=2021, season=2018)
















