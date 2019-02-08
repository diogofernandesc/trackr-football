from ratelimit import limits, sleep_and_retry
import requests as re
import os
import json
from ingest_engine.cons import Competition, Player, Team, Match, MatchEvent, FLS_STATES_MAPPER as state_mapper


class Fantasy(object):
    """
    Wrapper for API available at -> https://fantasy.premierleague.com/drf/
    """
    def __init__(self):
        self.session = re.Session()
        
