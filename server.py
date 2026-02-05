#!/usr/bin/env python3
"""Simple HTTP server to serve the slope angle map."""

import http.server
import socketserver
import os
import argparse
import webbrowser
from pathlib import Path


def generate_map():
    """Generate the slope map from DEM data."""
    print("Generating slope map...")

    from src.dem import load_dem_for_scottish_highlands, get_cell_size_meters
    from src.slope import calculate_slope
    from src.visualize import generate_scottish_highlands_map

    # Load DEM data
    print("Loading DEM data for Scottish Highlands...")
    dem = load_dem_for_scottish_highlands()
    print(f"  Elevation shape: {dem.elevation.shape}")
    print(f"  Bounds: {dem.bounds}")
    print(f"  Resolution: {dem.resolution} degrees")

    # Calculate cell size in meters
    center_lat = (dem.bounds[1] + dem.bounds[3]) / 2
    cell_size = get_cell_size_meters(dem.resolution, center_lat)
    print(f"  Cell size: {cell_size:.1f} meters")

    # Calculate slopes
    print("Calculating slope angles...")
    slopes = calculate_slope(dem.elevation, cell_size)
    print(f"  Slope range: {slopes[~np.isnan(slopes)].min():.1f}° to {slopes[~np.isnan(slopes)].max():.1f}°")

    # Generate map
    print("Generating Folium map...")
    generate_scottish_highlands_map(slopes, dem.bounds)
    print("Done!")


def run_server(port: int = 8000, regenerate: bool = False, open_browser: bool = True):
    """
    Run HTTP server to serve the map.

    Args:
        port: Port number to serve on
        regenerate: If True, regenerate the map before serving
        open_browser: If True, open the map in a web browser
    """
    map_file = 'scottish_highlands_slope_map.html'

    if regenerate or not os.path.exists(map_file):
        generate_map()

    # Change to project directory
    os.chdir(Path(__file__).parent)

    handler = http.server.SimpleHTTPRequestHandler

    # Allow port reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True

    # Try to find an available port
    for try_port in range(port, port + 10):
        try:
            httpd = socketserver.TCPServer(("", try_port), handler)
            port = try_port
            break
        except OSError as e:
            if try_port == port + 9:
                raise OSError(f"Could not find available port in range {port}-{port+9}") from e
            continue

    with httpd:
        url = f"http://localhost:{port}/{map_file}"
        print(f"\nServing at {url}")
        print("Press Ctrl+C to stop the server")

        if open_browser:
            webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == '__main__':
    import numpy as np  # Import here to avoid issues if not generating

    parser = argparse.ArgumentParser(description='Serve the Scottish Highlands slope angle map')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on (default: 8000)')
    parser.add_argument('--regenerate', action='store_true', help='Regenerate the map before serving')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')

    args = parser.parse_args()
    run_server(port=args.port, regenerate=args.regenerate, open_browser=not args.no_browser)
