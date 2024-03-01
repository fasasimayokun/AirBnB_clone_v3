#!/usr/bin/python3
"""this creates a view for city objects and handles all default
RESTful Api actions"""

from flask import abort, jsonify, request
from models.state import State
from models.city import City
from models import storage
from api.v1.views import app_views


# it handles the url for retrieving all City objects of a state
@app_views.route('/states/<state_id>/cities', methods=['GET'],
                 strict_slashes=False)
def get_cities_by_state(state_id):
    """this method retrieves the list of all city objects of a state"""
    state = storage.get(State, state_id)
    # if the state doesn't exist
    if not state:
        abort(404)

    # getting all the cities in the state and covert it to dictionaries
    cities = [city.to_dict() for city in state.cities]
    return jsonify(cities)


# it handles the url for retrieving a single city by its id
@app_views.route('/cities/<city_id>', methods=['GET'], strict_slashes=False)
def get_city(city_id):
    """it retrieves a single city obj"""
    city = storage.get(City, city_id)
    if city:
        return jsonify(city.to_dict())
    else:
        abort(404)


# it handles the url for deleting a city by its id
@app_views.route('/cities/<city_id>', methods=['DELETE'])
def delete_city(city_id):
    """this method deletes a city obj"""
    city = storage.get(City, city_id)
    # if the city exist
    if city:
        # delete from storage and save changes
        storage.delete(city)
        storage.save()
        # to show succesful deletion return 200 status code
        return jsonify({}), 200
    else:
        abort(404)


# it handles the url for creating a new city under a specified state
@app_views.route('/states/<state_id>/cities', methods=['POST'],
                 strict_slashes=False)
def create_city(state_id):
    """this method creates a new city under a state"""
    state = storage.get(State, state_id)
    # if the state doesn't exist
    if not state:
        abort(404)

    # check if the request data is a JSON
    if not request.is_json:
        abort(400, 'Not a JSON')

    data = request.get_json()
    if 'name' not in data:
        abort(400, 'Missing name')

    data['state_id'] = state_id
    # create the new city object with the Json datat
    city = City(**data)
    city.save()
    return jsonify(city.to_dict()), 201


# it handles the url for updating an existing city object by id
@app_views.route('/cities/<city_id>', methods=['PUT'], strict_slashes=False)
def update_city(city_id):
    """this method updates the city object"""
    city = storage.get(City, city_id)
    if city:
        if not request.is_json:
            abort(400, 'Not a JSON')

        # get the json data from the request
        data = request.get_json()
        # the fields not to update
        keys_ignore = ['id', 'state_id', 'created_at', 'updated_at']

        for key, value in data.items():
            if key not in keys_ignore:
                setattr(city, key, value)

        city.save()
        return jsonify(city.to_dict()), 200
    else:
        abort(404)


@app_views.errorhandler(404)
def not_found(error):
    """the method that handles the 404 not found errror"""
    return jsonify({"error": "Not found"}), 404


@app_views.errorhandler(400)
def bad_request(error):
    """the method that handles the 400 illegal request to API"""
    return jsonify({"error": "Bad Request"}), 400
