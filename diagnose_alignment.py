#!/usr/bin/env python3
"""Diagnostic script to test slope map alignment at known locations."""

import numpy as np
from src.dem import load_dem_for_scottish_highlands, get_cell_size_meters
from src.slope import calculate_slope


def get_slope_at_coord(slopes: np.ndarray, bounds: tuple, lat: float, lon: float) -> float:
    """Get slope value at a specific coordinate."""
    west, south, east, north = bounds

    # Convert lat/lon to array indices
    height, width = slopes.shape

    # Fractional position in the bounds
    x_frac = (lon - west) / (east - west)
    y_frac = (north - lat) / (north - south)  # Note: north is at row 0

    # Convert to pixel indices
    col = int(x_frac * width)
    row = int(y_frac * height)

    # Clamp to valid range
    col = max(0, min(width - 1, col))
    row = max(0, min(height - 1, row))

    return slopes[row, col], row, col


def main():
    print("Loading DEM data...")
    dem = load_dem_for_scottish_highlands()

    center_lat = (dem.bounds[1] + dem.bounds[3]) / 2
    cell_size = get_cell_size_meters(dem.resolution, center_lat)

    print("Calculating slopes...")
    slopes = calculate_slope(dem.elevation, cell_size)

    print(f"\nDEM bounds: {dem.bounds}")
    print(f"DEM shape: {dem.elevation.shape}")
    print(f"Resolution: {dem.resolution} degrees ({cell_size:.1f} meters)")

    # Known landmarks in the Cairngorms with distinctive terrain
    # These should have steep slopes nearby
    test_points = [
        # (name, lat, lon, expected terrain description)
        ("Cairn Gorm summit", 57.1167, -3.6431, "Should be on plateau, moderate slopes nearby"),
        ("Coire an t-Sneachda headwall", 57.1089, -3.6542, "Very steep cliffs - should show high slope"),
        ("Loch Avon", 57.0983, -3.5750, "Loch surrounded by steep corrie walls"),
        ("Ben Macdui summit", 57.0703, -3.6689, "Plateau summit, gentler slopes"),
        ("Lurcher's Crag", 57.1000, -3.7167, "Steep crag - should show high slope"),
        ("Coire an Lochain headwall", 57.1050, -3.6850, "Steep cliffs"),
    ]

    print("\n" + "="*80)
    print("ALIGNMENT TEST - Checking slope values at known locations")
    print("="*80)

    for name, lat, lon, description in test_points:
        slope_val, row, col = get_slope_at_coord(slopes, dem.bounds, lat, lon)
        elev_val = dem.elevation[row, col]

        print(f"\n{name}")
        print(f"  Coordinates: {lat:.4f}°N, {lon:.4f}°W")
        print(f"  Pixel index: row={row}, col={col}")
        print(f"  Elevation: {elev_val:.0f}m")
        print(f"  Slope angle: {slope_val:.1f}°")
        print(f"  Expected: {description}")

        # Sample nearby area to find max slope
        r_start, r_end = max(0, row-50), min(slopes.shape[0], row+50)
        c_start, c_end = max(0, col-50), min(slopes.shape[1], col+50)
        local_slopes = slopes[r_start:r_end, c_start:c_end]
        print(f"  Max slope within ~1.5km: {np.nanmax(local_slopes):.1f}°")

    # Test for systematic offset by checking if steep terrain is consistently offset
    print("\n" + "="*80)
    print("OFFSET DETECTION TEST")
    print("="*80)

    # Find the steepest point in the entire dataset
    steep_row, steep_col = np.unravel_index(np.nanargmax(slopes), slopes.shape)
    steep_slope = slopes[steep_row, steep_col]
    steep_elev = dem.elevation[steep_row, steep_col]

    # Convert back to coordinates
    west, south, east, north = dem.bounds
    height, width = slopes.shape
    steep_lon = west + (steep_col / width) * (east - west)
    steep_lat = north - (steep_row / height) * (north - south)

    print(f"\nSteepest point in dataset:")
    print(f"  Coordinates: {steep_lat:.4f}°N, {steep_lon:.4f}°W")
    print(f"  Slope: {steep_slope:.1f}°")
    print(f"  Elevation: {steep_elev:.0f}m")
    print(f"\nCheck this coordinate on the map - the steep terrain overlay")
    print(f"should align with visible cliffs/steep terrain on the base map.")


def test_offset():
    """Test if there's a systematic north-south offset."""
    print("\n" + "="*80)
    print("SYSTEMATIC OFFSET TEST")
    print("="*80)

    dem = load_dem_for_scottish_highlands()
    center_lat = (dem.bounds[1] + dem.bounds[3]) / 2
    cell_size = get_cell_size_meters(dem.resolution, center_lat)
    slopes = calculate_slope(dem.elevation, cell_size)

    # Coire an t-Sneachda is a known steep cliff at approximately:
    # 57.1089°N, -3.6542°W
    # Search in a grid around this location to find where the steepest slopes actually are

    base_lat, base_lon = 57.1089, -3.6542

    print(f"\nSearching for steep terrain near Coire an t-Sneachda ({base_lat}°N, {base_lon}°W)")
    print("Testing offsets from -0.02° to +0.02° in latitude (~2.2km)")

    best_offset = 0
    best_slope = 0

    for offset_deg in np.arange(-0.02, 0.021, 0.001):
        test_lat = base_lat + offset_deg
        slope_val, _, _ = get_slope_at_coord(slopes, dem.bounds, test_lat, base_lon)
        if slope_val > best_slope:
            best_slope = slope_val
            best_offset = offset_deg

        if abs(offset_deg) < 0.0001 or abs(offset_deg - 0.01) < 0.0001 or abs(offset_deg + 0.01) < 0.0001:
            offset_m = offset_deg * 111000
            print(f"  Offset {offset_deg:+.3f}° ({offset_m:+.0f}m): slope = {slope_val:.1f}°")

    offset_m = best_offset * 111000
    print(f"\n  Best match: offset {best_offset:+.3f}° ({offset_m:+.0f}m) with slope = {best_slope:.1f}°")

    if abs(best_offset) > 0.005:  # More than ~500m offset
        print(f"\n  WARNING: Significant offset detected!")
        print(f"  The slope data appears to be shifted {offset_m:.0f}m {'NORTH' if best_offset > 0 else 'SOUTH'}")
        print(f"  relative to where the steep terrain should be.")


if __name__ == "__main__":
    main()
    test_offset()
