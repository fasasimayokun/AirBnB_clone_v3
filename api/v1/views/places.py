#!/usr/bin/python3
"""this script creates a view for Place objects and handles all
default RESTful API actions(get, post, put, delete, update)"""

from flask import abort, jsonify, request
from models import storage
from models.user import User
from models.city import City
from models.place import Place
from models.state import State
from models.amenity import Amenity
from api.v1.views import app_views


# it handles the url for retrieving all place objects of a city
@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places_by_city(city_id):
    """this method retrieves all the place of a city in storage"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    # get all places objects of the city and convert it to dictionaries
    places = [place.to_dict() for place in city.places]

    return jsonify(places)


# it handles the url for retrieving an place obj by its id
@app_views.route('/places/<place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    """this method retrieves a single place obj"""
    place = storage.get(Place, place_id)
    if place:
        return jsonify(place.to_dict())
    else:
        abort(404)


# it handles the url for deleting a single place by its id
@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place(place_id):
    """this method deletes an user obj"""
    place = storage.get(Place, place_id)
    if place:
        storage.delete(place)
        storage.save()
        return jsonify({}), 200
    else:
        abort(404)


# it handles the url for creating an place object
@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """this method creates a new place object"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    # check if the request is in a json format
    if not request.is_json:
        abort(400, 'Not a JSON')

    # get the JSON data from the request
    data = request.get_json()
    if 'name' not in data:
        abort(400, 'Missing name')

    if 'user_id' not in data:
        abort(400, 'Missing user_id')
    # get user object with the user_id from storage
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)

    # assign the city_id to the json data
    data['city_id'] = city_id
    # now create the new place object with the json data
    place = Place(**data)
    place.save()
    # return the newly created place & status code 201 for a succesful creation
    return jsonify(place.to_dict()), 201


# it handles the url for updating a place object by its id
@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """this method updates the place object with the given id"""
    place = storage.get(Place, place_id)
    if place:
        if not request.is_json:
            abort(400, 'Not a JSON')

        data = request.get_json()
        keys_ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
        # update the place with the given json data
        for key, value in data.items():
            if key not in keys_ignore:
                setattr(place, key, value)

        place.save()
        # returns the updated place and 200 status code
        return jsonify(place.to_dict()), 200
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


# it handles the new endpoint POST /api/v1/places_search
@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """this method retrieves place objects based on
    the given json search criteria"""

    # check the request format to be json
    if not request.is_json:
        abort(400, description="Not a JSON")

    # get the data from the given json body
    data = request.get_json()

    # get the criteria from the data
    if data and len(data):
        states = data.get('states', None)
        cities = data.get('cities', None)
        amenities = data.get('amenities', None)

    # retrieve all places if no criteria given
    if not data or not len(data) or (not states and not
                                     cities and not amenities):
        places = storage.all(Place).values()
        list_places = []
        # change each place object to a dictionary and join it to the list
        for place in places:
            list_places.append(place.to_dict())

        return jsonify(list_places)

    # creating a list to store the filtered places based on criteria provided
    list_places = []

    # retrives filtered places based on states criteria
    if states:
        states_obj = [storage.get(State, st_id) for st_id in states]
        # loop thru individual state object
        for state in states_obj:
            if state:
                # loop thru individual city in the state's cities list
                for city in state.cities:
                    if city:
                        for place in city.places:
                            # append the place to the list of filtered places
                            list_places.append(place)

    # filtering places based on cities criteria
    if cities:
        city_obj = [storage.get(City, ct_id) for ct_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in list_places:
                        list_places.append(place)

    # filter places based on amenities criteria
    if amenities:
        # retrieve all place objects from storage if list_places is empty
        if not list_places:
            list_places = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, am_id) for am_id in amenities]
        list_places = [place for place in list_places
                       if all([am in place.amenities for am in amenities_obj])]

    # preparing the final list of places for response
    places = []
    for plc in list_places:
        dt = plc.to_dict()
        # remove the amenities key from the dictionary
        dt.pop('amenities', None)
        places.append(dt)

    return jsonify(places)
