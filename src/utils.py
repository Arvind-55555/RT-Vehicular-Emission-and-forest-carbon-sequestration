"""
This module contains utility functions for the application.
"""
import pandas as pd
import numpy as np
import logging
import joblib
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_time_features(df: pd.DataFrame, date_column: str = "daily_date") -> pd.DataFrame:
    """
    Create time-based features for the model.

    Args:
        df (pd.DataFrame): The input DataFrame.
        date_column (str): The name of the date column.

    Returns:
        pd.DataFrame: The DataFrame with added time-based features.
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])

    df["day_of_week"] = df[date_column].dt.dayofweek
    df["day_of_year"] = df[date_column].dt.dayofyear
    df["month"] = df[date_column].dt.month
    df["is_weekend"] = (df[date_column].dt.dayofweek >= 5).astype(int)
    df["quarter"] = df[date_column].dt.quarter

    return df


def calculate_rolling_features(
    df: pd.DataFrame, columns: List[str], windows: List[int] = [7, 30]
) -> pd.DataFrame:
    """
    Calculate rolling statistics for time series data.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (List[str]): The columns for which to calculate rolling features.
        windows (List[int]): The window sizes for the rolling features.

    Returns:
        pd.DataFrame: The DataFrame with added rolling features.
    """
    df = df.sort_values(["city_id", "ward_id", "daily_date"])

    for column in columns:
        for window in windows:
            df[f"{column}_rolling_mean_{window}"] = df.groupby(["city_id", "ward_id"])[
                column
            ].transform(lambda x: x.rolling(window=window, min_periods=1).mean())
            df[f"{column}_rolling_std_{window}"] = df.groupby(["city_id", "ward_id"])[
                column
            ].transform(lambda x: x.rolling(window=window, min_periods=1).std())

    return df


def save_model(model: Any, filepath: str) -> None:
    """
    Save trained model to file.

    Args:
        model (Any): The trained model.
        filepath (str): The path to save the model to.
    """
    joblib.dump(model, filepath)
    logger.info(f"Model saved to {filepath}")


def load_model(filepath: str) -> Any:
    """
    Load trained model from file.

    Args:
        filepath (str): The path to load the model from.

    Returns:
        Any: The loaded model.
    """
    model = joblib.load(filepath)
    logger.info(f"Model loaded from {filepath}")
    return model


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate regression metrics.

    Args:
        y_true (np.ndarray): The true values.
        y_pred (np.ndarray): The predicted values.

    Returns:
        Dict[str, float]: A dictionary of regression metrics.
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mse)

    return {"mse": mse, "mae": mae, "r2": r2, "rmse": rmse}
