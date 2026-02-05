"""Slope calculation from elevation data."""

import numpy as np


def calculate_slope(elevation: np.ndarray, cell_size: float) -> np.ndarray:
    """
    Calculate slope angle in degrees from elevation data.

    Args:
        elevation: 2D numpy array of elevation values in meters
        cell_size: Size of each grid cell in meters

    Returns:
        2D numpy array of slope angles in degrees (0-90)
    """
    # Calculate gradients in both directions
    # gradient returns rate of change per cell, so divide by cell_size for actual gradient
    dz_dy, dz_dx = np.gradient(elevation, cell_size)

    # Calculate slope magnitude
    # slope = sqrt(dz_dx^2 + dz_dy^2)
    gradient_magnitude = np.sqrt(dz_dx**2 + dz_dy**2)

    # Convert to angle in degrees
    # arctan gives angle where tan(angle) = rise/run = gradient
    slope_radians = np.arctan(gradient_magnitude)
    slope_degrees = np.degrees(slope_radians)

    return slope_degrees
