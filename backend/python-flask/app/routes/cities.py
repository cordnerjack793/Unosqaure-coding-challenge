from flask import Blueprint, jsonify
from app.models.city import City

cities_bp = Blueprint('cities', __name__)

# ============================================================
#  City Routes — YOUR TASK #1
#
#  Implement the REST endpoint for cities.
# ============================================================
def format_city(city):
    return {
        "id": city.id,
        "name": city.name,
        "country": city.country,
        "latitude": city.latitude,
        "longitude": city.longitude,
        "stadium": city.stadium
    }

# ============================================================
#  GET /api/cities — Return all host cities
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #1)
#
# This should return all 16 host cities as a JSON array.
#
# Hint: Use City.query.all() to get all cities from the database,
# then convert each to a dict using city.to_dict()
#
# Expected response: [{ id, name, country, latitude, longitude, stadium }, ...]
#
# ============================================================

@cities_bp.route('/')
def get_all():
    # TODO: Replace with your implementation (YOUR TASK #1)
    try:
        # 1. Fetch all host cities from the database
        cities = City.query.all()
        
        # 2. Convert each city object to a dict using our helper function
        # This matches the "Expected response" exactly
        cities_list = [format_city(city) for city in cities]
        
        # 3. Return the JSON array
        return jsonify(cities_list), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500