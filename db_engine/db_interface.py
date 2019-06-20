from typing import Union

from sqlalchemy import or_, func
from collections import namedtuple
from db_engine.db_driver import Competition, Team, Standings, StandingsEntry, Match, db
from ingest_engine.cons import IGNORE, Team as TEAM, Standings as STANDINGS, Competition as COMPETITION, Match as MATCH

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
            val = query_str.split(":")[1]
            if "$lt" in query_str:
                return table.c[column] < val

            elif "$gt" in query_str:
                return table.c[column] > val

            elif "$lte" in query_str:
                return table.c[column] <= val

            elif "$gte" in query_str:
                return table.c[column] >= val

    return table.c[column] == query_str


def to_json(result_map, limit=10):
    list_dict_result = []
    for k, v in result_map.items():
        dict_result = k.__dict__
        dict_result.pop(IGNORE.INSTANCE_STATE, None)
        dict_result['table'] = clean_output(v, as_list=True)
        list_dict_result.append(dict_result)

    if len(list_dict_result) == 1:
        return list_dict_result[0]

    else:

        return list_dict_result[:limit]


def clean_output(query_res, as_list=False):
    """
    Ensure only the right fields come out following a DB query
    :param query_res: the query result to be clean
    :param as_list: format output to output as list even when result is solely one entity e.g. for a standings table
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

    return result


class DBInterface(object):

    def __init__(self, db):
        self.db = db

    def get_last_game_week(self, filters) -> int:
        """
        Get the latest game week
        :return: int indicator
        """
        base_standings_filters = []
        bs_query = self.db.session.query(func.max(Standings.match_day))

        if type(filters) == list:
            active_filters = filters
        else:
            active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:
                base_standings_filters.append(Standings.__table__.c[filter_[0]] == filter_val)

        return bs_query.filter(*base_standings_filters).scalar()

    def get_competition(self, multi=False, filters=None):
        """
        Query DB for competition record
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

        return clean_output(query_result)

    def get_team(self, multi=False, filters=None):
        """
        Query DB for team record
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
                    db_filters.append(Team.__table__.c[filter_[0]] == filter_val)

        if multi:
            query_result = team_query.filter(or_(*db_filters))
        else:
            query_result = team_query.filter(*db_filters)

        return clean_output(query_result)

    def get_standings(self, limit=10, multi=False, filters=None):
        """
        Query DB for standings records
        :param limit: Due to how heavy standings are, default amount of standings to 10, unless otherwise changed
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param filters: namedtuple with all available filter fields
        :return: matched (if any) standings records
        """
        db_filters = []
        stan_query = self.db.session.query(Standings, StandingsEntry)

        active_filters = [(f, v) for f, v in filters._asdict().items() if v]

        for filter_ in active_filters:
            for filter_val in filter_[1]:

                # Applied different filtering method when it's a team name e.g. SQL LIKE search
                if filter_[0] == STANDINGS.TEAM_NAME:
                    db_filters.append(StandingsEntry.team_name.ilike(f"%{filter_val}%"))

                else:
                    active_table = Standings.__table__
                    if col_exists(table=Standings, col=filter_[0]):
                        active_table = Standings.__table__

                    elif col_exists(table=StandingsEntry, col=filter_[0]):
                        active_table = StandingsEntry.__table__

                    db_filters.append(filter_parse(query_str=filter_val, table=active_table, column=filter_[0]))

        if multi:
            stan_query = stan_query.filter(or_(*db_filters)).limit(100).all()
        else:
            stan_query = stan_query.filter(*db_filters).limit(100).all()  # no standings will have more than 100 entries
        standings_map = {}

        # Reformatting dict to get standings in list per comp as "standing_entries" field
        for tpl in stan_query:
            if tpl[0] not in standings_map:
                standings_map[tpl[0]] = [tpl[1]]

            else:
                standings_map[tpl[0]].append(tpl[1])

        result = to_json(standings_map, limit=limit)
        return result

    def get_match(self, multi: bool = False, filters=None) -> dict:
        """
        Query DB for match record
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param filters: namedtuple with all available filter fields
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
                    db_filters.append(Match.__table__.c[filter_[0]] == filter_val)

        if multi:
            query_result = match_query.filter(or_(*db_filters))

        else:
            query_result = match_query.filter(*db_filters)

        return clean_output(query_result)

    def insert_match(self, record: Union[list,dict]):
        """
        Insert record into DB
        :return:
        """
        if type(record) == dict:
            record = [record]

        for match in record:
            db_player = Match(
                fd_id=match[MATCH.FOOTBALL_DATA_ID],
                season_start_date=match[MATCH.SEASON_START_DATE],
                season_end_date=match[MATCH.SEASON_END_DATE],
                season_year=match[MATCH.SEASON_YEAR],
                utc_date=match[MATCH.MATCH_UTC_DATE],
                start_time_epoch=match[MATCH.START_TIME_EPOCH],
                start_time=match[MATCH.START_TIME],
                status=match[MATCH.STATUS],
                match_day=match[MATCH.MATCHDAY],
                ...
            )
                (
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








