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

    def optimise(self, matches: list) -> dict:
            if not matches:
                return build_route([], 'nearest-neighbour')

            # 1. Sort all matches by kickoff date
            matches.sort(key=lambda m: m['kickoff'])

            # 2. Group matches that fall on the same day
            matches_by_day = {}
            for match in matches:
                date = match['kickoff'].split('T')[0]
                
                # If the "folder" for this date doesn't exist, create it
                if date not in matches_by_day:
                    matches_by_day[date] = []
                    
                # Now we know it exists, so we can safely add the match
                matches_by_day[date].append(match)
                
            # 3. Start with the first match chronologically
            first_match = matches[0]
            ordered_matches = [first_match]
            current_match = first_match
            
           # 4. Process each day group chronologically
            sorted_dates = sorted(matches_by_day.keys())
            
            for date in sorted_dates:
                # Create a copy of the day's matches to safely iterate
                day_group = list(matches_by_day[date])
                
                while day_group:
                    # 4a & 4b: Find the best next match for this day
                    # If only one match remains (4a), min() simply selects it.
                    # If multiple matches remain (4b), min() picks the one with the shortest geographic distance from your current position.
                    next_match = min(day_group, key=lambda m: calculate_distance(
                        current_match['city']['latitude'], 
                        current_match['city']['longitude'],
                        m['city']['latitude'], 
                        m['city']['longitude']
                    ))
                    
                    # 5. Logic to add the match and update position.
                    if next_match not in ordered_matches:
                        ordered_matches.append(next_match)
                        current_match = next_match
                    
                    # Remove from the local group so the loop eventually finishes
                    day_group.remove(next_match)


            # 6. Return build_route(ordered_matches, 'nearest-neighbour')
            return build_route(ordered_matches, 'nearest-neighbour')
        
        
        
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
    