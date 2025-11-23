import pandas as pd
import numpy as np
import os
from typing import Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """Enhanced data loader with error handling and validation"""
    
    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.json']
        
    def load_vehicle_data(self, file_path: str) -> pd.DataFrame:
        """Load and validate vehicle emissions data"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Data file not found: {file_path}")
                
            # Auto-detect file type and load
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
                
            # Validate required columns
            required_columns = ['vehicle_type', 'fuel_type', 'distance', 'emissions']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
                
            logger.info(f"Successfully loaded vehicle data with {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error loading vehicle data: {str(e)}")
            raise
    
    def load_forest_data(self, file_path: str) -> pd.DataFrame:
        """Load and validate forest carbon data"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Forest data file not found: {file_path}")
                
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            # Basic data validation
            if df.isnull().sum().sum() > 0:
                logger.warning("Forest data contains missing values")
                
            return df
            
        except Exception as e:
            logger.error(f"Error loading forest data: {str(e)}")
            raise