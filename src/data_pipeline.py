import argparse
import yaml
import logging
import os
import pandas as pd
from src.data_loader import DataLoader
from src.feature_engineering import calculate_sequestration_and_removal
from src.model_trainer import train_lgbm_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main(config_path):
    """Main data pipeline execution."""
    logger.info("Starting data pipeline...")
    
    # Load configuration
    config = load_config(config_path)
    
    # Initialize paths
    input_path = config['data_processing']['input_path']
    output_path = config['data_processing']['output_path']
    
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    # Initialize data loader
    loader = DataLoader(data_path=input_path)
    
    try:
        # Load data
        # Note: In a real scenario, we might iterate over files or load specific ones
        # For this example, we'll assume specific filenames or skip if not found
        # to avoid crashing if data is missing in this demo environment
        
        # Create dummy data if files don't exist (for CI/CD demonstration purposes)
        if not os.path.exists(os.path.join(input_path, 'vehicle_data.csv')):
            logger.warning("Vehicle data not found. Creating dummy data for demonstration.")
            vehicle_df = pd.DataFrame({
                'vehicle_type': ['car', 'truck', 'twowheeler'] * 100,
                'fuel_type': ['petrol', 'diesel', 'petrol'] * 100,
                'distance': [10.5, 20.0, 5.0] * 100,
                'emissions': [150.0, 300.0, 50.0] * 100,
                'traffic_index_0_100': [50] * 300,
                'total_vehicles': [1000] * 300,
                'car_prop': [0.5] * 300,
                'truck_prop': [0.2] * 300,
                'twowheeler_prop': [0.3] * 300
            })
        else:
            vehicle_df = loader.load_vehicle_data(os.path.join(input_path, 'vehicle_data.csv'))
            
        if not os.path.exists(os.path.join(input_path, 'forest_data.csv')):
            logger.warning("Forest data not found. Creating dummy data for demonstration.")
            forest_df = pd.DataFrame({
                'forest_type': ['deciduous', 'coniferous'] * 150,
                'carbon_sequestered': [1000.0, 1200.0] * 150,
                'area_hectares': [50.0, 60.0] * 150,
                'median_ndvi': [0.6] * 300,
                'max_temp_c': [25.0] * 300,
                'humidity_pct': [70.0] * 300,
                'forest_area_sqkm': [0.5] * 300,
                'wind_speed_ms': [3.0] * 300,
                'pm25_ambient_ug_m3': [25.0] * 300,
                'nox_ambient_ug_m3': [40.0] * 300
            })
        else:
            forest_df = loader.load_forest_data(os.path.join(input_path, 'forest_data.csv'))
            
        # Merge data (simplistic merge for demonstration)
        # In reality, this would be a spatial or temporal join
        merged_df = pd.concat([vehicle_df, forest_df], axis=1)
        
        # Feature Engineering
        processed_df = calculate_sequestration_and_removal(merged_df)
        
        # Save processed data
        processed_df.to_csv(os.path.join(output_path, 'processed_data.csv'), index=False)
        logger.info(f"Processed data saved to {output_path}")
        
        # Model Training (Optional: only if we have target columns)
        # For this demo, we'll assume we want to train if we have 'Net_CO2_kg'
        if 'Net_CO2_kg' in processed_df.columns:
            logger.info("Training model...")
            # Prepare features (drop targets and non-numeric)
            targets = ['Net_CO2_kg', 'Net_PM25_kg', 'Net_NOX_kg']
            X = processed_df.drop(columns=targets)
            # Select only numeric columns for simplicity in this demo
            X = X.select_dtypes(include=[float, int])
            Y = processed_df[targets]
            
            # Train
            train_lgbm_model(X, Y)
            
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run data pipeline')
    parser.add_argument('--config', type=str, required=True, help='Path to configuration file')
    args = parser.parse_args()
    
    main(args.config)
