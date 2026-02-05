"""Tests for DEM data loading module."""

import numpy as np
import pytest
from src.dem import DEMData, load_dem, get_cell_size_meters


class TestDEMData:
    """Test DEMData dataclass."""

    def test_dem_data_creation(self):
        """DEMData should store elevation array and metadata."""
        elevation = np.random.rand(100, 100) * 1000
        bounds = (-5.0, 56.5, -4.5, 57.0)  # west, south, east, north
        resolution = 0.000833  # approximately 90m in degrees

        dem = DEMData(elevation=elevation, bounds=bounds, resolution=resolution)

        assert dem.elevation.shape == (100, 100)
        assert dem.bounds == bounds
        assert dem.resolution == resolution

    def test_dem_data_bounds_order(self):
        """Bounds should be (west, south, east, north)."""
        elevation = np.zeros((10, 10))
        bounds = (-6.5, 56.0, -3.5, 58.0)

        dem = DEMData(elevation=elevation, bounds=bounds, resolution=0.001)

        west, south, east, north = dem.bounds
        assert west < east
        assert south < north


class TestCellSizeCalculation:
    """Test conversion from degrees to meters."""

    def test_cell_size_at_equator(self):
        """At equator, 1 degree ≈ 111km."""
        resolution_degrees = 1 / 1200  # 3 arc-second SRTM
        latitude = 0

        cell_size = get_cell_size_meters(resolution_degrees, latitude)

        # At equator, ~90m for 3 arc-second data
        assert 80 < cell_size < 100

    def test_cell_size_at_scottish_latitude(self):
        """At Scottish Highlands latitude (~57°N), cell size should be smaller in E-W."""
        resolution_degrees = 1 / 1200  # 3 arc-second
        latitude = 57

        cell_size = get_cell_size_meters(resolution_degrees, latitude)

        # At 57°N, cos(57°) ≈ 0.545, so E-W distance is about half
        # Average cell size should be somewhere between
        assert 50 < cell_size < 90

    def test_cell_size_increases_with_resolution(self):
        """Larger resolution value should give larger cell size."""
        latitude = 57

        small_res = get_cell_size_meters(1/1200, latitude)  # 3 arc-second
        large_res = get_cell_size_meters(1/120, latitude)   # 30 arc-second

        assert large_res > small_res


class TestDEMLoading:
    """Test DEM loading functionality."""

    def test_load_dem_returns_dem_data(self):
        """load_dem should return a DEMData object."""
        # Use a small test area
        bounds = (-5.0, 57.0, -4.9, 57.1)

        dem = load_dem(bounds)

        assert isinstance(dem, DEMData)
        assert dem.elevation is not None
        assert len(dem.bounds) == 4

    def test_elevation_values_reasonable(self):
        """Elevation values should be within reasonable range for Scotland."""
        bounds = (-5.0, 57.0, -4.9, 57.1)

        dem = load_dem(bounds)

        # Scotland elevations: sea level to ~1300m (Ben Nevis)
        # Allow some buffer for data artifacts
        assert np.nanmin(dem.elevation) >= -100
        assert np.nanmax(dem.elevation) <= 2000

    def test_dem_has_positive_resolution(self):
        """DEM resolution should be positive."""
        bounds = (-5.0, 57.0, -4.9, 57.1)

        dem = load_dem(bounds)

        assert dem.resolution > 0
