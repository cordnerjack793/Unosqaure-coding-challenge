from flask import Blueprint, jsonify, request
from app.models.match import Match
from app.models.flight_price import FlightPrice
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy
from app.bonus.best_value_finder import BestValueFinder  # For BONUS CHALLENGE #1

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
        # 1. Ticket Costs (Always works because it's top-level)
        t_cost = sum(m.get('ticketPrice', 0) for m in matches)
        
        # 2. Flight Costs (Fixed to look inside the 'city' object)
        f_total, cur = 0, origin
        for m in matches:
            # Check nested city object first, then fallback to flat keys
            city_data = m.get('city', {})
            dest = city_data.get('id') or m.get('cityId') or m.get('city_id')
            
            if cur and dest:
                # If flight not found, we use a $500 default to show 'some' cost
                f_total += flights.get(f"{cur}_{dest}", 500.0 if cur != dest else 0)
            cur = dest

        # 3. Accommodation (Fixed to use nested accommodationPerNight)
        s_total = 0
        for i in range(len(matches) - 1):
            m1, m2 = matches[i], matches[i+1]
            
            # Get price from the nested city object
            price_per_night = m1.get('city', {}).get('accommodationPerNight', 0)
            
            try:
                # Safely parse the day from the kickoff string
                k1, k2 = str(m1.get('kickoff', '')), str(m2.get('kickoff', ''))
                d1, d2 = int(k1[8:10]), int(k2[8:10])
                nights = (d2 - d1) if d2 >= d1 else (30 - d1 + d2)
                s_total += max(1, nights) * price_per_night
            except (ValueError, IndexError):
                # Fallback to at least 1 night if dates are missing/broken
                s_total += price_per_night

        # 4. Final Validation
        found_countries = {str(m.get('city', {}).get('country', '')).upper() for m in matches}
        visited = [c for c in self.REQUIRED if c.upper() in found_countries]
        missing = [c for c in self.REQUIRED if c not in visited]
        
        total = t_cost + f_total + s_total
        
        return {
            "feasible": total <= budget and not missing and len(matches) >= 5,
            "totalCost": round(total, 2),
            "costBreakdown": {
                "tickets": round(t_cost, 2), 
                "flights": round(f_total, 2), 
                "accommodation": round(s_total, 2), 
                "total": round(total, 2)
            },
            "countriesVisited": visited,
            "missingCountries": missing
        }
    REQUIRED = ['USA', 'Mexico', 'Canada']

class CostCalculator:
    def calculate(self, matches, budget, origin, flights):
        if not matches:
            return {
                "feasible": False,
                "totalCost": 0,
                "costBreakdown": {"tickets": 0, "flights": 0, "accommodation": 0, "total": 0},
                "countriesVisited": [],
                "missingCountries": self.REQUIRED
            }

        # 1. Ticket Costs
        t_cost = sum(m.get('ticketPrice', 0) for m in matches)
        
        # 2. Flight Costs
        f_total = 0
        # Ensure origin is a string to match the flight map keys
        cur = str(origin) if origin else None
        
        for m in matches:
            # Look everywhere for the Destination ID
            city_obj = m.get('city', {})
            dest = str(city_obj.get('id') or m.get('cityId') or m.get('city_id') or '')
            
            if cur and dest and cur != dest:
                # Build the lookup key (e.g., "city-atlanta_city-mexico")
                flight_key = f"{cur}_{dest}"
                # If flight not found in f_map, we use 500 as a placeholder
                f_total += flights.get(flight_key, 500.0)
            
            # Move our current location to this match's city for the next leg
            cur = dest

        # 3. Accommodation Costs
        s_total = 0
        for i in range(len(matches) - 1):
            m1 = matches[i]
            m2 = matches[i+1]
            
            # Get price from nested city object
            price_per_night = m1.get('city', {}).get('accommodationPerNight', 0)
            
            try:
                # Extract day from 'YYYY-MM-DD' or 'ISO' string
                k1, k2 = str(m1.get('kickoff', '')), str(m2.get('kickoff', ''))
                d1, d2 = int(k1[8:10]), int(k2[8:10])
                
                # Logic for month-rollover (simplified)
                nights = (d2 - d1) if d2 >= d1 else (30 - d1 + d2)
                s_total += max(1, nights) * price_per_night
            except (ValueError, IndexError):
                # If date parsing fails, assume at least 1 night stay
                s_total += price_per_night

        # 4. Final Totals and Validation
        total = t_cost + f_total + s_total
        
        # Check Country Coverage
        found_countries = {str(m.get('city', {}).get('country', '')).upper() for m in matches}
        visited = [c for c in self.REQUIRED if c.upper() in found_countries]
        missing = [c for c in self.REQUIRED if c not in visited]
        
        return {
            "feasible": total <= budget and len(visited) == 3 and len(matches) >= 5,
            "totalCost": round(total, 2),
            "costBreakdown": {
                "tickets": round(t_cost, 2),
                "flights": round(f_total, 2),
                "accommodation": round(s_total, 2),
                "total": round(total, 2)
            },
            "countriesVisited": visited,
            "missingCountries": missing
        }
   
@optimise_bp.route('/budget', methods=['POST'])
def budget_optimise():
    data = request.get_json() or {}
    budget = data.get('budget', 0)
    ids = data.get('matchIds', [])
    origin = str(data.get('originCityId', '')) # Force string

    # 1. Fetch and Sort
    raw_matches = Match.query.filter(Match.id.in_(ids)).all()
    matches = [m.to_dict() for m in sorted(raw_matches, key=lambda x: x.kickoff)]
    
    # 2. Build Flight Map - Normalize ALL IDs to strings
    f_map = {}
    for f in FlightPrice.query.all():
        # Get whichever ID exists and force it to a string
        f_from = str(getattr(f, 'origin_city_id', getattr(f, 'from_city_id', '')))
        f_to = str(getattr(f, 'destination_city_id', getattr(f, 'to_city_id', '')))
        f_price = getattr(f, 'price', getattr(f, 'priceUsd', 0))
        f_map[f"{f_from}_{f_to}"] = float(f_price)

    # 3. Calculate
    result = CostCalculator().calculate(matches, budget, origin, f_map)

    return jsonify({
        **result, 
        "stops": [{"match": m, "city": m.get('city')} for m in matches]
    }), 200
    
    
    
    

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
    # 1. Extract budget and originCityId from request JSON
    data = request.get_json()
    budget = float(data.get('budget'))
    origin_city_id = data.get('originCityId')

    # 2. Fetch all available matches from the database
    all_matches = Match.query.all()
    
    # 3. Convert matches to dicts
    match_dicts = [match.to_dict() for match in all_matches]
    
    # 4. Fetch all flight prices 
    flight_prices = []
    for fp in FlightPrice.query.all():
        f_dict = fp.to_dict()
        flight_prices.append({
            'from_city_id': f_dict.get('origin_city_id') or f_dict.get('from_city_id'),
            'to_city_id': f_dict.get('destination_city_id') or f_dict.get('to_city_id'),
            'price': float(f_dict.get('price') or f_dict.get('priceUsd', 0))
        })

    # 5. Create a BestValueFinder instance
    finder = BestValueFinder()

    # 6. Call the logic
    result = finder.find_best_value(
        all_matches=match_dicts, 
        budget=budget, 
        origin_city_id=origin_city_id, 
        flight_prices=flight_prices
    )

    # 7. Return the result
    return jsonify(result), 200