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
        ticket_total = sum(float(m.get('ticketPrice', 0)) for m in matches)

        # 2. Calculate flight costs
        flight_total = 0
        starting_location = str(origin_city_id)
        
        for m in matches:
            # Gets the next city on the list
            next_city = str((m.get('city')).get('id'))
            
            # Gets the total flight cost for all flights
            flight_total += self.get_flight_price(starting_location, next_city, flight_prices)
            
            # Update current location to move to the next city in the sequence
            starting_location = next_city
            
            
        # 3. Calculate accommodation costs:
        accommodation_total = 0
        for i in range(len(matches)):
            current_match = matches[i]
            
            # Get the nightly rate for the current city
            current_city = current_match.get('city')
            nightly_rate = float(current_city.get('accommodationPerNight'))
            
            # If there is another match after this one
            if i < len(matches) - 1:
                next_match = matches[i+1]
                
                # Get kickoffs for both matches to find the gap between the matches (number of nights)
                current_kickoff = current_match.get('kickoff')
                next_kickoff = next_match.get('kickoff')
        
              
                # Get the total price for the accommidation
                accommodation_total += (self.calculate_nights_between(current_kickoff, next_kickoff) * nightly_rate)
            else:
                # Add this so it matches what is on the 'best_value_finder.pt'
                # It is staying over after the last night before going home
                accommodation_total += (1 * nightly_rate)
                

        # 4. Build CostBreakdown with all costs and total
        breakdown = CostBreakdown(
            tickets=round(ticket_total),
            flights=round(flight_total),
            accommodation=round(accommodation_total),
            total=round(ticket_total+flight_total+accommodation_total)
        )


        feasible = True
        # 5. Check country constraint
        visited = self.get_countries_visited(matches)
        missing = self.get_missing_countries(visited)
        
        if len(missing) > 0:
            feasible = False

        # 6. Check budget constraint
        if breakdown['total'] > budget:
            feasible = False

        # 7. Generate suggestions if not feasible:
        suggestions = ""
        if not feasible:
            suggestions = self.generate_suggestions(budget, breakdown['total'], missing, matches)

        # 8. Return BudgetResult with all results
        return {
            "feasible": feasible,
            "costBreakdown": breakdown,
            "countriesVisited": visited,
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
