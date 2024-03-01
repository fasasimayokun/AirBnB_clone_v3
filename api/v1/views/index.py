#!/usr/bin/python3
"""This creates a path '/status' on the object app_views"""


from flask import jsonify
from api.v1.views import app_views
from models import storage


@app_views.route('/status', methods=['GET'])
def api_status():
    """this method returns a JSON response for RESTful API status"""
    response = {'status': 'OK'}
    return jsonify(response)


# it handles the /stats url path
@app_views.route('/stats', methods=['GET'])
def get_stats():
    """this method retrieves the number of individual objects by type"""
    stats = {
            "amenities": storage.count('Amenity'),
            "cities": storage.count('City'),
            "places": storage.count('Place'),
            "reviews": storage.count('Review'),
            "states": storage.count('State'),
            "users": storage.count('User')
            }
    return jsonify(stats)
