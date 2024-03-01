#!/usr/bin/python3
"""this script creates a view for Review objects and handles all
default RESTful API actions(get, post, put, delete, update)"""

from flask import abort, jsonify, request
from models import storage
from models.user import User
from models.place import Place
from models.review import Review
from api.v1.views import app_views


# it handles the url for retrieving all Review objects of a place
@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
def get_reviews_by_place(place_id):
    """this method retrieves all the review of a place in storage"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    # get all reviews objects of the place and convert it to dictionaries
    reviews = [review.to_dict() for review in place.reviews]

    return jsonify(reviews)


# it handles the url for retrieving a review obj by its id
@app_views.route('/reviews/<review_id>', methods=['GET'],
                 strict_slashes=False)
def get_review(review_id):
    """this method retrieves a single review obj"""
    review = storage.get(Review, review_id)
    if review:
        return jsonify(review.to_dict())
    else:
        abort(404)


# it handles the url for deleting a single review by its id
@app_views.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    """this method deletes a review obj"""
    review = storage.get(Review, review_id)
    if review:
        storage.delete(review)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


# it handles the url for creating a review object
@app_views.route('/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
def create_review(place_id):
    """this method creates a new review object"""
    # firstly get the place with the given id
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    # check if the request is in a json format
    if not request.is_json:
        abort(400, 'Not a JSON')

    # get the JSON data from the request
    data = request.get_json()
    if 'text' not in data:
        abort(400, 'Missing text')

    if 'user_id' not in data:
        abort(400, 'Missing user_id')

    # get user object with the user_id from storage
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)

    # assign the place_id to the json data
    data['place_id'] = place_id
    # now create the new review object with the json data
    review = Review(**data)
    review.save()
    # return the newly created review & status code 201 for a success creation
    return jsonify(review.to_dict()), 201


# it handles the url for updating a review object by its id
@app_views.route('/reviews/<review_id>', methods=['PUT'],
                 strict_slashes=False)
def update_review(review_id):
    """this method updates the review object with the given id"""
    review = storage.get(Review, review_id)
    if review:
        if not request.is_json:
            abort(400, 'Not a JSON')

        data = request.get_json()
        keys_ignore = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
        # update the review with the given json data
        for key, value in data.items():
            if key not in keys_ignore:
                setattr(review, key, value)

        # save the changes
        review.save()
        # returns the updated review and 200 status code
        return jsonify(review.to_dict()), 200
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
