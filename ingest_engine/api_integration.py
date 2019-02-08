import requests as re
from ratelimit import sleep_and_retry, limits
import json

SECOND = 1


class ApiIntegration(object):

    def __init__(self):
        self.session = re.session()

    @sleep_and_retry
    @limits(calls=6, period=SECOND)
    def perform_get(self, built_uri):
        """
        Performs GET request dealing with any issues arising specific to this API
        :param built_uri: API Url to use in GET request
        :return: Parsed results or {} if failed
        """

        request = self.session.get(built_uri)
        try:
            result = json.loads(request.text)

        except re.exceptions.ConnectionError:
            result = {}

        except json.decoder.JSONDecodeError:
            result = {}

        return result

