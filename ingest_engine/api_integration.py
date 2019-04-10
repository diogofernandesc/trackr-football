import requests as re
import json

SECOND = 1


class ApiIntegration(object):

    def __init__(self, api_key=None):
        self.session = re.session()
        if api_key:
            self.session.headers.update({'X-Auth-Token': api_key})

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

