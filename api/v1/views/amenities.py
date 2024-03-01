#!/usr/bin/python3
"""this script creates a view for Amenity objects and handles all
default RESTful API actions(get, post, put, delete, update)"""

from flask import abort, jsonify, request
from models import storage
from models.amenity import Amenity
from api.v1.views import app_views


# it handles the url for retrieving all Amenity objects
@app_views.route('/amenities', methods=['GET'], strict_slashes=False)
def get_all_amenities():
    """this method retrieves all the amenities in storage"""
    amenities = storage.all(Amenity).values()
    return jsonify([amenity.to_dict() for amenity in amenities])


# it handles the url for retrieving an amenity obj by its id
@app_views.route('/amenities/<amenity_id>', methods=['GET'],
                 strict_slashes=False)
def get_amenity(amenity_id):
    """this method retrieves a single amenity obj"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        return jsonify(amenity.to_dict())
    else:
        abort(404)


# it handles the url for deleting a single amenity by its id
@app_views.route('/amenities/<amenity_id>', methods=['DELETE'])
def delete_amenity(amenity_id):
    """this method deletes an amenity obj"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        storage.delete(amenity)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


# it handles the url for creating an amenity object
@app_views.route('/amenities', methods=['POST'], strict_slashes=False)
def create_amenity():
    """this method creates a new amenity"""
    if not request.is_json:
        abort(400, 'Not a JSON')

    # get the JSON data from the request
    data = request.get_json()
    if 'name' not in data:
        abort(400, 'Missing name')

    # create an amenity with the json data given
    amenity = Amenity(**data)
    amenity.save()
    # return status code 201 for a succesful creation
    return jsonify(amenity.to_dict()), 201


# it handles the url for updating an amenity object by its id
@app_views.route('/amenities/<amenity_id>', methods=['PUT'],
                 strict_slashes=False)
def update_amenity(amenity_id):
    """this method updates the amenity object with the given id"""
    amenity = storage.get(Amenity, amenity_id)
    if amenity:
        if not request.is_json:
            abort(400, 'Not a JSON')

        data = request.get_json()
        keys_ignore = ['id', 'created_at', 'updated_at']
        # update the amenity
        for key, value in data.items():
            if key not in keys_ignore:
                setattr(amenity, key, value)

        amenity.save()
        return jsonify(amenity.to_dict()), 200
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
