from flask import Blueprint, request, jsonify, current_app, render_template

ui_service = Blueprint('ui_service', __name__, template_folder='templates', url_prefix='/', static_url_path='',
                       static_folder='static')

www_ui_service = Blueprint('www_ui_service', __name__, template_folder='templates', url_prefix='/', static_url_path='',
                           static_folder='static', subdomain='www')


@ui_service.route('/', methods=['GET'])
def index():
    return ui_service.send_static_file('index.html')


@www_ui_service.route('/', methods=['GET'])
def index():
    return ui_service.send_static_file('index.html')