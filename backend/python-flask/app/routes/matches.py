from flask import Blueprint, jsonify, request
from app.models.match import Match

matches_bp = Blueprint('matches', __name__)

# ============================================================
#  Matches Routes — YOUR TASK #2
#
#  Implement the REST endpoints for matches.
# ============================================================


# ============================================================
#  GET /api/matches — Return matches with optional filters
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #2)
#
# Query parameters (both optional):
#   ?city=city-atlanta    → filter by city ID
#   ?date=2026-06-14      → filter by date (YYYY-MM-DD)
#
# Hint: Use request.args.get() to extract optional query parameters.
# Use Match.query with filter_by() or filter() to apply filters.
# Order results by kickoff and convert to dicts using match.to_dict()
#
# ============================================================

@matches_bp.route('', methods=['GET'])
def get_matches():
    try:
    
        # Extract optional query parameters
        city_id = request.args.get('city')  # e.g., 'city-atlanta'
        match_date = request.args.get('date')  # e.g., '2026-06-11'

        # Start building the query
        query = Match.query

        # Filter by City ID
        if city_id:
            # Gets information about the games in a specific city using the city_id
            query = query.filter_by(city_id=city_id)
        
        # Filter by Date
        if match_date:
            # Gets infromation about the games on a specific date using the match_date
            # Using .contains() ignores the time part
            query = query.filter(Match.kickoff.contains(match_date))
            
        
        # Gets the information about the games and orders them by kickoff time in ascending order
        matches = query.order_by(Match.kickoff).all()
            
        #  Return the list using the model's to_dict method
        return jsonify([m.to_dict() for m in matches]), 200
    
    except Exception as e:
         return jsonify({"error": str(e)}), 500



# ============================================================
#  GET /api/matches/<id> — Return a single match by ID
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #2)
#
# Hint: Use Match.query.get(id) — returns None if not found.
# Return 404 with an error message if not found.
#
# ============================================================

@matches_bp.route('/<id>', methods=['GET'])
def get_match_by_id(id):
    try:
        # Get the match by ID using Match.query.get(id)
        match = Match.query.get(id)

        # If the match is found, return its details as JSON using match.to_dict()
        return jsonify(match.to_dict()), 200
    
    except Exception as e:
         return jsonify({"error": str(e)}), 500