from sqlalchemy import union, or_

from db_engine.db_driver import Competition
from ingest_engine.cons import IGNORE


def to_json(result_map):
    dict_result = {}
    for k, v in result_map.items():
        dict_result = k.__dict__
        dict_result.pop(IGNORE.INSTANCE_STATE, None)
        dict_result['standings_entries'] = clean_output(v)
    return dict_result


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
