from flask import Blueprint, request, jsonify, current_app, render_template

docs_service = Blueprint('docs_service', __name__, subdomain='docs', template_folder='templates',
                         static_url_path='', static_folder='static', url_prefix='/')


@docs_service.route('/', methods=['GET'])
def docs():
    return docs_service.send_static_file('output.html')
