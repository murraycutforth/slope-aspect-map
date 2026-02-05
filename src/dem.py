"""DEM data fetching and loading using SRTM elevation data."""

import os
import numpy as np
from dataclasses import dataclass
from typing import Tuple
import tempfile

import elevation
import rasterio


@dataclass
class DEMData:
    """Container for DEM data and metadata."""
    elevation: np.ndarray  # 2D array of elevation values in meters
    bounds: Tuple[float, float, float, float]  # (west, south, east, north)
    resolution: float  # Resolution in degrees


def get_cell_size_meters(resolution_degrees: float, latitude: float) -> float:
    """
    Convert resolution from degrees to approximate meters.

    At a given latitude, the east-west distance per degree is reduced by cos(lat).
    We return an average cell size accounting for this.

    Args:
        resolution_degrees: Cell size in degrees
        latitude: Latitude in degrees

    Returns:
        Approximate cell size in meters
    """
    # Meters per degree at equator
    meters_per_degree_lat = 111320  # roughly constant
    meters_per_degree_lon = 111320 * np.cos(np.radians(latitude))

    # Average of lat and lon cell sizes
    cell_size_lat = resolution_degrees * meters_per_degree_lat
    cell_size_lon = resolution_degrees * meters_per_degree_lon

    return (cell_size_lat + cell_size_lon) / 2


def load_dem(bounds: Tuple[float, float, float, float],
             output_dir: str = None) -> DEMData:
    """
    Load DEM data for the specified bounds using SRTM data.

    Args:
        bounds: (west, south, east, north) in degrees
        output_dir: Directory to cache downloaded tiles (default: temp dir)

    Returns:
        DEMData object with elevation array and metadata
    """
    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), 'srtm_cache')
    os.makedirs(output_dir, exist_ok=True)

    # Create output file path
    output_file = os.path.join(output_dir, 'dem.tif')

    # Download/clip SRTM data to bounds
    west, south, east, north = bounds
    elevation.clip(bounds=(west, south, east, north), output=output_file, max_download_tiles=15)

    # Load the raster data
    with rasterio.open(output_file) as src:
        elev_data = src.read(1)  # Read first band
        transform = src.transform
        resolution = transform[0]  # Cell size in degrees

        # Get actual bounds from the raster file (not the requested bounds)
        # rasterio bounds are (left, bottom, right, top) = (west, south, east, north)
        actual_bounds = src.bounds
        actual_bounds = (actual_bounds.left, actual_bounds.bottom,
                         actual_bounds.right, actual_bounds.top)

    # Handle nodata values
    elev_data = elev_data.astype(np.float32)
    elev_data[elev_data < -1000] = np.nan  # SRTM nodata is typically -32768

    return DEMData(
        elevation=elev_data,
        bounds=actual_bounds,  # Use actual bounds from raster, not requested bounds
        resolution=abs(resolution)
    )


def load_dem_for_scottish_highlands(output_dir: str = None) -> DEMData:
    """
    Load DEM data for the Scottish Highlands region.

    Covers approximately lat 56.0-58.0, lon -5.5 to -2.8
    Focused on central Highlands and Cairngorms.

    Args:
        output_dir: Directory to cache downloaded tiles

    Returns:
        DEMData object for Scottish Highlands
    """
    # Scottish Highlands bounding box (shifted east to cover Cairngorms)
    bounds = (-5.5, 56.0, -2.8, 58.0)
    return load_dem(bounds, output_dir)
