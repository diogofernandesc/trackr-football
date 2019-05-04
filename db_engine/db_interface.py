from sqlalchemy import or_

from db_engine.db_driver import Competition, Team, Standings, StandingsEntry
from ingest_engine.cons import IGNORE, Team as TEAM, Standings as STANDINGS


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


def to_json(result_map):
    list_dict_result = []
    for k, v in result_map.items():
        dict_result = k.__dict__
        dict_result.pop(IGNORE.INSTANCE_STATE, None)
        dict_result['standings_entries'] = clean_output(v)
        list_dict_result.append(dict_result)
    return list_dict_result


def clean_output(query_res):
    """
    Ensure only the right fields come out following a DB query
    :param query_res: the query result to be clean
    :return:
    """
    result = []
    for res in query_res:
        final_res = res.__dict__
        if IGNORE.INSTANCE_STATE in final_res:
            final_res.pop(IGNORE.INSTANCE_STATE, None)

        result.append(final_res)

    if len(result) == 1:
        return result[0]

    return result


class DBInterface(object):

    def __init__(self, db):
        self.db = db

    def get_competition(self, multi=False, id_=None, name=None, code=None, location=None, fd_api_id=None, fls_api_id=None):
        """
        Query DB for competition record
        :param multi: Perform OR query on filters, SQL OR otherwise SQL AND
        :param id_: DB ID of competition
        :param name: The name of the competition, LIKE match performed
        :param code: The code of the competition
        :param location: Country/Location of the competition
        :param fd_api_id: Football data API id for competition
        :param fls_api_id: FastestLiveScores API id for competition
        :return:  matched (if any) competition records
        """
        applied_filters = []
        comp_query = self.db.session.query(Competition)

        if id_:
            for id_val in id_:
                applied_filters.append(Competition.id == id_val)

        if name:
            for name_val in name:
                applied_filters.append(Competition.name.ilike(f"%{name_val}%"))

        if code:
            for code_val in code:
                applied_filters.append(Competition.code == code_val)

        if location:
            for loc_val in location:
                applied_filters.append(Competition.location.ilike(f"%{loc_val}%"))

        if fd_api_id:
            for fd_val in fd_api_id:
                applied_filters.append(Competition.fd_api_id == fd_val)

        if fls_api_id:
            for fls_val in fls_api_id:
                applied_filters.append(Competition.fls_api_id == fls_val)

        if multi:
            query_result = comp_query.filter(or_(*applied_filters))
        else:
            query_result = comp_query.filter(*applied_filters)

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

    def get_standings(self, multi=False, filters=None):
        """
        Query DB for standings records
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

                    db_filters.append(active_table.c[filter_[0]] == filter_val)

        # or_filter = [True for f in active_filters if f[0] == STANDINGS.ID]
        if multi:
            stan_query = stan_query.filter(or_(*db_filters)).all()
        else:
            stan_query = stan_query.filter(*db_filters).all()
        standings_map = {}

        # Reformatting dict to get standings in list per comp as "standing_entries" field
        for tpl in stan_query:
            if tpl[0] not in standings_map:
                standings_map[tpl[0]] = [tpl[1]]
        #
            else:
                standings_map[tpl[0]].append(tpl[1])

        result = to_json(standings_map)
        return result


        # if id_:
        #     stan_query = stan_query.filter(Standings.id == id_)
        #
        # if competition_id:
        #     stan_query = stan_query.filter(Standings.competition_id == competition_id)
        #
        # if type_:
        #     stan_query = stan_query.filter(Standings.type == type_)
        #
        # if season:
        #     stan_query = stan_query.filter(Standings.season == season)
        #
        # if match_day:
        #     stan_query = stan_query.filter(Standings.match_day == match_day)
        #
        # if position:
        #     stan_query = stan_query.filter(StandingsEntry.position == position)
        #
        # stan_query = stan_query.all()
        # standings_map = {}
        #
        # # Reformatting dict to get standings in list per comp as "standing_entries" field
        # for tpl in stan_query:
        #     if tpl[0] not in standings_map:
        #         standings_map[tpl[0]] = [tpl[1]]
        #
        #     else:
        #         standings_map[tpl[0]].append(tpl[1])
        #
        # return to_json(standings_map)








