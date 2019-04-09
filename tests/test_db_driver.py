import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_TEST_CONNECTION_STR')  # For debugging/testing
        self.db = SQLAlchemy(self.app)

    def tearDown(self):
        pass



