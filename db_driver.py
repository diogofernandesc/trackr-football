from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from ingest_engine.cons import Competition as COMP, \
    Standings as STANDINGS, Team as TEAM, Match as MATCH


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
db = SQLAlchemy(app)


class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    code = db.column(db.String(20), unique=False, nullable=True)
    location = db.column(db.String(80), unique=False, nullable=False)
    fd_api_id = db.column(COMP.FOOTBALL_DATA_API_ID, db.Integer, unique=True, nullable=False)
    fls_api_id = db.column(COMP.FASTEST_LIVE_SCORES_API_ID, db.Integer, unique=True, nullable=False)


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
    fd_id = db.Column(MATCH.FOOTBALL_DATA_ID, unique=True, nullable=False)
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
    # referee_group # TODO foreign key
    fls_match_id = db.Column(MATCH.FLS_MATCH_ID, unique=True, nullable=False)
    fls_competition_id = db.Column(MATCH.FLS_API_COMPETITION_ID, unique=False, nullable=False)
    competition = db.Column(MATCH.COMPETITION, unique=False, nullable=False)
    # events # TODO foreign key
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
    home_form = db.Column(db.ARRAY, unique=False, nullable=False)
    away_form = db.Column(db.ARRAY, unique=False, nullable=False)
    h_fls_id = db.Column(MATCH.HOME_TEAM_FLS_ID, db.Integer, unique=False, nullable=False)
    a_fls_id = db.Column(MATCH.AWAY_TEAM_FLS_ID, db.Integer, unique=False, nullable=False)
    # previous encounters TODO foreign key and table
    psc = db.Column(MATCH.PENALTY_SHOOTOUT_SCORE, db.String, unique=False, nullable=False)
    finished = db.Column(db.Boolean, unique=False, nullable=False)
    fantasy_game_week = db.Col















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
    phone = db.Column(db.Integer(80), unique=True, nullable=False)
    website = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    year_founded = db.Column(db.Integer, unique=False, nullable=False)
    club_colours = db.Column(db.String(40), unique=False, nullable=False)
    stadium = db.Column(db.String(120), unique=False, nullable=False)
    stadium_lat = db.Column(db.Float, unique=False, nullable=False)
    stadium_long = db.Column(db.Float, unique=False, nullable=False)
    stadium_capacity = db.Column(db.Integer, unique=False, nullable=False)
    fls_api_id = db.Column(TEAM.FASTEST_LIVE_SCORES_API_ID, unique=True, nullable=False)
    fantasy_code = db.Column(db.Integer, unique=True, nullable=False)
    home_strength = db.Column(TEAM.FANTASY_OVERALL_HOME_STRENGTH, db.Integer, unique=False, nullable=False)
    away_strength = db.Column(TEAM.FANTASY_OVERALL_AWAY_STRENGTH, db.Integer, unique=False, nullable=False)
    attack_home_strength = db.Column(TEAM.FANTASY_ATTACK_HOME_STRENGTH, db.Integer, unique=False, nullable=False)
    attack_away_strength = db.Column(TEAM.FANTASY_ATTACK_AWAY_STRENGTH, db.Integer, unique=False, nullable=False)
    defense_home_strength = db.Column(TEAM.FANTASY_DEFENCE_HOME_STRENGTH, db.Integer, unique=False, nullable=False)
    defense_away_strength = db.Column(TEAM.FANTASY_DEFENCE_AWAY_STRENGTH, db.Integer, unique=False, nullable=False)

    ID = 'id'
    FOOTBALL_DATA_ID = 'football_data_id'
    SEASON_FOOTBALL_DATA_ID = 'season_football_data_id'
    SEASON_START_DATE = 'season_start_date'
    SEASON_END_DATE = 'season_end_date'
    SEASON_YEAR = 'season_year'
    MATCH_UTC_DATE = 'utc_date'
    START_TIME_EPOCH = 'start_time_epoch'
    START_TIME = 'start_time'
    STATUS = 'status'
    MATCHDAY = 'matchday'
    FULL_TIME_HOME_SCORE = 'full_time_home_score'
    FULL_TIME_AWAY_SCORE = 'full_time_away_score'
    HALF_TIME_HOME_SCORE = 'half_time_home_score'
    HALF_TIME_AWAY_SCORE = 'half_time_away_score'
    EXTRA_TIME_HOME_SCORE = 'extra_time_home_score'
    EXTRA_TIME_AWAY_SCORE = 'extra_time_away_score'
    PENALTY_HOME_SCORE = 'penalty_home_score'
    PENALTY_AWAY_SCORE = 'penalty_away_score'
    WINNER = 'winner'
    HOME_TEAM = 'home_team'
    AWAY_TEAM = 'away_team'
    REFEREES = 'referees'
    FILTERS = 'filters'
    FLS_MATCH_ID = 'fls_match_id'
    FLS_API_COMPETITION_ID = 'fls_competition_id'
    COMPETITION = 'competition'
    EVENTS = 'events'
    HOME_SCORE_PROBABILITY = 'home_score_probability'
    HOME_CONCEDE_PROBABILITY = 'home_concede_probability'
    AWAY_SCORE_PROBABILITY = 'away_score_probability'
    AWAY_CONCEDE_PROBABILITY = 'away_concede_probability'
    HOME_SCORE_PROBABILITY_OVER_1_5 = 'home_score_probability_over_1_5'  # THESE STATS ARE BASED ON THE LAST 5 GAMES
    HOME_SCORE_PROBABILITY_OVER_2_5 = 'home_score_probability_over_2_5'
    HOME_SCORE_PROBABILITY_OVER_3_5 = 'home_score_probability_over_3_5'
    HOME_SCORE_PROBABILITY_UNDER_1_5 = 'home_score_probability_under_1_5'
    HOME_SCORE_PROBABILITY_UNDER_2_5 = 'home_score_probability_under_2_5'
    HOME_SCORE_PROBABILITY_UNDER_3_5 = 'home_score_probability_under_3_5'
    AWAY_SCORE_PROBABILITY_OVER_1_5 = 'away_score_probability_over_1_5'
    AWAY_SCORE_PROBABILITY_OVER_2_5 = 'away_score_probability_over_2_5'
    AWAY_SCORE_PROBABILITY_OVER_3_5 = 'away_score_probability_over_3_5'
    AWAY_SCORE_PROBABILITY_UNDER_1_5 = 'away_score_probability_under_1_5'
    AWAY_SCORE_PROBABILITY_UNDER_2_5 = 'away_score_probability_under_2_5'
    AWAY_SCORE_PROBABILITY_UNDER_3_5 = 'away_score_probability_under_3_5'
    HOME_FORM = 'home_form'
    AWAY_FORM = 'away_form'
    HOME_TEAM_FLS_ID = 'home_team_fls_id'
    AWAY_TEAM_FLS_ID = 'away_team_fls_id'
    PREVIOUS_ENCOUNTERS = 'previous_encounters'
    PENALTY_SHOOTOUT_SCORE = 'penalty_shootout_score'
    FINISHED = 'finished'
    FANTASY_GAME_WEEK = 'fantasy_game_week'
    FANTASY_GAME_WEEK_ID = 'fantasy_game_week_id'
    GOALS_SCORED = 'goals_scored'
    ASSISTS = 'assists'
    OWN_GOALS = 'own_goals'
    PENALTIES_SAVED = 'penalties_saved'
    PENALTIES_MISSED = 'penalties_missed'
    YELLOW_CARDS = 'yellow_cards'
    RED_CARDS = 'red_cards'
    SAVES = 'saves'
    BONUS = 'bonus'
    BPS = 'bps'
    FANTASY_HOME_TEAM_DIFFICULTY = 'fantasy_home_team_difficulty'
    FANTASY_AWAY_TEAM_DIFFICULTY = 'fantasy_away_team_difficulty'
    FANTASY_MATCH_CODE = 'fantasy_match_code'
    MINUTES = 'minutes'
    FANTASY_HOME_TEAM_CODE = 'fantasy_home_team_code'
    FANTASY_AWAY_TEAM_CODE = 'fantasy_away_team_code'
    FANTASY_HOME_TEAM_ID = 'fantasy_home_team_id'
    FANTASY_AWAY_TEAM_ID = 'fantasy_away_team_id'
    SIDE = 'side'
    GOAL_AMOUNT = 'amount'