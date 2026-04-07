from datetime import datetime
from typing import Optional
from app.strategies.route_strategy import BudgetResult, CostBreakdown


class CostCalculator:
    """
    CostCalculator — YOUR TASK #5

    ============================================================
    WHAT YOU NEED TO IMPLEMENT:
    ============================================================

    The calculate method should:
    1. Calculate ticket costs (sum of ticketPrice for all matches)
    2. Calculate flight costs (between consecutive cities + from origin)
    3. Calculate accommodation costs (nights × city's accommodationPerNight rate)
    4. Check feasibility (total ≤ budget AND visits USA, Mexico, Canada)
    5. Return suggestions if not feasible

    ============================================================
    HELPER METHODS PROVIDED:
    ============================================================

    The helper methods below are already implemented for you:
    - get_flight_price(): Look up flight price between two cities
    - calculate_nights_between(): Calculate nights between two dates
    - get_countries_visited(): Get list of unique countries from matches
    - get_missing_countries(): Check which required countries are missing
    - generate_suggestions(): Create cost-saving suggestions

    """

    REQUIRED_COUNTRIES = ['USA', 'Mexico', 'Canada']

    def calculate(
        self,
        matches: list,
        budget: float,
        origin_city_id: str,
        flight_prices: list
    ) -> BudgetResult:
        """
        Calculate the total cost of a trip and check if it's within budget.

        Args:
            matches: List of match dicts the user wants to attend (sorted by date)
            budget: The user's maximum budget in USD
            origin_city_id: The city where the user starts their trip
            flight_prices: All available flight prices between cities

        Returns:
            BudgetResult dict containing feasibility, costs, and suggestions
        """
        # TODO: Implement cost calculation (YOUR TASK #5)
        #
        # Pseudocode:
        # 1. Calculate ticket costs:
        #    - Sum of match['ticketPrice'] for all matches
        #
        # 2. Calculate flight costs:
        #    - From origin_city_id to first match's city
        #    - Between each consecutive match city (if different)
        #    - Use get_flight_price() helper to look up prices
        #
        # 3. Calculate accommodation costs:
        #    - For each city visited, calculate nights stayed
        #    - Use calculate_nights_between() for dates
        #    - Multiply nights by city's accommodationPerNight
        #
        # 4. Build CostBreakdown with all costs and total
        #
        # 5. Check country constraint:
        #    - Use get_countries_visited() and get_missing_countries()
        #    - If missing countries, set feasible = False
        #
        # 6. Check budget constraint:
        #    - If total > budget, set feasible = False
        #    - Set minimumBudgetRequired = total
        #
        # 7. Generate suggestions if not feasible:
        #    - Use generate_suggestions() helper
        #
        # 8. Return BudgetResult with all results


        # 1. Calculate ticket costs
        ticket_total = sum(match.get('ticketPrice', 0) for match in matches)

        # 2. Calculate flight costs
        flight_total = 0
        current_loc = origin_city_id
        for match in matches:
            dest_city = match.get('cityId') or match.get('city_id')
            flight_total += self.get_flight_price(current_loc, dest_city, flight_prices)
            current_loc = dest_city
        
        # 3. Calculate accommodation costs
        accommodation_total = 0
        if matches:
            first_city = matches[0].get('city', {})
            accommodation_total += first_city.get('accommodationPerNight', 0) or first_city.get('accommodation_per_night', 0)
            
            for i in range(len(matches) - 1):
                nights = self.calculate_nights_between(matches[i]['kickoff'], matches[i+1]['kickoff'])
                city_info = matches[i].get('city', {})
                rate = city_info.get('accommodationPerNight', 0) or city_info.get('accommodation_per_night', 0)
                accommodation_total += (nights * rate)

        # 4. Build Cost Breakdown
        total_cost = ticket_total + flight_total + accommodation_total

        # --- 5. FIXED COUNTRY CHECK (DO NOT USE HELPER HERE) ---
        visited_set = set()
        for m in matches:
            # Look for country in nested city object OR top level
            city_data = m.get('city', {})
            c_name = city_data.get('country') if isinstance(city_data, dict) else m.get('country')
            
            if c_name:
                c_clean = str(c_name).strip().lower()
                if 'usa' in c_clean or 'united states' in c_clean:
                    visited_set.add('USA')
                elif 'mexico' in c_clean:
                    visited_set.add('Mexico')
                elif 'canada' in c_clean:
                    visited_set.add('Canada')

        # Calculate missing based on our cleaned set
        missing = [c for c in self.REQUIRED_COUNTRIES if c not in visited_set]
        
        # 6. Check feasibility
        is_under_budget = total_cost <= budget
        feasible = is_under_budget and (not missing)

        # 7. Suggestions
        suggestions = self.generate_suggestions(matches, total_cost, budget) if not feasible else []

        # 8. Final Return
        return {
            "feasible": feasible,
            "breakdown": {
                "tickets": ticket_total,
                "flights": flight_total,
                "accommodation": accommodation_total,
                "total": total_cost
            },
            "totalCost": round(total_cost, 2),
            "minimumBudgetRequired": round(total_cost, 2),
            "missingCountries": missing,
            "suggestions": suggestions
        }


       
   

    # ============================================================
    # HELPER METHODS (Already implemented for you)
    # ============================================================

    def get_flight_price(
        self,
        from_city_id: str,
        to_city_id: str,
        flight_prices: list
    ) -> float:
        """
        Look up the flight price between two cities.
        Returns an estimated price if no direct flight exists.
        """
        if from_city_id == to_city_id:
            return 0

        for fp in flight_prices:
            if fp['from_city_id'] == from_city_id and fp['to_city_id'] == to_city_id:
                return fp['price']

        # If no direct flight, estimate based on average
        if flight_prices:
            avg_price = sum(fp['price'] for fp in flight_prices) / len(flight_prices)
            return avg_price * 1.2  # 20% markup for indirect routes
        return 300 * 1.2

    def calculate_nights_between(self, date1: str, date2: str) -> int:
        """Calculate the number of nights between two dates."""
        d1 = datetime.fromisoformat(date1.split('T')[0])
        d2 = datetime.fromisoformat(date2.split('T')[0])
        return max(0, (d2 - d1).days)

    def get_countries_visited(self, matches: list) -> list:
        """Get list of unique countries visited from matches."""
        countries = set()
        for match in matches:
            countries.add(match['city']['country'])
        return list(countries)

    def get_missing_countries(self, countries_visited: list) -> list:
        """Check which required countries (USA, Mexico, Canada) are missing."""
        return [c for c in self.REQUIRED_COUNTRIES if c not in countries_visited]

    def generate_suggestions(
        self,
        matches: list,
        total: float,
        budget: float
    ) -> list:
        """Generate cost-saving suggestions when budget is exceeded."""
        suggestions = []
        overage = total - budget

        if len(matches) > 5:
            most_expensive = max(matches, key=lambda m: m['ticketPrice'])
            suggestions.append(
                f"Consider removing the {most_expensive['homeTeam']['name']} vs "
                f"{most_expensive['awayTeam']['name']} match to save ${most_expensive['ticketPrice']}"
            )

        suggestions.append(
            f"You are ${overage:.0f} over budget. Consider reducing the number of matches."
        )

        return suggestions
