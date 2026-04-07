import pytest
from app.strategies.nearest_neighbour_strategy import NearestNeighbourStrategy


class TestNearestNeighbourStrategy:
    """
    NearestNeighbourStrategyTest — YOUR TASK #4

    ============================================================
    WHAT YOU NEED TO IMPLEMENT:
    ============================================================

    Write unit tests for the NearestNeighbourStrategy.
    Each test has a TODO comment explaining what to test.

    """

    def setup_method(self):
        self.strategy = NearestNeighbourStrategy()

    def test_happy_path_returns_valid_route(self):
        """Should return a valid route for multiple matches (happy path)"""
        # TODO: Implement test (YOUR TASK #4)
        # Arrange: Create an array of matches across different cities and dates
        # Act: Call self.strategy.optimise(matches)
        # Assert: Verify the result has stops, totalDistance > 0, and strategy = 'nearest-neighbour'
   
        matches = [
            {
                "id": "match-1",
                "kickoff": "2026-06-11T17:00:00Z",
                "city": {
                    "name": "Mexico City",
                    "latitude": 19.4326,
                    "longitude": -99.1332
                }
            },
            {
                "id": "match-2",
                "kickoff": "2026-06-12T19:00:00Z",
                "city": {
                    "name": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060
                }
            }
        ]

        result = self.strategy.optimise(matches)

        assert "stops" in result
        assert len(result["stops"]) >=1
        assert result["totalDistance"] > 0
        assert result["strategy"] == "nearest-neighbour"
        

    def test_empty_matches_returns_empty_route(self):
        """Should return an empty route for empty matches"""
        # TODO: Implement test (YOUR TASK #4)
        # Arrange: Create an empty array of matches
        # Act: Call self.strategy.optimise([])
        # Assert: Verify the result has empty stops and totalDistance = 0
        
        matches = []
        
        result = self.strategy.optimise(matches)

        assert result["stops"] == []
        assert result["totalDistance"] == 0
        assert result["strategy"] == "nearest-neighbour"

    def test_single_match_returns_zero_distance(self):
        """Should return zero distance for a single match"""
        # TODO: Implement test (YOUR TASK #4)
        # Arrange: Create an array with a single match
        # Act: Call self.strategy.optimise(matches)
        # Assert: Verify totalDistance = 0 and len(stops) = 1
        
        matches = [
            {
                "id": "match-1",
                "kickoff": "2026-06-11T17:00:00Z",
                "city": {
                    "name": "Mexico City",
                    "latitude": 19.4326,
                    "longitude": -99.1332
                }
            }
        ]
        
        result = self.strategy.optimise(matches)
        
        assert result["totalDistance"] == 0
        assert len(result["stops"]) == 1
    
        
        
