import flask
from flask_sqlalchemy import SQLAlchemy
import os

from db_engine.db_interface import DBInterface


app = flask.Flask(__name__, subdomain_matching=True)
app.config['DEBUG'] = True
app.config["SERVER_NAME"] = "localhost:5000"
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db_interface = DBInterface(db=db)
app.config['db_interface'] = db_interface

from api_engine.crud_service import crud_service
from api_engine.api_service import api_service
from api_engine.docs_service import docs_service
app.register_blueprint(crud_service)  # Adds functionality for handling DB
app.register_blueprint(api_service)
app.register_blueprint(docs_service)

if __name__ == '__main__':
    app.run()
