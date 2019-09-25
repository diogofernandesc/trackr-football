import flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from db_engine.db_interface import DBInterface


application = flask.Flask(__name__, subdomain_matching=True)
application.config['DEBUG'] = True
application.config["SERVER_NAME"] = "trackr.football"
application.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('POSTGRES_CONNECTION_STR')
application.config['JSON_AS_ASCII'] = False
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)
db_interface = DBInterface(db=db)
application.config['db_interface'] = db_interface

# limiter = Limiter(
#     application,
#     key_func=get_remote_address)
#
# application.config['limiter'] = limiter
#
# limiter.limit("200/day;100/hour;10/minute")(api_service)
from api_engine.crud_service import crud_service
from api_engine.api_service import api_service
from api_engine.docs_service import docs_service
from api_engine.ui_service import ui_service, www_ui_service

application.register_blueprint(crud_service)  # Adds functionality for handling DB
application.register_blueprint(api_service)
application.register_blueprint(docs_service)
application.register_blueprint(ui_service)
application.register_blueprint(www_ui_service)


@application.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"message": f"Rate limit threshold exceeded: {e.description}",
                    "status_code": 429})


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000)
