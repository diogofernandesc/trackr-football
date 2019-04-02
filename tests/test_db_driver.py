import unittest

class ApiTest(unittest.TestCase):
    def setUp(self):
        self.fantasy = Fantasy()

    def tearDown(self):
        self.fantasy.session.close()