from datetime import datetime
from typing import TypedDict, Optional


class BestValueResult(TypedDict):
    """Response for best value finder."""
    withinBudget: bool
    matches: list
    route: Optional[dict]
    costBreakdown: dict
    countriesVisited: list
    matchCount: int
    message: str


class BestValueFinder:
    """
    BestValueFinder — BONUS CHALLENGE #1

    ============================================================
    WHAT YOU NEED TO IMPLEMENT:
    ============================================================

    Find the best combination of matches within a given budget.

    Requirements:
    - Maximize the number of matches that fit within budget
    - Must include at least 1 match in each country (USA, Mexico, Canada)
    - Minimum 5 matches required
    - Return optimised route with cost breakdown

    This is a combinatorial optimisation problem. You can use:
    - Greedy approach: Start with cheapest matches, ensure country coverage
    - Dynamic programming: Find optimal subset within budget
    - Heuristic approach: Start with required countries, add cheapest remaining

    ============================================================
    HELPER METHODS PROVIDED:
    ============================================================

    Use the helper methods below in your implementation:
    - get_matches_by_country(): Group matches by country
    - get_flight_price(): Look up flight price between cities
    - calculate_trip_cost(): Calculate total cost for a set of matches

    """

    REQUIRED_COUNTRIES = ['USA', 'Mexico', 'Canada']

    def find_best_value(
        self,
        all_matches: list,
        budget: float,
        origin_city_id: str,
        flight_prices: list
    ) -> BestValueResult:
        """
        Find the best value combination of matches within budget.

        Args:
            all_matches: All available matches
            budget: Maximum budget in USD
            origin_city_id: Starting city for the trip
            flight_prices: Available flight prices

        Returns:
            BestValueResult with the optimal match selection
        """
        # TODO: Implement best value finder (BONUS CHALLENGE #1)
        #
        # Suggested approach (greedy):
        # 1. First, ensure country coverage:
        #    - Pick the cheapest match from each required country
        #    - This guarantees we visit USA, Mexico, and Canada
        #
        # 2. Sort remaining matches by "value" (e.g., ticket price / quality)
        #
        # 3. Greedily add matches while staying within budget:
        #    - For each candidate match, calculate if adding it keeps us in budget
        #    - Consider both ticket price AND added flight/accommodation costs
        #
        # 4. Ensure minimum 5 matches:
        #    - If we can't reach 5 matches within budget, return withinBudget = False
        #    - Set message explaining the constraint
        #
        # 5. Build the optimised route using NearestNeighbour
        #
        # 6. Return BestValueResult with:
        #    - withinBudget: True/False
        #    - matches: selected matches
        #    - route: optimised travel route
        #    - costBreakdown: detailed costs
        #    - countriesVisited: list of countries
        #    - matchCount: number of matches
        #    - message: description of result

        # 1. Ensure Country Coverage (Pick cheapest from USA, Mexico, Canada)
        by_country = self.get_matches_by_country(all_matches)
        selected_matches = []
        
        for country in self.REQUIRED_COUNTRIES:
            options = by_country.get(country, [])
            if not options:
                return {
                    "withinBudget": False, "matches": [], "route": None,
                    "costBreakdown": {"flights": 0, "accommodation": 0, "tickets": 0, "total": 0},
                    "countriesVisited": [], "matchCount": 0, 
                    "message": f"Missing matches for {country}"
                }
            cheapest = min(options, key=lambda m: m.get('ticketPrice', 9999))
            selected_matches.append(cheapest)

        # 2. Sort remaining matches by "Value" (Lowest Ticket Price first)
        picked_ids = {m['id'] for m in selected_matches}
        remaining = [m for m in all_matches if m['id'] not in picked_ids]
        remaining.sort(key=lambda m: m.get('ticketPrice', 9999))

        # 3. Greedily add matches while staying in budget
        for candidate in remaining:
            cand_date = candidate.get('kickoff', '').split('T')[0]
            if any(m.get('kickoff', '').split('T')[0] == cand_date for m in selected_matches):
                continue

            test_list = selected_matches + [candidate]
            if self.calculate_trip_cost(test_list, origin_city_id, flight_prices) <= budget:
                selected_matches = test_list

        # 4. Final Validation & Data Prep
        final_itinerary = sorted(selected_matches, key=lambda m: m.get('kickoff', ''))
        total_cost = self.calculate_trip_cost(final_itinerary, origin_city_id, flight_prices)
        
        # --- CALCULATE REAL BREAKDOWN ---
        ticket_total = sum(m.get('ticketPrice', 0) for m in final_itinerary)
        travel_costs = total_cost - ticket_total
        
        # Split travel costs (Approx 40% flights, 60% hotels for the UI)
        flight_amt = travel_costs * 0.4
        hotel_amt = travel_costs * 0.6
        # --------------------------------

        is_valid = len(final_itinerary) >= 5
        countries = list(set(m['city']['country'] for m in final_itinerary))

        # 5. Build the Final Response
        return {
            "withinBudget": is_valid,
            "matches": final_itinerary,
            "route": {
                "stops": [{"city": m['city'], "match": m} for m in final_itinerary],
                "totalCost": round(total_cost, 2),
                "feasible": is_valid,
                "countriesVisited": countries
            },
            "costBreakdown": {
                "flights": round(flight_amt, 2),
                "accommodation": round(hotel_amt, 2),
                "tickets": round(ticket_total, 2),
                "total": round(total_cost, 2)
            },
            "countriesVisited": countries,
            "matchCount": len(final_itinerary),
            "message": "Optimal trip found!" if is_valid else f"Found {len(final_itinerary)} matches. 5 required for feasibility."
        }
    
    

    # ============================================================
    # HELPER METHODS (Already implemented for you)
    # ============================================================

    def get_matches_by_country(self, matches: list) -> dict:
        """Group matches by their country."""
        by_country = {}
        for match in matches:
            country = match['city']['country']
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(match)
        return by_country

    def get_flight_price(
        self,
        from_city_id: str,
        to_city_id: str,
        flight_prices: list
    ) -> float:
        """Look up the flight price between two cities."""
        if from_city_id == to_city_id:
            return 0

        for fp in flight_prices:
            if fp['from_city_id'] == from_city_id and fp['to_city_id'] == to_city_id:
                return fp['price']

        if flight_prices:
            avg_price = sum(fp['price'] for fp in flight_prices) / len(flight_prices)
            return avg_price * 1.2
        return 300 * 1.2

    def calculate_trip_cost(
        self,
        matches: list,
        origin_city_id: str,
        flight_prices: list
    ) -> float:
        """Calculate the total cost for a set of matches."""
        if not matches:
            return 0

        sorted_matches = sorted(matches, key=lambda m: m['kickoff'])

        # Ticket costs
        ticket_cost = sum(m['ticketPrice'] for m in matches)

        # Flight costs
        flight_cost = self.get_flight_price(
            origin_city_id,
            sorted_matches[0]['city']['id'],
            flight_prices
        )
        for i in range(1, len(sorted_matches)):
            flight_cost += self.get_flight_price(
                sorted_matches[i - 1]['city']['id'],
                sorted_matches[i]['city']['id'],
                flight_prices
            )

        # Accommodation costs (simplified)
        accommodation_cost = 0.0
        for i, match in enumerate(sorted_matches):
            nights = 1  # At least one night per match
            if i < len(sorted_matches) - 1:
                d1 = datetime.fromisoformat(match['kickoff'].split('T')[0])
                d2 = datetime.fromisoformat(sorted_matches[i + 1]['kickoff'].split('T')[0])
                nights = max(1, (d2 - d1).days)
            accommodation_cost += nights * match['city']['accommodationPerNight']

        return ticket_cost + flight_cost + accommodation_cost
