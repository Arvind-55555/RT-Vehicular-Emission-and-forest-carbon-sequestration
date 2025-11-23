import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from emissions_calculator import EmissionsCalculator
from data_loader import DataLoader

class TestEmissionsCalculator:
    def setup_method(self):
        self.calculator = EmissionsCalculator()
    
    def test_calculate_emissions_valid(self):
        emissions = self.calculator.calculate_emissions(100, 'petrol')
        assert isinstance(emissions, float)
        assert emissions > 0
    
    def test_calculate_emissions_invalid_fuel(self):
        with pytest.raises(ValueError):
            self.calculator.calculate_emissions(100, 'invalid_fuel')
    
    def test_calculate_emissions_negative_distance(self):
        with pytest.raises(ValueError):
            self.calculator.calculate_emissions(-100, 'petrol')