import pytest
import pandas as pd
import os
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_pipeline import main, load_config

class TestDataPipeline:
    @pytest.fixture
    def mock_config(self):
        return {
            'data_processing': {
                'input_path': 'data/raw/',
                'output_path': 'data/processed/'
            }
        }
        
    @patch('builtins.open')
    @patch('yaml.safe_load')
    def test_load_config(self, mock_yaml_load, mock_open, mock_config):
        mock_yaml_load.return_value = mock_config
        config = load_config('config/test_config.yaml')
        assert config == mock_config
        
    @patch('data_pipeline.load_config')
    @patch('data_pipeline.DataLoader')
    @patch('data_pipeline.calculate_sequestration_and_removal')
    @patch('data_pipeline.train_lgbm_model')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('pandas.concat')
    @patch('pandas.DataFrame.to_csv')
    def test_main_pipeline(self, mock_to_csv, mock_concat, mock_exists, mock_makedirs, 
                          mock_train, mock_calc, mock_loader, mock_load_config, mock_config):
        # Setup mocks
        mock_load_config.return_value = mock_config
        mock_exists.return_value = True
        
        # Mock dataframes
        mock_df = pd.DataFrame({
            'A': [1, 2], 
            'Net_CO2_kg': [100, 200],
            'Net_PM25_kg': [10, 20],
            'Net_NOX_kg': [5, 10]
        })
        mock_loader_instance = mock_loader.return_value
        mock_loader_instance.load_vehicle_data.return_value = mock_df
        mock_loader_instance.load_forest_data.return_value = mock_df
        
        mock_concat.return_value = mock_df
        mock_calc.return_value = mock_df
        
        # Run pipeline
        main('config/test_config.yaml')
        
        # Verify calls
        mock_loader.assert_called_once()
        mock_calc.assert_called_once()
        mock_train.assert_called_once()
        mock_to_csv.assert_called()
        
    @patch('data_pipeline.load_config')
    @patch('data_pipeline.DataLoader')
    @patch('data_pipeline.train_lgbm_model')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('pandas.DataFrame.to_csv')
    def test_main_pipeline_missing_files(self, mock_to_csv, mock_exists, mock_makedirs, 
                                       mock_train, mock_loader, mock_load_config, mock_config):
        # Setup mocks to simulate missing files
        mock_load_config.return_value = mock_config
        mock_exists.return_value = False
        # Setup mocks to simulate missing files
        mock_load_config.return_value = mock_config
        mock_exists.return_value = False
        
        # Run pipeline
        # Should not raise error but create dummy data
        try:
            main('config/test_config.yaml')
        except Exception as e:
            pytest.fail(f"Pipeline raised exception on missing files: {e}")
