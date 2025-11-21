# main.py
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Create necessary directories
os.makedirs('models', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

from src.data_acquisition import get_traffic_and_weather_data
from src.feature_engineering import calculate_sequestration_and_removal
from src.model_trainer import train_lgbm_model
from src.utils import save_model

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_complete_pipeline():
    """Run the complete data pipeline and model training."""
    logger.info("Starting complete pipeline execution...")
    
    try:
        # 1. Data Acquisition
        logger.info("Step 1: Data Acquisition")
        raw_df = get_traffic_and_weather_data(
            start_date='2023-01-01', 
            days=180  # 6 months of data
        )
        
        logger.info(f"Acquired data with {len(raw_df)} records")
        logger.info(f"Columns: {list(raw_df.columns)}")
        
        # 2. Feature Engineering
        logger.info("Step 2: Feature Engineering")
        engineered_df = calculate_sequestration_and_removal(raw_df)
        
        # Save processed data
        engineered_df.to_csv('data/processed/training_data.csv', index=False)
        logger.info(f"Engineered data shape: {engineered_df.shape}")
        
        # 3. Prepare Features and Targets
        logger.info("Step 3: Preparing Features and Targets")
        
        # Define feature columns (excluding targets and identifiers)
        exclude_columns = [
            'daily_date', 'city_id', 'ward_id',
            'CO2_emission_kg', 'PM25_emission_kg', 'NOX_emission_kg',
            'co2_sequestered_kg', 'PM25_removed_kg', 'NOX_removed_kg',
            'co2_car_kg', 'co2_truck_kg', 'co2_twowheeler_kg',
            'pm25_car_kg', 'pm25_truck_kg', 'pm25_twowheeler_kg',
            'nox_car_kg', 'nox_truck_kg', 'nox_twowheeler_kg',
            'total_vehicles', 'car_prop', 'truck_prop', 'twowheeler_prop',
            'f_ndvi', 'f_temp', 'f_humidity', 'ambient_pm25_kg_m3', 
            'ambient_nox_kg_m3', 'canopy_area_sqm', 'total_vkt_km'
        ]
        
        feature_columns = [col for col in engineered_df.columns if col not in exclude_columns]
        X = engineered_df[feature_columns]
        
        # Define target variables
        Y = engineered_df[['Net_CO2_kg', 'Net_PM25_kg', 'Net_NOX_kg']]
        
        logger.info(f"Feature matrix shape: {X.shape}")
        logger.info(f"Target matrix shape: {Y.shape}")
        logger.info(f"Feature columns: {feature_columns}")
        
        # 4. Model Training
        logger.info("Step 4: Model Training")
        trainer, train_metrics, test_metrics = train_lgbm_model(X, Y)
        
        # 5. Save Final Model and Results
        logger.info("Step 5: Saving Results")
        
        # Save training summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'data_points': len(engineered_df),
            'features_used': len(feature_columns),
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'feature_importance': trainer.feature_importance.to_dict('records')
        }
        
        import json
        with open('models/training_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("Pipeline completed successfully!")
        logger.info(f"Training RMSE: {train_metrics['overall_rmse']:.2f}")
        logger.info(f"Test RMSE: {test_metrics['overall_rmse']:.2f}")
        logger.info(f"Test R²: {test_metrics['overall_r2']:.3f}")
        
        return trainer, engineered_df
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

def generate_sample_prediction(trainer=None):
    """Generate a sample prediction for testing."""
    if trainer is None:
        # Load trained model
        from src.utils import load_model
        trainer = load_model('models/trained_model.pkl')
    
    # Create sample input data
    sample_data = {
        'traffic_index_0_100': [75.0],
        'avg_speed_kph': [25.0],
        'max_temp_c': [32.0],
        'humidity_pct': [65.0],
        'wind_speed_ms': [3.0],
        'median_ndvi': [0.45],
        'forest_area_sqkm': [35.2],
        'pm25_ambient_ug_m3': [120.0],
        'nox_ambient_ug_m3': [80.0],
        'traffic_index_0_100_rolling_mean_7': [72.0],
        'traffic_index_0_100_rolling_std_7': [5.0],
        'median_ndvi_rolling_mean_7': [0.43],
        'max_temp_c_rolling_mean_7': [31.5],
        'day_of_week': [2],
        'day_of_year': [150],
        'month': [6],
        'is_weekend': [0],
        'quarter': [2],
        'city_id': ['Delhi'],
        'ward_id': ['Delhi_W1']
    }
    
    sample_df = pd.DataFrame(sample_data)
    prediction = trainer.predict(sample_df)
    
    logger.info("Sample Prediction:")
    logger.info(f"Net CO2: {prediction['Net_CO2_kg'].iloc[0]:.2f} kg/day")
    logger.info(f"Net PM2.5: {prediction['Net_PM25_kg'].iloc[0]:.4f} kg/day")
    logger.info(f"Net NOX: {prediction['Net_NOX_kg'].iloc[0]:.4f} kg/day")
    
    return prediction

if __name__ == '__main__':
    logger.info("Urban Emission and Sequestration Model Pipeline")
    
    # Run complete pipeline
    trainer, data = run_complete_pipeline()
    
    # Generate sample prediction
    generate_sample_prediction(trainer)