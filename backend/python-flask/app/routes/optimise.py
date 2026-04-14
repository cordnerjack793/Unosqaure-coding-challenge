from unittest import result

from flask import Blueprint, jsonify, request
from app.models.match import Match
from app.models.flight_price import FlightPrice
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy
from app.bonus.best_value_finder import BestValueFinder  # For BONUS CHALLENGE #1

from app.utils.cost_calculator import CostCalculator # For Task 5

optimise_bp = Blueprint('optimise', __name__)


# ============================================================
#  Route Optimisation — YOUR TASK #3 and #5
#
#  Implement route optimisation and budget calculation endpoints.
# ============================================================


# ============================================================
#  POST /api/route/optimise — Optimise a travel route
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #3)
#
# Request body: { "matchIds": ["match-1", "match-5", "match-12", ...] }
#
# Steps:
#   1. Extract matchIds from the request JSON
#   2. Fetch full match data from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Create a strategy instance: NearestNeighbourStrategy()
#      (or DateOnlyStrategy() to test with the working example first)
#   5. Call strategy.optimise(match_dicts)
#   6. Return the optimised route as JSON
#
# TIP: Start by using DateOnlyStrategy to verify your endpoint works,
# then switch to NearestNeighbourStrategy once you've implemented it.
#
# ============================================================

@optimise_bp.route('/optimise', methods=['POST'])
def optimise():
    try:
        #   1. Extract matchIds from the request JSON
        data = request.get_json()
        match_ids = data.get('matchIds')
        
        #   2. Fetch full match data from the database
        matches = Match.query.filter(Match.id.in_(match_ids)).all()
        
        #   3. Convert matches to dicts (using match.to_dict())
        match_dicts = [m.to_dict() for m in matches]

        #   4. Create a strategy instance: NearestNeighbourStrategy()
        strategy = NearestNeighbourStrategy()
        
        #   5. Call strategy.optimise(match_dicts)
        result = strategy.optimise(match_dicts)

        """
        I couldn't work out how to get the countries visted
        match count and feasible into this so did it separately here. 
        
        It would not let me calculate the cost as it still said that it was not feasible.
        
        I am guessing i need to do it in NearestNeighbourStrategy 
        but I couldn't work out how to return it from there.
        
        This also includes rthe matchCount and feasible keys in the return
        """

        countries = []
        for is_country in result.get('stops'):
            country = is_country['match']['city'].get('country')
            if country not in countries:
                countries.append(country)

        #   6. Return the optimised route as JSON
        return jsonify({
            **result,
            "countriesVisited": countries,
            "matchCount": len(match_dicts),
            "feasible": len(countries) >= 3 and len(match_dicts) >= 5
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ============================================================
#  POST /api/route/budget — Calculate trip costs and check budget
# ============================================================
#
# TODO: Implement this endpoint (YOUR TASK #5)
#
# Request body:
# {
#   "budget": 5000.00,
#   "matchIds": ["match-1", "match-5", "match-12", ...],
#   "originCityId": "city-atlanta"
# }
#
# Steps:
#   1. Extract budget, matchIds, and originCityId from request JSON
#   2. Fetch matches by IDs from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Fetch all flight prices from the database
#   5. Create a CostCalculator instance
#   6. Call calculator.calculate(match_dicts, budget, origin_city_id, flight_prices)
#   7. Return the BudgetResult as JSON
#
# IMPORTANT CONSTRAINTS:
#   - User MUST attend at least 1 match in each country (USA, Mexico, Canada)
#   - If the budget is insufficient, return feasible=False with:
#     - minimumBudgetRequired: the actual cost
#     - suggestions: ways to reduce cost
#   - If countries are missing, return feasible=False with:
#     - missingCountries: list of countries not covered
#
# ============================================================


@optimise_bp.route('/budget', methods=['POST'])
def budget_optimise():
    try:
        # 1. Extract
        data = request.get_json() or {}
        budget = data.get('budget')
        match_ids = data.get('matchIds', [])
        origin_city_id = data.get('originCityId')

        # 2. Fetch (Crucial: Order by kickoff here to keep answers consistent)
        matches = Match.query.filter(Match.id.in_(match_ids)).order_by(Match.kickoff).all()
        
        # 3. Convert
        match_dicts = [m.to_dict() for m in matches]

        # 4. Fetch (Crucial: str() and float() ensure the calculator can read the data)
        flight_list = []
        for flight in FlightPrice.query.all():
            flight_list.append({
                'from_city_id': str(flight.origin_city_id),
                'to_city_id': str(flight.destination_city_id),
                'price': float(flight.price_usd or 0)
            })

        # 5. Instance
        calculator = CostCalculator()
        
        # 6. Calculate
        result = calculator.calculate(match_dicts, budget, origin_city_id, flight_list)

        # 7. Return
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# ============================================================
#  POST /api/route/best-value — Find best match combination within budget
# ============================================================
#
# TODO: Implement this endpoint (BONUS CHALLENGE #1)
#
# Request body:
# {
#   "budget": 5000.00,
#   "originCityId": "city-atlanta"
# }
#
# Steps:
#   1. Extract budget and originCityId from request JSON
#   2. Fetch all available matches from the database
#   3. Convert matches to dicts (using match.to_dict())
#   4. Fetch all flight prices from the database
#   5. Create a BestValueFinder instance
#   6. Call finder.find_best_value(match_dicts, budget, origin_city_id, flight_prices)
#   7. Return the BestValueResult as JSON
#
# Requirements:
#   - Find the maximum number of matches that fit within budget
#   - Must include at least 1 match in each country (USA, Mexico, Canada)
#   - Minimum 5 matches required
#   - Return optimised route with cost breakdown
#
# ============================================================

@optimise_bp.route('/best-value', methods=['POST'])
def best_value():
    try:
        #  1. Extract budget and originCityId from request JSON
        data = request.get_json() 
        budget = float(data.get('budget'))
        origin_city_id = data.get('originCityId')

        #  2. Fetch all available matches from the database
        matches = Match.query.all()

        #  3. Convert matches to dicts (using match.to_dict())
        match_dicts = [match.to_dict() for match in matches]

        #  4. Fetch all flight prices from the database
        flight_list = []
        for flight in FlightPrice.query.all():
            flight_list.append({
                'from_city_id': str(flight.origin_city_id),
                'to_city_id': str(flight.destination_city_id),
                'price': float(flight.price_usd or 0)
            })

        # 6. Call finder.find_best_value(match_dicts, budget, origin_city_id, flight_prices)
        finder = BestValueFinder()
        result = finder.find_best_value(match_dicts, budget, origin_city_id, flight_list)

        # 7. Return the BestValueResult as JSON
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500