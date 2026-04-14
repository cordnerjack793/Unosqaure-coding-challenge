from flask import Blueprint, jsonify
from app.models.city import City

cities_bp = Blueprint('cities', __name__)

# ============================================================
#  City Routes — YOUR TASK #1
#
#  Implement the REST endpoint for cities.
# ============================================================

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
    try:

        # Get all cities from the database
        cities = City.query.all()
        # Create a list to hold the cleaned city data
        cities_list = []
        
        # Loop through the cities to get the data I need.
        for city in cities:
            # Get all the data from each city using the to_dict() method, which includes all fields
            city = city.to_dict()
  
            # Gets the information from the to_dict() output, but only includes the fields you specify
            city_information = {
                "id": city.get("id"),
                "name": city.get("name"),
                "country": city.get("country"),
                "latitude": city.get("latitude"),
                "longitude": city.get("longitude"),
                "stadium": city.get("stadium")
            }
            # Add the city data to the list
            cities_list.append(city_information)
        
        # Return the JSON
        return jsonify(cities_list), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500