import flask
from api_engine.api_cons import API_ENDPOINTS, API, ENDPOINT_DESCRIPTION

app = flask.Flask(__name__)
app.config['DEBUG'] = True
# Logging using app.logger.debug/warning/error


@app.route('/v1')
def base():
    api_endpoints = []
    for cons, endpoint in vars(API_ENDPOINTS).items():
        if not cons.startswith('__'):
            api_endpoints.append({
                API.ENDPOINT_URL: f'/v1/{endpoint}',
                API.URL_DESCRIPTION: ENDPOINT_DESCRIPTION.get(endpoint, "")
            })

    return flask.jsonify({
        API.ENDPOINTS: api_endpoints
    })







if __name__ == '__main__':
    app.run()



