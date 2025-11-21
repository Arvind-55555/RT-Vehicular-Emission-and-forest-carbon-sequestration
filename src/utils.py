# src/utils.py
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_time_features(df, date_column='daily_date'):
    """Create time-based features for the model."""
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    df['day_of_week'] = df[date_column].dt.dayofweek
    df['day_of_year'] = df[date_column].dt.dayofyear
    df['month'] = df[date_column].dt.month
    df['is_weekend'] = (df[date_column].dt.dayofweek >= 5).astype(int)
    df['quarter'] = df[date_column].dt.quarter
    
    return df

def calculate_rolling_features(df, columns, windows=[7, 30]):
    """Calculate rolling statistics for time series data."""
    df = df.sort_values(['city_id', 'ward_id', 'daily_date'])
    
    for column in columns:
        for window in windows:
            df[f'{column}_rolling_mean_{window}'] = df.groupby(['city_id', 'ward_id'])[column].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f'{column}_rolling_std_{window}'] = df.groupby(['city_id', 'ward_id'])[column].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
    
    return df

def save_model(model, filepath):
    """Save trained model to file."""
    joblib.dump(model, filepath)
    logger.info(f"Model saved to {filepath}")

def load_model(filepath):
    """Load trained model from file."""
    model = joblib.load(filepath)
    logger.info(f"Model loaded from {filepath}")
    return model

def validate_input_data(df, required_columns):
    """Validate that input data contains all required columns."""
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return True

def calculate_metrics(y_true, y_pred):
    """Calculate regression metrics."""
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mse)
    
    return {
        'mse': mse,
        'mae': mae,
        'r2': r2,
        'rmse': rmse
    }