#!/usr/bin/python3
"""this script creates a view for User objects and handles all
default RESTful API actions(get, post, put, delete, update)"""

from flask import abort, jsonify, request
from models import storage
from models.user import User
from api.v1.views import app_views


# it handles the url for retrieving all User objects
@app_views.route('/users', methods=['GET'], strict_slashes=False)
def get_all_users():
    """this method retrieves all the users in storage"""
    users = storage.all(User).values()
    return jsonify([user.to_dict() for user in users])


# it handles the url for retrieving an user obj by its id
@app_views.route('/users/<user_id>', methods=['GET'],
                 strict_slashes=False)
def get_user(user_id):
    """this method retrieves a single user obj"""
    user = storage.get(User, user_id)
    if user:
        return jsonify(user.to_dict())
    else:
        abort(404)


# it handles the url for deleting a single user by its id
@app_views.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """this method deletes an user obj"""
    user = storage.get(User, user_id)
    if user:
        storage.delete(user)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


# it handles the url for creating an user object
@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user():
    """this method creates a new user"""
    if not request.is_json:
        abort(400, 'Not a JSON')

    # get the JSON data from the request
    data = request.get_json()
    if 'email' not in data:
        abort(400, 'Missing email')

    if 'password' not in data:
        abort(400, 'Missing password')
    # create an user with the json data given
    user = User(**data)
    user.save()
    # return the newly created user & status code 201 for a succesful creation
    return jsonify(user.to_dict()), 201


# it handles the url for updating an user object by its id
@app_views.route('/users/<user_id>', methods=['PUT'],
                 strict_slashes=False)
def update_user(user_id):
    """this method updates the user object with the given id"""
    user = storage.get(User, user_id)
    if user:
        if not request.is_json:
            abort(400, 'Not a JSON')

        data = request.get_json()
        keys_ignore = ['id', 'email', 'created_at', 'updated_at']
        # update the user
        for key, value in data.items():
            if key not in keys_ignore:
                setattr(user, key, value)

        user.save()
        # returns the updated user and 200 status code
        return jsonify(user.to_dict()), 200
    else:
        abort(404)


@app_views.errorhandler(404)
def not_found(error):
    """handles the 404 not found error"""
    response = {'error': 'Not found'}
    return jsonify(response), 404


@app_views.errorhandler(400)
def bad_request(error):
    """handles the 400 bad request error"""
    response = {'error': 'Bad Request'}
    return jsonify(response), 400
