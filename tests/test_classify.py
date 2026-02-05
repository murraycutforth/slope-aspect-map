"""Tests for avalanche risk classification module."""

import numpy as np
import pytest
from src.classify import classify_slope, get_risk_color, RISK_CATEGORIES


class TestRiskClassification:
    """Test avalanche risk classification."""

    def test_low_risk_below_25_degrees(self):
        """Slopes below 25 degrees should be classified as low risk."""
        slopes = np.array([0, 10, 20, 24.9])

        categories = classify_slope(slopes)

        assert all(c == 'low' for c in categories)

    def test_moderate_risk_25_to_30_degrees(self):
        """Slopes between 25-30 degrees should be moderate risk."""
        slopes = np.array([25, 27, 29.9])

        categories = classify_slope(slopes)

        assert all(c == 'moderate' for c in categories)

    def test_high_risk_30_to_45_degrees(self):
        """Slopes between 30-45 degrees should be high risk (prime avalanche terrain)."""
        slopes = np.array([30, 35, 40, 44.9])

        categories = classify_slope(slopes)

        assert all(c == 'high' for c in categories)

    def test_very_high_risk_45_to_60_degrees(self):
        """Slopes between 45-60 degrees should be very high risk."""
        slopes = np.array([45, 50, 55, 59.9])

        categories = classify_slope(slopes)

        assert all(c == 'very_high' for c in categories)

    def test_extreme_risk_above_60_degrees(self):
        """Slopes above 60 degrees should be extreme risk."""
        slopes = np.array([60, 70, 80, 90])

        categories = classify_slope(slopes)

        assert all(c == 'extreme' for c in categories)

    def test_boundary_values(self):
        """Test exact boundary values."""
        # Boundaries: 25, 30, 45, 60
        assert classify_slope(np.array([24.99]))[0] == 'low'
        assert classify_slope(np.array([25.0]))[0] == 'moderate'
        assert classify_slope(np.array([29.99]))[0] == 'moderate'
        assert classify_slope(np.array([30.0]))[0] == 'high'
        assert classify_slope(np.array([44.99]))[0] == 'high'
        assert classify_slope(np.array([45.0]))[0] == 'very_high'
        assert classify_slope(np.array([59.99]))[0] == 'very_high'
        assert classify_slope(np.array([60.0]))[0] == 'extreme'


class TestColorMapping:
    """Test color mapping for risk categories."""

    def test_low_risk_is_green(self):
        """Low risk should map to green."""
        color = get_risk_color('low')
        assert color == (0, 255, 0, 150)  # Green with alpha

    def test_moderate_risk_is_yellow(self):
        """Moderate risk should map to yellow."""
        color = get_risk_color('moderate')
        assert color == (255, 255, 0, 150)  # Yellow with alpha

    def test_high_risk_is_orange(self):
        """High risk should map to orange."""
        color = get_risk_color('high')
        assert color == (255, 165, 0, 150)  # Orange with alpha

    def test_very_high_risk_is_red(self):
        """Very high risk should map to red."""
        color = get_risk_color('very_high')
        assert color == (255, 0, 0, 150)  # Red with alpha

    def test_extreme_risk_is_purple(self):
        """Extreme risk should map to purple."""
        color = get_risk_color('extreme')
        assert color == (128, 0, 128, 150)  # Purple with alpha


class TestRiskCategories:
    """Test risk category definitions."""

    def test_all_categories_defined(self):
        """All five risk categories should be defined."""
        expected = {'low', 'moderate', 'high', 'very_high', 'extreme'}
        assert set(RISK_CATEGORIES.keys()) == expected

    def test_categories_have_thresholds(self):
        """Each category should have min and max thresholds."""
        for category, info in RISK_CATEGORIES.items():
            assert 'min' in info
            assert 'max' in info
            assert info['min'] < info['max']
