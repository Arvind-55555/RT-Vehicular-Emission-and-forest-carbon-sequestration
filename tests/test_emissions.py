import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from emissions_calculator import EmissionsCalculator
from data_loader import DataLoader


class TestEmissionsCalculator:
    """Test suite for the EmissionsCalculator class."""

    def setup_method(self):
        """Set up the test case."""
        self.calculator = EmissionsCalculator()

    def test_calculate_emissions_valid(self):
        """Test the calculate_emissions method with valid inputs."""
        emissions = self.calculator.calculate_emissions(100, "petrol")
        assert isinstance(emissions, float)
        assert emissions > 0

    def test_calculate_emissions_invalid_fuel(self):
        """Test the calculate_emissions method with an invalid fuel type."""
        with pytest.raises(ValueError):
            self.calculator.calculate_emissions(100, "invalid_fuel")

    def test_calculate_emissions_negative_distance(self):
        """Test the calculate_emissions method with a negative distance."""
        with pytest.raises(ValueError):
            self.calculator.calculate_emissions(-100, "petrol")
