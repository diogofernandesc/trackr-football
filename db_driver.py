from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from ingest_engine.cons import Competition as COMP, \
    Standings as STANDINGS, Team as TEAM, Match as MATCH, Player as PLAYER


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
db = SQLAlchemy(app)


class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    code = db.Column(db.String(20), unique=False, nullable=True)
    location = db.Column(db.String(80), unique=False, nullable=False)
    fd_api_id = db.Column(COMP.FOOTBALL_DATA_API_ID, db.Integer, unique=True, nullable=False)
    fls_api_id = db.Column(COMP.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=True, nullable=False)


class Standings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), unique=False, nullable=False)
    season = db.Column(db.String(20), unique=False, nullable=False)
    match_day = db.Column(db.Integer, unique=False, nullable=False)


class StandingsEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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


class MatchStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, unique=False, nullable=False)
    player_id = db.Column(db.Integer, unique=False, nullable=False)
    minutes_passed = db.Column(db.Integer, unique=False, nullable=True)
    occurred_timestamp = db.Column(db.TIMESTAMP, unique=False, nullable=True)
    goals_scored = db.Column(db.Integer, unique=False, nullable=True)
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


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fantasy_id = db.Column(db.Integer, unique=True, nullable=False)
    fd_id = db.Column(TEAM.FOOTBALL_DATA_ID, db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    country = db.Column(db.String(80), unique=False, nullable=False)
    short_name = db.Column(db.String(80), unique=False, nullable=False)
    acronym = db.Column(db.String(20), unique=False, nullable=False)
    crest_url = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
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


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    date_of_birth = db.Column(db.Date, unique=False, nullable=False)
    date_of_birth_epoch = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    country_of_birth = db.Column(db.String(80), unique=False, nullable=False)
    nationality = db.Column(db.String(80), unique=False, nullable=False)
    position = db.Column(db.String(80), unique=False, nullable=False)
    shirt_number = db.Column(db.Integer, unique=False, nullable=False)
    team = db.Column(db.String(80), unique=False, nullable=False)
    number_of_goals = db.Column(db.Integer, unique=False, nullable=False)
    weight = db.Column(db.Float, unique=False, nullable=False)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    height = db.Column(db.Float, unique=False, nullable=False)
    team_fls_id = db.Column(db.Integer, unique=False, nullable=False)
    fd_api_id = db.Column(PLAYER.FOOTBALL_DATA_API_ID, db.Integer, unique=False, nullable=False)
    fls_api_id = db.Column(PLAYER.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=False, nullable=False)
    web_name = db.Column(PLAYER.FANTASY_WEB_NAME, db.String(80), unique=False, nullable=False)
    f_team_code = db.Column(PLAYER.FANTASY_TEAM_CODE, db.Integer, unique=False, nullable=False)
    f_id = db.Column(PLAYER.FANTASY_ID, db.Integer, unique=False, nullable=False)
    fantasy_status = db.Column(db.String(80), unique=False, nullable=False)
    fantasy_code = db.Column(db.Integer, unique=False, nullable=False)
    fantasy_price = db.Column(db.Float, unique=False, nullable=False)
    fantasy_news = db.Column(db.String(200), unique=False, nullable=False)
    fantasy_news_timestamp = db.Column(db.TIMESTAMP, unique=False, nullable=False)
    photo_url = db.Column(db.String(200), unique=False, nullable=False)
    fantasy_team_id = db.Column(db.Integer, unique=False, nullable=False)


class PlayerWeekInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)


    """
    # Separate # TODO: chance of playing this week and next
    # week fields
    # dream_team_member
    # fantasy_week_value
    ...
    """

    fantasy_overall_price_rise = db.Column(db.Float, unique=False, nullable=False)
    fantasy_overall_price_fall = db.Column(db.Float, unique=False, nullable=False)
    fantasy_overall_transfers_in = db.Column(db.Integer, unique=False, nullable=False)
    fantasy_overall_transfers_out = db.Column(db.Integer, unique=False, nullable=False)
    fantasy_overall_points = db.Column(db.Integer, unique=False, nullable=False)
    fantasy_point_average = db.Column(db.Float, unique=False, nullable=False)
    minutes_played = db.Column(db.Integer, unique=False, nullable=False)
    clean_sheets = db.Column(db.Integer, unique=False, nullable=False)
    fantasy_total_bonus = db.Column(db.Float, unique=False, nullable=False)
    fantasy_influence = db.Column(db.Float, unique=False, nullable=False)
    fantasy_creativity = db.Column(db.Float, unique=False, nullable=False)
    fantasy_threat = db.Column(db.Float, unique=False, nullable=False)
    fantasy_ict_index = db.Column(db.Float, unique=False, nullable=False)



# db.create_all()














