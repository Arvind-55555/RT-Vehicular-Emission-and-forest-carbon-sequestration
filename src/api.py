"""
FastAPI application for the Urban Pollution Net Impact Predictor.

This module defines the FastAPI application, including the API endpoints for
predicting the net pollution impact of policy interventions.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Any
import uvicorn

from src.utils import load_model
from src.config import CITIES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Urban Pollution Net Impact Predictor API",
    description="API for predicting net pollution impact of policy interventions",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
MODEL = None


class PolicyInput(BaseModel):
    """
    Input data model for the policy simulation.

    Attributes:
        city_id (str): The ID of the city.
        ward_id (str): The ID of the ward.
        traffic_index_0_100 (float): The traffic index, from 0 to 100.
        avg_speed_kph (float): The average speed in km/h.
        median_ndvi (float): The median NDVI value.
        forest_area_sqkm (float): The forest area in square kilometers.
        max_temp_c (float): The maximum temperature in Celsius.
        humidity_pct (float): The humidity in percent.
        wind_speed_ms (float): The wind speed in m/s.
        pm25_ambient_ug_m3 (float): The ambient PM2.5 concentration in µg/m³.
        nox_ambient_ug_m3 (float): The ambient NOx concentration in µg/m³.
        traffic_reduction_pct (float): The traffic reduction in percent.
        afforestation_increase_sqkm (float): The afforestation increase in square kilometers.
        bs_norm_upgrade_pct (float): The percentage of the fleet upgraded to BS-VI norms.
    """

    city_id: str
    ward_id: str
    traffic_index_0_100: float
    avg_speed_kph: float
    median_ndvi: float
    forest_area_sqkm: float
    max_temp_c: float
    humidity_pct: float
    wind_speed_ms: float
    pm25_ambient_ug_m3: float
    nox_ambient_ug_m3: float

    # Policy overrides
    traffic_reduction_pct: float = 0.0
    afforestation_increase_sqkm: float = 0.0
    bs_norm_upgrade_pct: float = 0.0


class PredictionResponse(BaseModel):
    """
    Response data model for the prediction.

    Attributes:
        city (str): The city ID.
        net_co2_tonnes_day (float): The net CO2 emissions in tonnes per day.
        net_pm25_tonnes_day (float): The net PM2.5 emissions in tonnes per day.
        net_nox_tonnes_day (float): The net NOx emissions in tonnes per day.
        policy_impact_co2 (Optional[float]): The policy impact on CO2 emissions.
        policy_impact_pm25 (Optional[float]): The policy impact on PM2.5 emissions.
        policy_impact_nox (Optional[float]): The policy impact on NOx emissions.
    """

    city: str
    net_co2_tonnes_day: float
    net_pm25_tonnes_day: float
    net_nox_tonnes_day: float
    policy_impact_co2: Optional[float] = None
    policy_impact_pm25: Optional[float] = None
    policy_impact_nox: Optional[float] = None


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    global MODEL
    try:
        MODEL = load_model("models/trained_model.pkl")
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError("Model loading failed")


@app.get("/")
async def root():
    return {"message": "Urban Pollution Net Impact Predictor API", "status": "healthy"}


@app.get("/cities")
async def get_cities():
    """Get list of supported cities."""
    return {"cities": CITIES}


@app.post("/api/v1/predict_net_impact", response_model=PredictionResponse)
async def predict_net_impact(data: PolicyInput):
    """
    Predict net pollution impact for a given scenario with policy interventions.
    """
    try:
        if MODEL is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        # Create baseline and scenario feature sets
        baseline_features = create_feature_dict(data, apply_policies=False)
        scenario_features = create_feature_dict(data, apply_policies=True)

        # Convert to DataFrames
        baseline_df = pd.DataFrame([baseline_features])
        scenario_df = pd.DataFrame([scenario_features])

        # Make predictions
        baseline_pred = MODEL.predict(baseline_df)
        scenario_pred = MODEL.predict(scenario_df)

        # Convert kg to tonnes
        baseline_tonnes = baseline_pred[0] / 1000
        scenario_tonnes = scenario_pred[0] / 1000

        # Calculate policy impact
        policy_impact = scenario_tonnes - baseline_tonnes

        response = PredictionResponse(
            city=data.city_id,
            net_co2_tonnes_day=float(scenario_tonnes[0]),
            net_pm25_tonnes_day=float(scenario_tonnes[1]),
            net_nox_tonnes_day=float(scenario_tonnes[2]),
            policy_impact_co2=float(policy_impact[0]),
            policy_impact_pm25=float(policy_impact[1]),
            policy_impact_nox=float(policy_impact[2]),
        )

        logger.info(f"Prediction completed for {data.city_id} - {data.ward_id}")
        return response

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_feature_dict(
    data: PolicyInput, apply_policies: bool = False
) -> Dict[str, float]:
    """
    Create feature dictionary with optional policy applications.

    Args:
        data (PolicyInput): The input data.
        apply_policies (bool): Whether to apply the policy interventions.

    Returns:
        Dict[str, float]: The feature dictionary.
    """
    features = {
        "traffic_index_0_100": data.traffic_index_0_100,
        "avg_speed_kph": data.avg_speed_kph,
        "max_temp_c": data.max_temp_c,
        "humidity_pct": data.humidity_pct,
        "wind_speed_ms": data.wind_speed_ms,
        "median_ndvi": data.median_ndvi,
        "forest_area_sqkm": data.forest_area_sqkm,
        "pm25_ambient_ug_m3": data.pm25_ambient_ug_m3,
        "nox_ambient_ug_m3": data.nox_ambient_ug_m3,
        "city_id": data.city_id,
        "ward_id": data.ward_id,
    }

    # Add time-based features (using current time as reference)
    from datetime import datetime

    current_date = datetime.now()

    features.update(
        {
            "day_of_week": current_date.weekday(),
            "day_of_year": current_date.timetuple().tm_yday,
            "month": current_date.month,
            "is_weekend": 1 if current_date.weekday() >= 5 else 0,
            "quarter": (current_date.month - 1) // 3 + 1,
        }
    )

    # Apply policy interventions if requested
    if apply_policies:
        # Traffic reduction policy
        if data.traffic_reduction_pct > 0:
            reduction_factor = 1.0 - data.traffic_reduction_pct / 100
            features["traffic_index_0_100"] *= reduction_factor
            features["avg_speed_kph"] = min(
                70, features["avg_speed_kph"] / reduction_factor
            )

        # Afforestation policy
        features["forest_area_sqkm"] += data.afforestation_increase_sqkm

        # BS norm upgrade (affects emission factors indirectly)
        # This would modify the internal emission calculation in a real scenario

        # Add rolling features (simplified)
        features["traffic_index_0_100_rolling_mean_7"] = (
            features["traffic_index_0_100"] * 0.95
        )
        features["traffic_index_0_100_rolling_std_7"] = (
            features["traffic_index_0_100"] * 0.1
        )
        features["median_ndvi_rolling_mean_7"] = features["median_ndvi"] * 1.02
        features["max_temp_c_rolling_mean_7"] = features["max_temp_c"] * 0.98
    else:
        # Add baseline rolling features
        features["traffic_index_0_100_rolling_mean_7"] = (
            features["traffic_index_0_100"] * 0.95
        )
        features["traffic_index_0_100_rolling_std_7"] = (
            features["traffic_index_0_100"] * 0.1
        )
        features["median_ndvi_rolling_mean_7"] = features["median_ndvi"] * 1.02
        features["max_temp_c_rolling_mean_7"] = features["max_temp_c"] * 0.98

    return features


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None,
        "timestamp": pd.Timestamp.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
