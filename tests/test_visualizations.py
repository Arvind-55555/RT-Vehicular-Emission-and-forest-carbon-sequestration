import pytest
import pandas as pd
import sys
import os
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from visualization import EmissionVisualizer

class TestVisualizations:
    def setup_method(self):
        self.visualizer = EmissionVisualizer()
        self.sample_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5),
            'emissions': [100, 120, 110, 130, 125],
            'vehicle_type': ['car'] * 5,
            'fuel_type': ['petrol'] * 5,
            'distance': [50, 60, 55, 65, 62]
        })
        
        self.forest_data = pd.DataFrame({
            'forest_type': ['deciduous', 'coniferous'],
            'carbon_sequestered': [500, 600],
            'area_hectares': [10, 15]
        })

    def test_emissions_trend_creation(self):
        """Test that emissions trend visualization can be created"""
        fig = self.visualizer.create_emissions_trend(self.sample_data)
        assert fig is not None
        
    def test_emissions_comparison_creation(self):
        """Test that emissions comparison charts can be created"""
        fig = self.visualizer.create_emissions_comparison(self.sample_data)
        assert fig is not None
        
    def test_carbon_balance_dashboard(self):
        """Test carbon balance dashboard creation"""
        fig = self.visualizer.create_carbon_balance_dashboard(
            self.sample_data, self.forest_data
        )
        assert fig is not None
        
    @patch('src.visualization.px.scatter_geo')
    def test_geospatial_visualization_skip(self, mock_scatter_geo):
        """Test geospatial visualization handles missing coordinates"""
        # Data without coordinates should skip gracefully
        fig = self.visualizer.create_geospatial_visualization(self.sample_data)
        # Should return None when coordinates are missing
        assert fig is None