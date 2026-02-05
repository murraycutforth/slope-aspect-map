"""Tests for slope calculation module."""

import numpy as np
import pytest
from src.slope import calculate_slope


class TestSlopeCalculation:
    """Test slope calculation on synthetic data."""

    def test_flat_plane_has_zero_slope(self):
        """A flat plane should have 0 degrees slope everywhere."""
        elevation = np.ones((10, 10)) * 100  # Flat at 100m
        cell_size = 30  # 30m resolution

        slope = calculate_slope(elevation, cell_size)

        np.testing.assert_array_almost_equal(slope, 0, decimal=5)

    def test_45_degree_slope(self):
        """A plane with rise = run should have 45 degree slope."""
        # Create a plane tilted at 45 degrees in the x direction
        # rise/run = 1 means for every meter horizontally, we go up 1 meter
        cell_size = 30  # 30m cells
        elevation = np.zeros((10, 10))
        for i in range(10):
            elevation[:, i] = i * cell_size  # Each column is cell_size meters higher

        slope = calculate_slope(elevation, cell_size)

        # Interior points should be 45 degrees (edges may differ due to gradient boundary)
        interior = slope[1:-1, 1:-1]
        np.testing.assert_array_almost_equal(interior, 45, decimal=1)

    def test_steep_slope(self):
        """Test a steep slope (approximately 63.4 degrees, where rise = 2*run)."""
        cell_size = 30
        elevation = np.zeros((10, 10))
        for i in range(10):
            elevation[:, i] = i * cell_size * 2  # Rise is 2x the run

        slope = calculate_slope(elevation, cell_size)

        # arctan(2) ≈ 63.43 degrees
        expected_angle = np.degrees(np.arctan(2))
        interior = slope[1:-1, 1:-1]
        np.testing.assert_array_almost_equal(interior, expected_angle, decimal=1)

    def test_output_shape_matches_input(self):
        """Output slope array should have same shape as input elevation."""
        elevation = np.random.rand(50, 100) * 1000
        cell_size = 30

        slope = calculate_slope(elevation, cell_size)

        assert slope.shape == elevation.shape

    def test_slope_is_non_negative(self):
        """Slope angles should always be non-negative."""
        elevation = np.random.rand(20, 20) * 500
        cell_size = 30

        slope = calculate_slope(elevation, cell_size)

        assert np.all(slope >= 0)

    def test_slope_max_is_reasonable(self):
        """Slope should not exceed 90 degrees."""
        # Even with extreme gradients, slope should cap at 90
        elevation = np.random.rand(20, 20) * 1000
        cell_size = 30

        slope = calculate_slope(elevation, cell_size)

        assert np.all(slope <= 90)

    def test_diagonal_slope(self):
        """Test slope calculation when tilted diagonally."""
        cell_size = 30
        elevation = np.zeros((10, 10))
        # Tilt in both x and y: each contributes 1/sqrt(2) to make total gradient = 1
        for i in range(10):
            for j in range(10):
                elevation[i, j] = (i + j) * cell_size / np.sqrt(2)

        slope = calculate_slope(elevation, cell_size)

        # Combined gradient magnitude should give 45 degrees
        interior = slope[2:-2, 2:-2]
        np.testing.assert_array_almost_equal(interior, 45, decimal=0)
