import requests as re


def test_request():
    result = re.get("http://api.football-api.com/2.0/standings/1204?Authorization=565ec012251f932ea4000001fa542ae9d994470e73fdb314a8a56d76")
    # print(result.text)

test_request()