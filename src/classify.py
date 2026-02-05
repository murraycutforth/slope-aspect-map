"""Avalanche risk classification based on slope angle."""

import numpy as np
from typing import Union, List

# Risk categories with slope thresholds in degrees
RISK_CATEGORIES = {
    'low': {'min': 0, 'max': 25, 'color': (0, 255, 0, 150)},           # Green
    'moderate': {'min': 25, 'max': 30, 'color': (255, 255, 0, 150)},   # Yellow
    'high': {'min': 30, 'max': 45, 'color': (255, 165, 0, 150)},       # Orange
    'very_high': {'min': 45, 'max': 60, 'color': (255, 0, 0, 150)},    # Red
    'extreme': {'min': 60, 'max': 90, 'color': (128, 0, 128, 150)},    # Purple
}


def classify_slope(slopes: np.ndarray) -> Union[np.ndarray, List[str]]:
    """
    Classify slope angles into avalanche risk categories.

    Args:
        slopes: Array of slope angles in degrees

    Returns:
        Array of risk category names ('low', 'moderate', 'high', 'very_high', 'extreme')
    """
    # Handle both 1D and 2D arrays
    original_shape = slopes.shape
    flat_slopes = slopes.flatten()

    categories = []
    for slope in flat_slopes:
        if slope < 25:
            categories.append('low')
        elif slope < 30:
            categories.append('moderate')
        elif slope < 45:
            categories.append('high')
        elif slope < 60:
            categories.append('very_high')
        else:
            categories.append('extreme')

    if len(original_shape) > 1:
        return np.array(categories).reshape(original_shape)
    return categories


def get_risk_color(category: str) -> tuple:
    """
    Get RGBA color tuple for a risk category.

    Args:
        category: Risk category name

    Returns:
        Tuple of (R, G, B, A) values (0-255)
    """
    return RISK_CATEGORIES[category]['color']


def slope_to_rgba(slopes: np.ndarray) -> np.ndarray:
    """
    Convert slope array to RGBA image array.

    Args:
        slopes: 2D array of slope angles in degrees

    Returns:
        3D array of shape (height, width, 4) with RGBA values
    """
    height, width = slopes.shape
    rgba = np.zeros((height, width, 4), dtype=np.uint8)

    # Create masks for each category
    low_mask = slopes < 25
    moderate_mask = (slopes >= 25) & (slopes < 30)
    high_mask = (slopes >= 30) & (slopes < 45)
    very_high_mask = (slopes >= 45) & (slopes < 60)
    extreme_mask = slopes >= 60

    # Apply colors
    rgba[low_mask] = RISK_CATEGORIES['low']['color']
    rgba[moderate_mask] = RISK_CATEGORIES['moderate']['color']
    rgba[high_mask] = RISK_CATEGORIES['high']['color']
    rgba[very_high_mask] = RISK_CATEGORIES['very_high']['color']
    rgba[extreme_mask] = RISK_CATEGORIES['extreme']['color']

    return rgba
