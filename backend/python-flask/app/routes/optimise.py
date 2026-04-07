from flask import Blueprint, jsonify, request
from app.models.match import Match
from app.models.flight_price import FlightPrice
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy

optimise_bp = Blueprint('optimise', __name__)


# ============================================================
#  POST /api/route/optimise — Optimise a travel route
# ============================================================

@optimise_bp.route('/optimise', methods=['POST'])
def optimise():
    # 1. Extract matchIds from the request JSON
    data = request.get_json()
    match_ids = data.get('matchIds', []) 

    # 2. Fetch full match data from the database
    matches = Match.query.filter(Match.id.in_(match_ids)).all()

    # 3. Convert matches to dicts
    match_dicts = [m.to_dict() for m in matches]

    # 4. Create a strategy instance
    strategy = NearestNeighbourStrategy()
    
    # 5. Call the optimise method on our strategy
    optimised_route = strategy.optimise(match_dicts)
    

    countries = {m.get('city', {}).get('country', '').upper() for m in match_dicts}
    visited = []
    if any(c in countries for c in ['USA', 'UNITED STATES']): visited.append('USA')
    if 'MEXICO' in countries: visited.append('Mexico')
    if 'CANADA' in countries: visited.append('Canada')
  
    optimised_route["countriesVisited"] = visited
    optimised_route["missingCountries"] = [c for c in ['USA', 'Mexico', 'Canada'] if c not in visited]
    optimised_route["feasible"] = len(match_ids) >= 5 and len(visited) == 3

    # 6. Return the optimised route as JSON
    return jsonify(optimised_route), 200


# ============================================================
#  POST /api/route/budget — Calculate trip costs and check budget
# ============================================================

class CostCalculator:
    REQUIRED = ['USA', 'Mexico', 'Canada']

    def calculate(self, matches, budget, origin, flights):
        # 1. Costs: Tickets + Flights
        t_cost = sum(m.get('ticketPrice', 0) for m in matches)
        f_total, cur = 0, origin
        for m in matches:
            dest = m.get('cityId') or m.get('city_id')
            f_total += flights.get(f"{cur}_{dest}", 500.0 if cur != dest else 0)
            cur = dest

        # 2. Costs: Accommodation (Calculated via zip to compare match pairs)
        s_total = matches[0].get('city', {}).get('accommodationPerNight', 0) if matches else 0
        for m1, m2 in zip(matches, matches[1:]):
            d1, d2 = int(str(m1['kickoff'])[8:10]), int(str(m2['kickoff'])[8:10])
            nights = (d2 - d1) if d2 >= d1 else (30 - d1 + d2)
            s_total += max(0, nights) * m1.get('city', {}).get('accommodationPerNight', 0)

        # 3. Validation
        countries = {str(m.get('city', {}).get('country', m.get('country', ''))).lower() for m in matches}
        visited = [c for c in self.REQUIRED if any(req in str(countries) for req in [c.lower(), 'united' if c == 'USA' else c])]
        
        total, missing = t_cost + f_total + s_total, [c for c in self.REQUIRED if c not in visited]
        
        return {
            "feasible": total <= budget and not missing and len(matches) >= 5,
            "totalCost": round(total, 2),
            "costBreakdown": {"tickets": t_cost, "flights": f_total, "accommodation": s_total, "total": total},
            "countriesVisited": visited, "missingCountries": missing,
            "minimumBudgetRequired": round(total, 2),
            "suggestions": [f"Over budget by ${total - budget:.0f}"] if total > budget else []
        }

@optimise_bp.route('/budget', methods=['POST'])
def budget_optimise():
    # 1. Extract 
    data = request.get_json() or {}
    budget, ids, origin = data.get('budget', 0), data.get('matchIds', []), data.get('originCityId')

    # 2. Fetch & 3. Convert (Combined into one sorted list comprehension)
    matches = [m.to_dict() for m in sorted(Match.query.filter(Match.id.in_(ids)).all(), key=lambda x: x.kickoff)]
    
    # 4. Fetch & Map Flights (One-liner dictionary comprehension)
    f_map = {f"{getattr(f, 'origin_city_id', getattr(f, 'from_city_id', ''))}_{getattr(f, 'destination_city_id', getattr(f, 'to_city_id', ''))}": 
             getattr(f, 'price', getattr(f, 'priceUsd', 0)) for f in FlightPrice.query.all()}

    # 5. Create instance & 6. Call
    result = CostCalculator().calculate(matches, budget, origin, f_map)

    # 7. Return (Directly spreading the result dictionary)
    return jsonify({**result, "stops": [{"match": m} for m in matches]}), 200
    
    
    
    
    
    
    
    
    

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
    # TODO: Replace with your implementation (BONUS CHALLENGE #1)
    return jsonify({}), 200
