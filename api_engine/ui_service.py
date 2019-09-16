from flask import Blueprint, request, jsonify, current_app, render_template

ui_service = Blueprint('ui_service', __name__, template_folder='templates', url_prefix='/', static_url_path='',
                       static_folder='static')


@ui_service.route('/', methods=['GET'])
def index():
    return ui_service.send_static_file('index.html')
