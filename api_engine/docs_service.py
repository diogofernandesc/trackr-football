from flask import Blueprint, request, jsonify, current_app, render_template

docs_service = Blueprint('docs_service', __name__, template_folder='templates', url_prefix='/', subdomain='docs')


@docs_service.route('/', methods=['GET'])
def docs():
    return render_template('output.html')
