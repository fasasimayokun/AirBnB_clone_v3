#!/usr/bin/python3
"""this creates a new view for state object & it also handles
all default RESTful API actions(get,post,put,delete,update)"""

from flask import abort, jsonify, request
from models.state import State
from api.v1.views import app_views
from models import storage


# this handles the url that retrieves all states in storage
@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_all_states():
    """this method retrieves the list of all state object"""
    states = storage.all(State).values()
    state_list = [state.to_dict() for state in states]
    return jsonify(state_list)


# this handles the url for retrieving a specific state by id
@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
def get_state(state_id):
    """this method retrieves a single state object"""
    state = storage.get(State, state_id)
    if state:
        return jsonify(state.to_dict())
    else:
        abort(404)


# this handles the url for deletes a specific state in storage by id
@app_views.route('/states/<state_id>', methods=['DELETE'])
def delete_state(state_id):
    """this method deletes a single state object"""
    state = storage.get(State, state_id)
    if state:
        storage.delete(state)
        storage.save()
        # return an empty json with 200 ok status code
        return jsonify({}), 200
    else:
        abort(404)


# this handles the url for creating a new state object
@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """this method creates a state object and saves to storage"""
    if not request.is_json:
        abort(400, "Not a JSON")

    kwargs = request.get_json()
    if 'name' not in kwargs:
        abort(400, "Missing name")

    # this creates a new State object with the JSON data
    state = State(**kwargs)
    state.save()
    return jsonify(state.to_dict()), 201


# this handles the url for updating a state object
@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    """this method updates a state object by id and saves to storage"""
    state = storage.get(State, state_id)
    if state:
        if not request.is_json:
            abort(400, 'Not a JSON')

        data_val = request.get_json()
        keys_ignore = ['id', 'created_at', 'updated_at']
        for key, value in data_val.items():
            if key not in keys_ignore:
                setattr(state, key, value)
        state.save()
        return jsonify(state.to_dict()), 200
    else:
        abort(404)


# this handles the 404 error
@app_views.errorhandler(404)
def not_found_error(error):
    """it raises a 404 error"""
    reponse = {'error': 'Not found'}
    return jsonify(response), 404


# this handles the 400 error
@app_views.errorhandler(400)
def bad_request(error):
    """it returns a message for illegal requests"""
    response = {"error": "Bad request"}
    return jsonify(response), 400
