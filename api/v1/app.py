#!/usr/bin/python3
"""This creates flask app and registers the blueprint app_views
with the flask instance app"""

from flask import Flask, jsonify
from flask_cors import CORS
from models import storage
from api.v1.views import app_views
from os import getenv

app = Flask(__name__)

# it enables the cors and allows requests from any origin
CORS(app, resources={r'/api/v1/*': {'origins': '0.0.0.0'}})

# this registers the app_views blueprint
app.register_blueprint(app_views)
app.url_map.strict_slashes = False


# this handles teardown func to close the sqlalchemy session obj afer
# each request
@app.teardown_appcontext
def teardown_engine(exception):
    """this removes the present sqlalchemy session object
    after each request"""
    storage.close()


# this handles the 404 Not Found error
@app.errorhandler(404)
def not_found(error):
    """this returns json response with Not found message"""
    response = {"error": "Not found"}
    return jsonify(response), 404


if __name__ == '__main__':
    # getting the host and port from the environment variables
    HOST = getenv('HBNB_API_HOST', '0.0.0.0')
    PORT = int(getenv('HBNB_API_PORT', 5000))
    # running the app in threaded mode for better performance
    app.run(host=HOST, port=PORT, threaded=True)
