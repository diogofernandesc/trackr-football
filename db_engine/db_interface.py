from typing import Union
import logging
import unidecode as unidecode
from sqlalchemy import or_, func
from db_engine.db_driver import Competition, Team, Standings, StandingsEntry, Match, Player, MatchStats, FantasyWeekStats
from ingest_engine.cons import IGNORE, Team as TEAM, Standings as STANDINGS, Competition as COMPETITION, Match as MATCH,\
    Player as PLAYER, MatchEvent as MATCH_EVENT

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def col_exists(table, col):
    """
    Check if column exists inside table
    :param table: SQLAlchemy table to check existence
    :param col: SQLAlchemy col to check existence
    :return: Whether or not :param col exists in :param table
    :rtype: bool
    """
    table = table.__table__
    table_cols = table._columns

    for t_col in table_cols:
        exists = col == t_col.key
        if exists:
            return exists

    return False


def filter_parse(query_str, table, column):
    """
    Parse individual filter into an SQLAlchemy query statement
    :param query_str: API URL query string
    :param table: SQL Table to query from
    :param column: SQL table column to query from
    :param val: filtering value
    :return: SQLAlchemy filter
    """

    if isinstance(query_str, str):
        if any(x in query_str for x in ["$lt", "$gt", "$lte", "$gte"]):
            [op, val] = query_str.split(":")
            if op == "$lt":
                return table.c[column] < val

            elif op == "$gt":
                return table.c[column] > val

            elif op == "$lte":
                return table.c[column] <= val

            elif op == "$gte":
                return table.c[column] >= val
    return table.c[column] == query_str


def to_json(result_map, aggregator_name, limit=10):
    list_dict_result = []
    if result_map:
        for k, v in result_map.items():
            dict_result = k.__dict__
            dict_result.pop(IGNORE.INSTANCE_STATE, None)
            dict_result[aggregator_name] = clean_output(v, as_list=True)
            list_dict_result.append(dict_result)

    if len(list_dict_result) == 1:
        return list_dict_result[0]

    else:
        return list_dict_result[:limit]


def clean_output(query_res, as_list=False, limit=10):
    """
    Ensure only the right fields come out following a DB query
    :param query_res: the query result to be clean
    :param as_list: format output to output as list even when result is solely one entity e.g. for a standings table
    :param limit:
    :return:
    """
    result = []
    for res in query_res:
        final_res = res.__dict__
        if IGNORE.INSTANCE_STATE in final_res:
            final_res.pop(IGNORE.INSTANCE_STATE, None)

        result.append(final_res)

    if not as_list and len(result) == 1:
        return result[0]

    return result[:limit]


class DBInterface(object):

    def __init__(self, db):
        self.db = db

    def update_names(self):
        """
        Remove characters from player names
        :return: Rows updated without characters
        """
        for player in self.db.session.query(Player).all():
            if player.name:
                player.name = unidecode.unidecode(player.name)
            if player.first_name:
                player.first_name = unidecode.unidecode(player.first_name)

            if player.last_name:
                player.last_name = unidecode.unidecode(player.last_name)

            self.db.session.commit()

    def get_last_game_week(self, filters) -> int:
        """
        Get the latest game week
        :return: int indicator
        """
        base_standings_filters = []
        bs_query = self.db.session.query(func.max(Standings.match_day))

        if isinstance(filters, list):
            active_filters = filters
        else:
            active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:
                base_standings_filters.append(Standings.__table__.c[filter_[0]] == filter_val)

        return bs_query.filter(*base_standings_filters).scalar()

    def get_competition(self, limit: int= 1, multi=False, filters=None):
        """
        Query DB for competition record
        :param limit: Number of competitions to retrieve
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param filters: namedtuple with all available filter fields
        :return:  matched (if any) competition records
        """
        db_filters = []
        comp_query = self.db.session.query(Competition)
        active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:

                # Applied different filtering method when it's a team name e.g. SQL LIKE search
                if filter_[0] in [COMPETITION.NAME, COMPETITION.LOCATION]:
                    db_filters.append(Competition.__table__.c[filter_[0]].ilike(f"%{filter_val}%"))

                else:
                    db_filters.append(Competition.__table__.c[filter_[0]] == filter_val)

        if multi:
            query_result = comp_query.filter(or_(*db_filters))
        else:
            query_result = comp_query.filter(*db_filters)

        return clean_output(query_result, limit=limit)

    def get_team(self, limit: int=10,  multi=False, filters=None):
        """
        Query DB for team record
        :param limit: Optional limit for number of teams to retrieve
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param filters: namedtuple with all available filter fields
        :return: matched (if any) team records
        """

        db_filters = []
        team_query = self.db.session.query(Team)
        active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:

                # Applied different filtering method when it's a team name e.g. SQL LIKE search
                if filter_[0] == TEAM.NAME:
                    db_filters.append(Team.name.ilike(f"%{filter_val}%"))

                else:
                    db_filters.append(filter_parse(query_str=filter_val, table=Team.__table__, column=filter_[0]))

        if multi:
            query_result = team_query.filter(or_(*db_filters))
        else:
            query_result = team_query.filter(*db_filters)

        return clean_output(query_result, limit=limit)

    def insert_team(self, record: Union[list, dict]):
        """
        Insert team record into DB
        :return:
        """
        if isinstance(record, dict):
            record = [record]

        for team in record:
            for player in team.get(TEAM.SQUAD):
                player[PLAYER.TEAM] = team[TEAM.NAME]
                player[PLAYER.TEAM_FD_ID] = team[TEAM.FOOTBALL_DATA_ID]
                self.insert_basic_player(fd_id=player[PLAYER.FOOTBALL_DATA_API_ID], record=player)
            team.pop(TEAM.ACTIVE_COMPETITIONS)  # for now ignore
            team.pop(TEAM.SQUAD)
            team_query = self.db.session.query(Team).filter(Team.fantasy_id == team.get(TEAM.FANTASY_ID))
            if not team_query.count():
                self.db.session.add(Team(**team))

        self.db.session.commit()

    def get_player(self, limit: int = 10,  multi=False, filters=None):
        """
        Query DB for player record
        :param limit: Optional limit for number of teams to retrieve
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param filters: namedtuple with all available filter fields
        :return: matched (if any) team records
        """

        db_filters = []
        player_query = self.db.session\
            .query(Player, FantasyWeekStats)\
            .outerjoin(FantasyWeekStats, Player.id == FantasyWeekStats.player_id)

        active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:

                if filter_[0] in [PLAYER.NAME, PLAYER.TEAM, PLAYER.COUNTRY_OF_BIRTH, PLAYER.NATIONALITY]:
                    db_filters.append(Player.name.ilike(f"%{filter_val}%"))

                else:
                    active_table = Player.__table__
                    if col_exists(table=Player, col=filter_[0]):
                        active_table = Player.__table__

                    elif col_exists(table=FantasyWeekStats, col=filter_[0]):
                        active_table = FantasyWeekStats.__table__

                    db_filters.append(filter_parse(query_str=filter_val, table=active_table, column=filter_[0]))

        if multi:
            query_result = player_query.filter(or_(*db_filters)).all()
        else:
            query_result = player_query.filter(*db_filters).all()

        player_week_stat_map = {}
        for player, week_stat in query_result:
            if player not in player_week_stat_map:
                player_week_stat_map[player] = []

            if week_stat:
                player_week_stat_map[player].append(week_stat)

        result = to_json(player_week_stat_map, aggregator_name=PLAYER.WEEK_STATS, limit=limit)
        return result

    def insert_player(self, record: Union[list, dict]):
        """
        Insert player record into DB
        :return:
        """
        if isinstance(record, dict):
            record = [record]

        for player in record:
            fantasy_week_stats = None
            fantasy_stats = None
            player_query = self.db.session.query(Player).filter(Player.name.ilike(player[PLAYER.NAME]))
            if not player_query.count():
                player_query = self.db.session.query(Player).filter(Player.name.ilike(player[PLAYER.FANTASY_WEB_NAME]))

            if not player_query.count():
                player_query = self.db.session.query(Player)\
                    .filter(Player.name.ilike(f"{player[PLAYER.FANTASY_WEB_NAME]} {player[PLAYER.LAST_NAME]}"))

            if not player_query.count():  # Try to match with just first and last name
                player_query = self.db.session\
                    .query(Player) \
                    .filter(Player.name.ilike(
                     f"{player[PLAYER.FIRST_NAME].split(' ')[0]} {player[PLAYER.LAST_NAME].split(' ')[-1]}"))

            if not player_query.count():  # Try to match with (first) first name and (first) last name
                player_query = self.db.session\
                    .query(Player) \
                    .filter(Player.name.ilike(
                     f"{player[PLAYER.FIRST_NAME].split(' ')[0]} {player[PLAYER.LAST_NAME].split(' ')[0]}"))

            if not player_query.count():  # Try to match with (last) first name and (first) last name
                player_query = self.db.session \
                    .query(Player) \
                    .filter(Player.name.ilike(
                    f"{player[PLAYER.FIRST_NAME].split(' ')[-1]} {player[PLAYER.LAST_NAME].split(' ')[0]}"))

            if not player_query.count():  # Try to match with just web_name and (last) last name
                player_query = self.db.session\
                    .query(Player) \
                    .filter(Player.name.ilike(
                     f"{player[PLAYER.FANTASY_WEB_NAME]} {player[PLAYER.LAST_NAME].split(' ')[-1]}"))

            if not player_query.count():  # Try to match with first_name and (first) last name
                player_query = self.db.session\
                    .query(Player) \
                    .filter(Player.name.ilike(
                     f"{player[PLAYER.FIRST_NAME]} {player[PLAYER.LAST_NAME].split(' ')[0]}"))

            if not player_query.count():  # Try to match with just web_name and (first) last name
                player_query = self.db.session\
                    .query(Player) \
                    .filter(Player.name.ilike(
                     f"{player[PLAYER.FANTASY_WEB_NAME]} {player[PLAYER.LAST_NAME].split(' ')[0]}"))

            if player_query.count():
                player_record = player_query.first()
                player_record.fantasy_id = player.get(PLAYER.FANTASY_ID, None)
                player_record.fantasy_code = player.get(PLAYER.FANTASY_CODE, None)
                player_record.fantasy_team_code = player.get(PLAYER.FANTASY_TEAM_CODE, None)
                player_record.fantasy_team_id = player.get(PLAYER.FANTASY_TEAM_ID, None)
                player_record.first_name = player.get(PLAYER.FIRST_NAME, None)
                player_record.last_name = player.get(PLAYER.LAST_NAME, None)
                player_record.number_of_goals = player.get(PLAYER.NUMBER_OF_GOALS, None)
                player_record.fantasy_news = player.get(PLAYER.FANTASY_NEWS, None)
                player_record.fantasy_news_timestamp = player.get(PLAYER.FANTASY_NEWS_TIMESTAMP, None)
                player_record.photo_url = player.get(PLAYER.FANTASY_PHOTO_URL, None)
                player_record.fantasy_overall_price_rise = player.get(PLAYER.FANTASY_OVERALL_PRICE_RISE, None)
                player_record.fantasy_overall_price_fall = player.get(PLAYER.FANTASY_OVERALL_PRICE_FALL, None)
                player_record.fantasy_week_price_rise = player.get(PLAYER.FANTASY_WEEK_PRICE_RISE, None)
                player_record.fantasy_week_price_fall = player.get(PLAYER.FANTASY_WEEK_PRICE_FALL, None)
                player_record.fantasy_overall_transfers_in = player.get(PLAYER.FANTASY_OVERALL_TRANSFERS_IN, None)
                player_record.fantasy_overall_transfers_out = player.get(PLAYER.FANTASY_OVERALL_TRANSFERS_OUT, None)
                player_record.fantasy_overall_points = player.get(PLAYER.FANTASY_OVERALL_POINTS, None)
                player_record.fantasy_point_average = player.get(PLAYER.FANTASY_POINT_AVERAGE, None)
                player_record.fantasy_total_bonus = player.get(PLAYER.FANTASY_TOTAL_BONUS, None)
                player_record.fantasy_price = player.get(PLAYER.FANTASY_PRICE, None)
                player_record.chance_of_playing_this_week = player.get(PLAYER.FANTASY_CHANCE_OF_PLAYING_THIS_WEEK, None)
                player_record.chance_of_playing_next_week = player.get(PLAYER.FANTASY_CHANCE_OF_PLAYING_NEXT_WEEK, None)
                player_record.fantasy_dream_team_member = player.get(PLAYER.FANTASY_DREAM_TEAM_MEMBER, None)
                player_record.fantasy_dream_team_count = player.get(PLAYER.FANTASY_DREAM_TEAM_COUNT, None)
                player_record.fantasy_selection_percentage = player.get(PLAYER.FANTASY_SELECTION_PERCENTAGE, None)
                player_record.fantasy_form = player.get(PLAYER.FANTASY_FORM, None)
                player_record.fantasy_special = player.get(PLAYER.FANTASY_SPECIAL, None)
                player_record.bps = player.get(PLAYER.FANTASY_TOTAL_BONUS, None)

                for match in player.get(PLAYER.SEASON_MATCH_HISTORY, []):
                    match_stat_query = self.db.session.query(MatchStats).\
                        filter(MatchStats.player_id == player_record.id).\
                        filter(MatchStats.fantasy_match_id == match[MATCH.FANTASY_MATCH_ID])

                    if not match_stat_query.count():
                        fantasy_stats = MatchStats()
                        fantasy_stats.fantasy_match_id = match[MATCH.FANTASY_MATCH_ID]
                        fantasy_stats.goals_scored = match[PLAYER.NUMBER_OF_GOALS]
                        fantasy_stats.goals_conceded = match[PLAYER.GOALS_CONCEDED]
                        fantasy_stats.assists = match[PLAYER.ASSISTS]
                        fantasy_stats.own_goals = match[PLAYER.OWN_GOALS]
                        fantasy_stats.penalties_saved = match[PLAYER.PENALTIES_SAVED]
                        fantasy_stats.penalties_missed = match[PLAYER.PENALTIES_MISSED]
                        fantasy_stats.yellow_cards = match[PLAYER.YELLOW_CARDS]
                        fantasy_stats.red_cards = match[PLAYER.RED_CARDS]
                        fantasy_stats.saves = match[PLAYER.SAVES]
                        fantasy_stats.clean_sheet = match[MATCH_EVENT.CLEAN_SHEET]
                        fantasy_stats.fantasy_influence = match[PLAYER.FANTASY_INFLUENCE]
                        fantasy_stats.fantasy_creativity = match[PLAYER.FANTASY_CREATIVITY]
                        fantasy_stats.fantasy_threat = match[PLAYER.FANTASY_THREAT]
                        fantasy_stats.fantasy_ict_index = match[PLAYER.FANTASY_ICT_INDEX]
                        fantasy_stats.played_at_home = match[PLAYER.PLAYED_AT_HOME]
                        fantasy_stats.minutes_played = match[PLAYER.MINUTES_PLAYED]

                    week_stat_query = self.db.session.query(FantasyWeekStats). \
                        filter(FantasyWeekStats.player_id == player_record.id). \
                        filter(FantasyWeekStats.game_week == match[MATCH.FANTASY_GAME_WEEK])

                    if not week_stat_query.count():
                        fantasy_week_stats = FantasyWeekStats()
                        fantasy_week_stats.game_week = match[MATCH.FANTASY_GAME_WEEK]
                        fantasy_week_stats.season_value = match[PLAYER.FANTASY_SEASON_VALUE]
                        fantasy_week_stats.fantasy_week_points = match[PLAYER.FANTASY_WEEK_POINTS]
                        fantasy_week_stats.fantasy_transfers_balance = match[PLAYER.FANTASY_TRANSFERS_BALANCE]
                        fantasy_week_stats.fantasy_selection_count = match[PLAYER.FANTASY_SELECTION_COUNT]
                        fantasy_week_stats.fantasy_week_transfers_in = match[PLAYER.FANTASY_WEEK_TRANSFERS_IN]
                        fantasy_week_stats.fantasy_week_transfers_out = match[PLAYER.FANTASY_WEEK_TRANSFERS_OUT]
                        fantasy_week_stats.fantasy_week_bonus = match[PLAYER.FANTASY_WEEK_BONUS]

                    if not match_stat_query.count() and fantasy_stats:
                        player_record.match_stats.append(fantasy_stats)
                    if not week_stat_query.count() and fantasy_week_stats:
                        player_record.week_stats.append(fantasy_week_stats)

                    match_query = self.db.session.query(Match) \
                        .filter(Match.fantasy_match_id == match[MATCH.FANTASY_MATCH_ID])

                    if match_query.count() and fantasy_stats and match_stat_query.count():
                        match_record = match_query.first()
                        match_record.stats.append(fantasy_stats)

                self.db.session.commit()

    def get_standings(self, limit=10, multi=False, filters=None):
        """
        Query DB for standings records
        :param limit: Due to how heavy standings are, default amount of standings to 10, unless otherwise changed
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param filters: namedtuple with all available filter fields
        :return: matched (if any) standings records
        """
        db_filters = []
        stan_query = self.db.session\
            .query(Standings, StandingsEntry)\
            .join(StandingsEntry, Standings.id == StandingsEntry.standings_id)

        active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:

                # Applied different filtering method when it's a team name e.g. SQL LIKE search
                if filter_[0] == STANDINGS.TEAM_NAME:
                    db_filters.append(StandingsEntry.team_name.ilike(f"%{filter_val}%"))

                else:
                    active_table = Standings.__table__
                    if col_exists(table=Standings, col=filter_[0]) and filter_[0] != STANDINGS.ID:
                        active_table = Standings.__table__

                    elif col_exists(table=StandingsEntry, col=filter_[0]):
                        active_table = StandingsEntry.__table__

                    column = filter_[0]
                    if filter_[0] == STANDINGS.ID:  # Ensure that standings_id column is used when querying DB
                        column = STANDINGS.STANDINGS_ID

                    db_filters.append(filter_parse(query_str=filter_val, table=active_table, column=column))

        comp_filter = db_filters[0]
        db_filters = db_filters[1:]

        if multi:
            stan_query = stan_query.filter(comp_filter).filter(or_(*db_filters)).limit(100).all()
        else:
            stan_query = stan_query.filter(*db_filters).limit(100).all()  # no standings will have more than 100 entries
        standings_map = {}

        # Reformatting dict to get standings in list per comp as "standing_entries" field
        for tpl in stan_query:
            if tpl[0] not in standings_map:
                standings_map[tpl[0]] = [tpl[1]]

            else:
                standings_map[tpl[0]].append(tpl[1])

        result = to_json(standings_map, aggregator_name='table', limit=limit)
        return result

    def update_standings(self, match_day, record):
        """
        Update standings for the given match_day
        :param match_day: match_day for standings
        :return: DB record updated
        """
        comp_query = self.db.session.query(Competition).filter(Competition.fd_api_id == 2021)
        comp = comp_query.first()

        stan_query = self.db.session.query(Standings)\
            .filter(Standings.match_day == match_day)\
            .filter(Standings.competition_id == comp.id)

        if not stan_query.count():
            for stan in record['standings']:
                table = stan.pop(STANDINGS.TABLE, [])
                db_standing = Standings(**stan)

                for entry in table:
                    se = StandingsEntry(**entry)
                    db_standing.standings_entries.append(se)

                comp.standings.append(db_standing)

            self.db.session.add(comp)
            self.db.session.commit()

            return True

        return False

    def get_match(self, limit: int = 10, multi: bool = False, filters=None) -> dict:
        """
        Query DB for match record
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param filters: namedtuple with all available filter fields
        :param limit: Result set size
        :return: matched (if any) match records
        """
        db_filters = []
        match_query = self.db.session.query(Match)
        active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:

                if any(filter_name in filter_[0] for filter_name in [MATCH.HOME_TEAM,
                                                                     MATCH.AWAY_TEAM,
                                                                     MATCH.COMPETITION,
                                                                     ]):
                    db_filters.append(Match.__table__.c[filter_[0]].ilike(f"%{filter_val}%"))

                else:
                    db_filters.append(filter_parse(query_str=filter_val, table=Match.__table__, column=filter_[0]))

        if multi:
            query_result = match_query.filter(or_(*db_filters))

        else:
            query_result = match_query.filter(*db_filters)

        return clean_output(query_result, limit=limit)

    def insert_match(self, record: Union[list, dict]):
        """
        Insert record into DB
        :return:
        """
        if isinstance(record, dict):
            record = [record]

        for match in record:
            match_query = self.db.session.query(Match).filter(Match.match_fd_id == match[MATCH.FOOTBALL_DATA_ID])
            if not match_query.count():
                match.pop(MATCH.GOALS_SCORED, None)
                match.pop(MATCH.EVENTS, None)
                match.pop(MATCH.ASSISTS, None)
                match.pop(MATCH.OWN_GOALS, None)
                match.pop(MATCH.BPS, None)
                match.pop(MATCH.BONUS, None)
                match.pop(MATCH.BPS, None)
                match.pop(MATCH.PENALTIES_SAVED, None)
                match.pop(MATCH.PENALTIES_MISSED, None)
                match.pop(MATCH.YELLOW_CARDS, None)
                match.pop(MATCH.RED_CARDS, None)
                match.pop(MATCH.SAVES, None)
                match.pop(MATCH.PREVIOUS_ENCOUNTERS, None)
                self.db.session.add(Match(**match))

        self.db.session.commit()

    def get_stats(self, limit: int = 10, multi: bool = False, filters=None) -> dict:
        """
        Query DB for stats record
        :param filters: namedtuple with all available filter fields
        :param multi: Whether to perform OR querying on filters
        :param limit: Result set size
        :return: matched (if any) match stats records
        """
        db_filters = []
        stat_query = self.db.session.query(MatchStats)
        active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:
                db_filters.append(filter_parse(query_str=filter_val, table=MatchStats.__table__, column=filter_[0]))

        if multi:
            query_result = stat_query.filter(or_(*db_filters))

        else:
            query_result = stat_query.filter(*db_filters)

        return clean_output(query_result, limit=limit)

    def insert_basic_player(self, fd_id, record: Union[list, dict]):
        """
        Inserts basic player record
        :param fd_id: Column used to check if record already exists
        :param record: Record to insert
        :return:
        """
        player_query = self.db.session.query(Player).filter(Player.fd_id == fd_id)
        if not player_query.count():  # If player exists
            record.pop(TEAM.SQUAD_ROLE)
            self.db.session.add(Player(**record))

        self.db.session.commit()

# if __name__ == "__main__":
#     db = DBInterface()
#     db.update_names()









