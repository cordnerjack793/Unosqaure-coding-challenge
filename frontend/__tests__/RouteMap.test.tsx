import { render, screen } from '@testing-library/react';
import RouteMap from '../src/components/RouteMap';
import { OptimisedRoute } from '../src/types';

// ============================================================
// Mock react-leaflet to prevent the "export" SyntaxError
// ============================================================
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children }: any) => <div data-testid="map-container">{children}</div>,
  TileLayer: () => null,
  Marker: ({ children }: any) => <div data-testid="marker">{children}</div>,
  Popup: ({ children }: any) => <div data-testid="popup">{children}</div>,
  Polyline: () => null,
}));

jest.mock('leaflet', () => ({
  DivIcon: jest.fn(),
}));

describe('RouteMap', () => {
  it('should render placeholder message when route is null', () => {
    // TODO: Implement test
    // Arrange: Render RouteMap with route={null}
    // Assert: Verify placeholder message is displayed

    // Arrange: Render RouteMap with route={null}
    render(<RouteMap route={null} originCity={null} />);

    // Assert: Verify placeholder message is displayed
    const title = screen.queryByText(/Route Map/i);
    const instruction = screen.queryByText(/Validate a route to see it displayed on the map/i);
    
    expect(title).not.toBeNull();
    expect(instruction).not.toBeNull();
  });

  it('should render a map container when route is provided', () => {
    // TODO: Implement test
    // Arrange: Create a mock route with stops
    // Act: Render RouteMap with the route
    // Assert: Verify MapContainer is rendered

    // 1. Arrange: Create a mock route with stops
    const mockRoute = {
      stops: [
        {
          stopNumber: 1,
          city: { id: 'atl', name: 'Atlanta', latitude: 33.7, longitude: -84.3 },
          match: { id: 'm1', homeTeam: { name: 'USA' }, awayTeam: { name: 'Wales' }, kickoff: '2026-06-12T18:00:00Z' }
        }
      ],
      totalCost: 150,
      feasible: true,
      countriesVisited: ['USA']
    } as any;

    // 2. Act: Render RouteMap with the route
    render(<RouteMap route={mockRoute} originCity={null} />);

    // 3. Assert: Verify MapContainer is rendered
    const mapElement = screen.queryByTestId('map-container');
    expect(mapElement).not.toBeNull();
    
    // Also verify the "Select matches" placeholder is no longer visible
    const placeholder = screen.queryByText(/Validate a route/i);
    expect(placeholder).toBeNull();
  });

  it('should render a marker for each stop in the route', () => {
    // TODO: Implement test
    // Arrange: Create a mock route with 3 stops
    // Act: Render RouteMap with the route
    // Assert: Verify 3 markers are rendered

    // 1. Arrange: Create a mock route with 3 stops in 3 DIFFERENT cities
    const mockRoute = {
      stops: [
        { 
          stopNumber: 1, 
          city: { id: 'city-1', name: 'Atlanta', latitude: 33.7, longitude: -84.3 },
          match: { id: 'm1', homeTeam: { name: 'USA' }, awayTeam: { name: 'Wales' } }
        },
        { 
          stopNumber: 2, 
          city: { id: 'city-2', name: 'Mexico City', latitude: 19.4, longitude: -99.1 },
          match: { id: 'm2', homeTeam: { name: 'Mexico' }, awayTeam: { name: 'Poland' } }
        },
        { 
          stopNumber: 3, 
          city: { id: 'city-3', name: 'Toronto', latitude: 43.6, longitude: -79.3 },
          match: { id: 'm3', homeTeam: { name: 'Canada' }, awayTeam: { name: 'Nigeria' } }
        }
      ],
      totalCost: 300,
      feasible: true,
      countriesVisited: ['USA', 'Mexico', 'Canada']
    } as any;

    // 2. Act: Render
    render(<RouteMap route={mockRoute} originCity={null} />);

    // 3. Assert: Verify 3 markers are rendered
    // Using 'marker' to match the data-testid defined in the jest.mock above
    const markers = screen.queryAllByTestId('marker');
    
    expect(markers.length).toBe(3);
  });

  it('should handle route with empty stops array', () => {
    // TODO: Implement test
    // Arrange: Create a mock route with empty stops array
    // Act: Render RouteMap with the route
    // Assert: Verify component handles edge case gracefully

    const emptyRoute = { stops: [] } as any;
    render(<RouteMap route={emptyRoute} originCity={null} />);
    
    expect(screen.queryByTestId('map-container')).not.toBeNull();
    expect(screen.queryAllByTestId('marker').length).toBe(0);
  });
});
it('should handle route with empty stops array', () => {
    // TODO: Implement test
    // Arrange: Create a mock route with empty stops array
    const emptyRoute = {
      stops: [],
      totalCost: 0,
      feasible: true,
      countriesVisited: []
    } as any;

    // Act: Render RouteMap with the route
    render(<RouteMap route={emptyRoute} originCity={null} />);

    // Assert: Verify component handles edge case gracefully
    // The map should still exist, but with no markers drawn on it
    expect(screen.queryByTestId('map-container')).not.toBeNull();
    expect(screen.queryAllByTestId('marker').length).toBe(0);
  });
