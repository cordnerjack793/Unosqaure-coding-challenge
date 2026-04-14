from app.strategies.route_strategy import RouteStrategy, build_route
from app.utils.haversine import calculate_distance


class NearestNeighbourStrategy(RouteStrategy):
    """
    NearestNeighbourStrategy — YOUR TASK #3

    Implement a smarter route optimisation using the nearest-neighbour heuristic.
    The idea: when you have multiple matches on the same day (or close dates),
    choose the one that's geographically closest to where you currently are.

    This should produce shorter total distances than DateOnlyStrategy.
    """
        # Pseudocode:
        # 1. Sort all matches by kickoff date
        # 2. Group matches that fall on the same day
        #    Hint: match['kickoff'].split('T')[0] gives the date string
        # 3. Start with the first match chronologically — this is your starting city
        # 4. For each subsequent day group:
        #    a. If only one match that day → add it to the route
        #    b. If multiple matches that day → pick the one whose city is closest
        #       to your current position (use calculate_distance)
        # 5. Track your "current city" as you go — update it after each match
        # 6. Return build_route(ordered_matches, 'nearest-neighbour')
        #
        # Helper you'll need:
        #   calculate_distance(lat1, lon1, lat2, lon2) → returns distance in km
        #
        # Example:
        #   dist = calculate_distance(
        #       current_city['latitude'], current_city['longitude'],
        #       candidate['city']['latitude'], candidate['city']['longitude']
        #   )
        #
        # Tips:
        # - You can use itertools.groupby or a dict to group by date
        # - Don't forget to handle the case where there's only one match on a day
        # - The first match in chronological order should always be your starting point

    def optimise(self, matches: list) -> dict:

        # 1. Sort matches chronologically
        matches.sort(key=lambda m: m['kickoff'])
        
        # 2. Group matches that fall on the same day
        grouped_by_date = {}
        for m in matches:
            date_key = m['kickoff'].split('T')[0]
            if date_key not in grouped_by_date:
                grouped_by_date[date_key] = []
            grouped_by_date[date_key].append(m)
            
        # sort keys by the date they are played   
        sorted_dates = sorted(grouped_by_date.keys())
        
        # 3. Start with the first match chronologically — this is your starting city
        first_date = sorted_dates[0]
        first_match = grouped_by_date[first_date][0]
        
        ordered_matches = [first_match]
        current_city = first_match['city']
            
        # 4. For each subsequent day group:
        for date in sorted_dates[1:]:
            day_group = grouped_by_date[date]

            # a. If only one match that day → add it to the route
            if len(day_group) == 1:
                next_match = day_group[0]
            
            # b. If multiple matches that day → pick the one whose city is closest
            else:
                next_match = min(day_group, key=lambda m: calculate_distance(
                    current_city['latitude'],
                    current_city['longitude'],
                    m['city']['latitude'],
                    m['city']['longitude']
                ))

            # 5. Track your "current city" as you go — update it after each match
            ordered_matches.append(next_match)
            current_city = next_match['city']

        # 6. Return the formatted route
        return build_route(ordered_matches, 'nearest-neighbour')