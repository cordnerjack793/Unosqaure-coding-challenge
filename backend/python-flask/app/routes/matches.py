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
    # 1. Extract optional query parameters
    city_id = request.args.get('city')  # e.g., 'city-atlanta'
    match_date = request.args.get('date')  # e.g., '2026-06-11'

    query = Match.query

    # 2. Filter by City
    if city_id:
        query = query.filter(Match.city_id == city_id)
    
    # 3. Filter by Date
    if match_date:
        # Using .contains() ignores the time part
        query = query.filter(Match.kickoff.contains(match_date))

    # 4. Order results by kickoff
    matches = query.order_by(Match.kickoff.asc()).all()

    # 5. Return the list using the model's to_dict method
    # If this still 500s, use the manual mapping from my previous message
    return jsonify([m.to_dict() for m in matches]), 200


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
    match = Match.query.get(id)

    if match is None:
        return jsonify({"error": f"Match {id} not found"}), 404

    return jsonify(match.to_dict()), 200
