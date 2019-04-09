from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os
from sqlalchemy.exc import IntegrityError
import logging
from ingest_engine.ingest_driver import Driver, str_comparator
from ingest_engine.cons import Competition as COMP, \
    Standings as STANDINGS, Team as TEAM, Match as MATCH, Player as PLAYER

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

driver = Driver()
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_TEST_CONNECTION_STR')  # For debugging/testing
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
    id = db.Column(db.Integer, primary_key=True)
    standings = db.relationship('Standings', backref='competition', lazy=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    code = db.Column(db.String(20), unique=False, nullable=True)
    location = db.Column(db.String(80), unique=False, nullable=False)
    fd_api_id = db.Column(COMP.FOOTBALL_DATA_API_ID, db.Integer, unique=True, nullable=False)
    fls_api_id = db.Column(COMP.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=True, nullable=False)


class Standings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # standings_entries = db.relationship('StandingsEntry', backpopulates="standings")
    standings_entries = db.relationship('StandingsEntry', backref='standings', lazy=True)
                                        # primaryjoin="standings.id==standings_entry.standings_id")
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    type = db.Column(db.String(20), unique=False, nullable=False)
    season = db.Column(db.String(20), unique=False, nullable=False)
    match_day = db.Column(db.Integer, unique=False, nullable=False)


class StandingsEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    standings_id = db.Column(db.Integer, db.ForeignKey('standings.id'), nullable=False)
    position = db.Column(db.Integer, unique=False, nullable=False)
    team_name = db.Column(db.String(80), unique=False, nullable=False)
    fd_team_id = db.Column(STANDINGS.FOOTBALL_DATA_TEAM_ID, db.Integer, unique=False, nullable=False)
    games_played = db.Column(db.Integer, unique=False, nullable=False)
    games_won = db.Column(db.Integer, unique=False, nullable=False)
    games_drawn = db.Column(db.Integer, unique=False, nullable=False)
    games_lost = db.Column(db.Integer, unique=False, nullable=False)
    points = db.Column(db.Integer, unique=False, nullable=False)
    goals_for = db.Column(db.Integer, unique=False, nullable=False)
    goals_against = db.Column(db.Integer, unique=False, nullable=False)
    goals_difference = db.Column(db.Integer, unique=False, nullable=False)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stats = db.relationship('MatchStats', uselist=False, backref='match')
    fd_id = db.Column(MATCH.FOOTBALL_DATA_ID, db.Integer, unique=True, nullable=False)
    season_start_date = db.Column(db.Date, unique=False, nullable=False)
    season_end_date = db.Column(db.Date, unique=False, nullable=False)
    season_year = db.Column(db.Integer, unique=False, nullable=False)
    utc_date = db.Column(db.Date, unique=False, nullable=False)
    start_time_epoch = db.Column(db.Time, unique=False, nullable=False)
    start_time = db.Column(db.DateTime, unique=False, nullable=False)
    status = db.Column(db.String(20), unique=False, nullable=False)
    match_day = db.Column(db.Integer, unique=False, nullable=False)
    ft_home_score = db.Column(MATCH.FULL_TIME_HOME_SCORE, db.Integer, unique=False, nullable=False)
    ft_away_score = db.Column(MATCH.FULL_TIME_AWAY_SCORE, db.Integer, unique=False, nullable=False)
    ht_home_score = db.Column(MATCH.HALF_TIME_HOME_SCORE, db.Integer, unique=False, nullable=False)
    ht_away_score = db.Column(MATCH.HALF_TIME_AWAY_SCORE, db.Integer, unique=False, nullable=False)
    et_home_score = db.Column(MATCH.EXTRA_TIME_HOME_SCORE, db.Integer, unique=False, nullable=True)
    et_away_score = db.Column(MATCH.EXTRA_TIME_AWAY_SCORE, db.Integer, unique=False, nullable=True)
    p_home_score = db.Column(MATCH.PENALTY_HOME_SCORE, db.Integer, unique=False, nullable=True)
    p_away_score = db.Column(MATCH.PENALTY_AWAY_SCORE, db.Integer, unique=False, nullable=True)
    winner = db.Column(db.String(10), unique=False, nullable=False)
    home_team = db.Column(db.String(80), unique=False, nullable=False)
    away_team = db.Column(db.String(80), unique=False, nullable=False)
    referees = db.Column(db.ARRAY(db.String), unique=False, nullable=False)
    fls_match_id = db.Column(MATCH.FLS_MATCH_ID, db.Integer, unique=True, nullable=False)
    fls_competition_id = db.Column(MATCH.FLS_API_COMPETITION_ID, db.Integer, unique=False, nullable=False)
    competition = db.Column(MATCH.COMPETITION, db.String, unique=False, nullable=False)
    home_score_probability = db.Column(db.Float, unique=False, nullable=False)
    away_score_probability = db.Column(db.Float, unique=False, nullable=False)
    home_concede_probability = db.Column(db.Float, unique=False, nullable=False)
    away_concede_probability = db.Column(db.Float, unique=False, nullable=False)
    home_o15_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_OVER_1_5, db.Float, unique=False, nullable=False)
    home_o25_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_OVER_2_5, db.Float, unique=False, nullable=False)
    home_o35_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_OVER_3_5, db.Float, unique=False, nullable=False)
    home_u15_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_UNDER_1_5, db.Float, unique=False, nullable=False)
    home_u25_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_UNDER_2_5, db.Float, unique=False, nullable=False)
    home_u35_prob = db.Column(MATCH.HOME_SCORE_PROBABILITY_UNDER_3_5, db.Float, unique=False, nullable=False)
    away_o15_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_OVER_1_5, db.Float, unique=False, nullable=False)
    away_o25_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_OVER_2_5, db.Float, unique=False, nullable=False)
    away_o35_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_OVER_3_5, db.Float, unique=False, nullable=False)
    away_u15_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_UNDER_1_5, db.Float, unique=False, nullable=False)
    away_u25_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_UNDER_2_5, db.Float, unique=False, nullable=False)
    away_u35_prob = db.Column(MATCH.AWAY_SCORE_PROBABILITY_UNDER_3_5, db.Float, unique=False, nullable=False)
    home_form = db.Column(db.ARRAY(db.String), unique=False, nullable=False)
    away_form = db.Column(db.ARRAY(db.String), unique=False, nullable=False)
    h_fls_id = db.Column(MATCH.HOME_TEAM_FLS_ID, db.Integer, unique=False, nullable=False)
    a_fls_id = db.Column(MATCH.AWAY_TEAM_FLS_ID, db.Integer, unique=False, nullable=False)
    psc = db.Column(MATCH.PENALTY_SHOOTOUT_SCORE, db.String, unique=False, nullable=False)
    finished = db.Column(db.Boolean, unique=False, nullable=False)
    fantasy_game_week = db.Column(db.Integer, unique=False, nullable=False)
    home_team_difficulty = db.Column(db.Integer, unique=False, nullable=False)
    away_team_difficulty = db.Column(db.Integer, unique=False, nullable=False)
    fantasy_match_code = db.Column(db.Integer, unique=True, nullable=False)
    minutes = db.Column(db.Integer, unique=False, nullable=False)
    f_home_team_code = db.Column(MATCH.FANTASY_HOME_TEAM_CODE, db.Integer, unique=False, nullable=False)
    f_away_team_code = db.Column(MATCH.FANTASY_AWAY_TEAM_CODE, db.Integer, unique=False, nullable=False)
    f_home_team_id = db.Column(MATCH.FANTASY_HOME_TEAM_ID, db.Integer, unique=False, nullable=False)
    f_away_team_id = db.Column(MATCH.FANTASY_AWAY_TEAM_ID, db.Integer, unique=False, nullable=False)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matches = db.relationship('Match', secondary=player_match_table, lazy='subquery',
                              backref=db.backref('player_teams', lazy=True))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    match_stats = db.relationship('MatchStats', backref='stats_player')
    week_stats = db.relationship('FantasyWeekStats', backref='week_stats_player', lazy=True)
    name = db.Column(db.String(200), unique=False, nullable=False)
    first_name = db.Column(db.String(80), unique=False, nullable=True)
    last_name = db.Column(db.String(80), unique=False, nullable=True)
    date_of_birth = db.Column(db.Date, unique=False, nullable=True)
    date_of_birth_epoch = db.Column(db.BigInteger, unique=False, nullable=True)
    country_of_birth = db.Column(db.String(80), unique=False, nullable=True)
    nationality = db.Column(db.String(80), unique=False, nullable=True)
    position = db.Column(db.String(80), unique=False, nullable=False)
    shirt_number = db.Column(db.Integer, unique=False, nullable=False)
    team = db.Column(db.String(80), unique=False, nullable=False)
    number_of_goals = db.Column(db.Integer, unique=False, nullable=False)
    weight = db.Column(db.Float, unique=False, nullable=True)
    gender = db.Column(db.String(20), unique=False, nullable=True)
    height = db.Column(db.Float, unique=False, nullable=True)
    team_fls_id = db.Column(db.Integer, unique=False, nullable=False)
    fd_api_id = db.Column(PLAYER.FOOTBALL_DATA_API_ID, db.Integer, unique=False, nullable=True)
    fls_api_id = db.Column(PLAYER.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=False, nullable=False)
    web_name = db.Column(PLAYER.FANTASY_WEB_NAME, db.String(80), unique=False, nullable=True)
    f_team_code = db.Column(PLAYER.FANTASY_TEAM_CODE, db.Integer, unique=False, nullable=True)
    f_id = db.Column(PLAYER.FANTASY_ID, db.Integer, unique=False, nullable=True)
    fantasy_status = db.Column(db.String(80), unique=False, nullable=True)
    fantasy_code = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_price = db.Column(db.Float, unique=False, nullable=True)
    fantasy_news = db.Column(db.String(200), unique=False, nullable=True)
    fantasy_news_timestamp = db.Column(db.TIMESTAMP, unique=False, nullable=True)
    photo_url = db.Column(db.String(200), unique=False, nullable=True)
    fantasy_team_id = db.Column(db.Integer, unique=False, nullable=True)


class MatchStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    occurred_timestamp = db.Column(db.TIMESTAMP, unique=False, nullable=True)
    goals_scored = db.Column(db.Integer, unique=False, nullable=True)
    goals_conceded = db.Column(db.Integer, unique=False, nullable=True)
    assists = db.Column(db.Integer, unique=False, nullable=True)
    own_goals = db.Column(db.Integer, unique=False, nullable=True)
    penalties_saved = db.Column(db.Integer, unique=False, nullable=True)
    penalties_missed = db.Column(db.Integer, unique=False, nullable=True)
    yellow_cards = db.Column(db.Integer, unique=False, nullable=True)
    red_cards = db.Column(db.Integer, unique=False, nullable=True)
    saves = db.Column(db.Integer, unique=False, nullable=True)
    bonus = db.Column(db.Integer, unique=False, nullable=True)
    bps = db.Column(db.Integer, unique=False, nullable=True)
    substitution = db.Column(db.Integer, unique=False, nullable=True)
    clean_sheet = db.Column(db.Boolean, unique=False, nullable=True)
    fantasy_influence = db.Column(db.Float, unique=False, nullable=True)
    fantasy_creativity = db.Column(db.Float, unique=False, nullable=True)
    fantasy_threat = db.Column(db.Float, unique=False, nullable=True)
    fantasy_ict_index = db.Column(db.Float, unique=False, nullable=True)
    open_play_crosses = db.Column(db.Integer, unique=False, nullable=True)
    big_chances_created = db.Column(db.Integer, unique=False, nullable=True)
    big_chances_missed = db.Column(db.Integer, unique=False, nullable=True)
    clearances_blocks_interceptions = db.Column(db.Integer, unique=False, nullable=True)
    recoveries = db.Column(db.Integer, unique=False, nullable=True)
    key_passes = db.Column(db.Integer, unique=False, nullable=True)
    tackles = db.Column(db.Integer, unique=False, nullable=True)
    winning_goals = db.Column(db.Integer, unique=False, nullable=True)
    attempted_passes = db.Column(db.Integer, unique=False, nullable=True)
    completed_passes = db.Column(db.Integer, unique=False, nullable=True)
    penalties_conceded = db.Column(db.Integer, unique=False, nullable=True)
    errors_leading_to_goal = db.Column(db.Integer, unique=False, nullable=True)
    errors_leading_to_goal_attempt = db.Column(db.Integer, unique=False, nullable=True)
    tackled = db.Column(db.Integer, unique=False, nullable=True)
    offside = db.Column(db.Integer, unique=False, nullable=True)
    target_missed = db.Column(db.Integer, unique=False, nullable=True)
    fouls = db.Column(db.Integer, unique=False, nullable=True)
    dribbles = db.Column(db.Integer, unique=False, nullable=True)
    played_at_home = db.Column(db.Boolean, unique=False, nullable=True)


class FantasyWeekStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_week = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_price = db.Column(db.Integer, unique=False, nullable=True)
    season_value = db.Column(db.Integer, unique=False, nullable=True)  # Fantasy value
    week_points = db.Column(db.Integer, unique=False, nullable=True)
    transfers_balance = db.Column(db.Integer, unique=False, nullable=True)
    selection_count = db.Column(db.Integer, unique=False, nullable=True)
    transfers_in = db.Column(db.Integer, unique=False, nullable=True)
    transfers_out = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_overall_price_rise = db.Column(db.Float, unique=False, nullable=True)
    fantasy_overall_price_fall = db.Column(db.Float, unique=False, nullable=True)
    fantasy_week_price_rise = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_week_price_fall = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_overall_transfers_in = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_overall_transfers_out = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_overall_points = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_point_average = db.Column(db.Float, unique=False, nullable=True)
    fantasy_total_bonus = db.Column(db.Float, unique=False, nullable=True)
    week_bonus = db.Column(db.Integer, unique=False, nullable=True)
    chance_of_playing_this_week = db.Column(db.Integer, unique=False, nullable=True)
    chance_of_playing_next_week = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_dream_team_member = db.Column(db.Boolean, unique=False, nullable=True)
    dream_team_count = db.Column(db.Integer, unique=False, nullable=True)
    selection_percentage = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_form = db.Column(db.Integer, unique=False, nullable=True)
    fantasy_special = db.Column(db.Boolean, unique=False, nullable=True)
    total_minutes_played = db.Column(db.Integer, unique=False, nullable=True)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competitions = db.relationship('Competition', secondary=comp_team_table, lazy='subquery',
                                   backref=db.backref('comp_teams', lazy=True))
    matches = db.relationship('Match', secondary=team_match_table, lazy='subquery',
                              backref=db.backref('match_teams', lazy=True))
    squad = db.relationship('Player', backref='player_team', lazy=True)
    fantasy_id = db.Column(db.Integer, unique=True, nullable=False)
    fd_id = db.Column(TEAM.FOOTBALL_DATA_ID, db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    country = db.Column(db.String(80), unique=False, nullable=False)
    short_name = db.Column(db.String(80), unique=False, nullable=False)
    acronym = db.Column(db.String(20), unique=False, nullable=False)
    crest_url = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String, unique=True, nullable=False)
    website = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    year_founded = db.Column(db.Integer, unique=False, nullable=False)
    club_colours = db.Column(db.String(40), unique=False, nullable=False)
    stadium = db.Column(db.String(120), unique=False, nullable=False)
    stadium_lat = db.Column(db.Float, unique=False, nullable=False)
    stadium_long = db.Column(db.Float, unique=False, nullable=False)
    stadium_capacity = db.Column(db.Integer, unique=False, nullable=False)
    fls_api_id = db.Column(TEAM.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=True, nullable=False)
    fantasy_code = db.Column(db.Integer, unique=True, nullable=False)
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
        db_comp = Competition(name=comp[COMP.NAME],
                              code=comp[COMP.CODE],
                              location=comp[COMP.LOCATION],
                              fd_api_id=comp[COMP.FOOTBALL_DATA_API_ID],
                              fls_api_id=comp[COMP.FASTEST_LIVE_SCORES_API_ID]
                              )
        standings = driver.request_standings(competition_id=comp[COMP.FOOTBALL_DATA_API_ID])
        if standings:
            for stan in standings['standings']:
                db_standing = Standings(type=stan[STANDINGS.TYPE],
                                        season=stan[STANDINGS.SEASON],
                                        match_day=stan[STANDINGS.MATCH_DAY])
                for entry in stan[STANDINGS.TABLE]:
                    se = StandingsEntry(
                        position=entry[STANDINGS.POSITION],
                        team_name=entry[STANDINGS.TEAM_NAME],
                        fd_team_id=entry[STANDINGS.FOOTBALL_DATA_TEAM_ID],
                        games_played=entry[STANDINGS.GAMES_PLAYED],
                        games_won=entry[STANDINGS.GAMES_WON],
                        games_drawn=entry[STANDINGS.GAMES_DRAWN],
                        games_lost=entry[STANDINGS.GAMES_LOST],
                        points=entry[STANDINGS.POINTS],
                        goals_for=entry[STANDINGS.GOALS_FOR],
                        goals_against=entry[STANDINGS.GOALS_AGAINST],
                        goals_difference=entry[STANDINGS.GOAL_DIFFERENCE]
                    )
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
        team_players = driver.request_player_details(team_name=team[TEAM.NAME],
                                                     team_fls_id=team[TEAM.FASTEST_LIVE_SCORES_API_ID])
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
    # teams = db.session\
    #     .query(func.max(StandingsEntry.points),
    #            StandingsEntry.team_name, StandingsEntry.team).filter_by(standings_id=8).group_by(StandingsEntry.team_name).all()
    # teams = driver.request_teams(fd_comp_id=2021, fls_comp_id=2, season=2018)  # PREMIER LEAGUE
    # for team in teams:
    #     ingest_players(team_fls_id=team[TEAM.FASTEST_LIVE_SCORES_API_ID])
    # db.session.commit()
    # competitions = Competition.query.all()
    ingest_competitions()

    # ingest_teams(fls_comp_id=2, fd_comp_id=2021, season=2018)















