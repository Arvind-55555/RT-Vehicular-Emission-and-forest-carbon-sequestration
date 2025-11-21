# src/config.py

import os
from datetime import datetime

# --- API Configuration ---
class APIConfig:
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "your_google_maps_key")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_openweather_key")
    CPCB_API_BASE = "https://api.cpcbccr.com/v1"  # Example CPCB API

# --- City Configuration ---
CITIES = [
    "Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata", 
    "Hyderabad", "Pune", "Ahmedabad", "Surat", "Jaipur"
]

# Real forest cover data from ISFR 2023 (in sq km)
FOREST_COVER_DATA = {
    'Delhi': {'area_sqkm': 176.0, 'tree_cover_percent': 11.87},
    'Mumbai': {'area_sqkm': 130.0, 'tree_cover_percent': 18.0},
    'Bengaluru': {'area_sqkm': 110.0, 'tree_cover_percent': 15.0},
    'Chennai': {'area_sqkm': 85.0, 'tree_cover_percent': 12.0},
    'Kolkata': {'area_sqkm': 95.0, 'tree_cover_percent': 14.0},
    'Hyderabad': {'area_sqkm': 120.0, 'tree_cover_percent': 16.0},
    'Pune': {'area_sqkm': 140.0, 'tree_cover_percent': 17.0},
    'Ahmedabad': {'area_sqkm': 90.0, 'tree_cover_percent': 10.0},
    'Surat': {'area_sqkm': 80.0, 'tree_cover_percent': 9.0},
    'Jaipur': {'area_sqkm': 100.0, 'tree_cover_percent': 11.0}
}

# Real vehicle registration data (2020, in thousands)
VEHICLE_DATA = {
    'Delhi': {'total_vehicles': 11893.0, 'car_prop': 0.35, 'truck_prop': 0.05, 'twowheeler_prop': 0.55},
    'Mumbai': {'total_vehicles': 3876.17, 'car_prop': 0.30, 'truck_prop': 0.10, 'twowheeler_prop': 0.55},
    'Bengaluru': {'total_vehicles': 9638.36, 'car_prop': 0.40, 'truck_prop': 0.08, 'twowheeler_prop': 0.48},
    'Chennai': {'total_vehicles': 6351.73, 'car_prop': 0.38, 'truck_prop': 0.07, 'twowheeler_prop': 0.50},
    'Kolkata': {'total_vehicles': 1024.08, 'car_prop': 0.32, 'truck_prop': 0.06, 'twowheeler_prop': 0.57},
    'Hyderabad': {'total_vehicles': 3242.81, 'car_prop': 0.36, 'truck_prop': 0.08, 'twowheeler_prop': 0.52},
    'Pune': {'total_vehicles': 3198.83, 'car_prop': 0.42, 'truck_prop': 0.09, 'twowheeler_prop': 0.45},
    'Ahmedabad': {'total_vehicles': 4571.19, 'car_prop': 0.34, 'truck_prop': 0.08, 'twowheeler_prop': 0.54},
    'Surat': {'total_vehicles': 2800.0, 'car_prop': 0.33, 'truck_prop': 0.10, 'twowheeler_prop': 0.53},
    'Jaipur': {'total_vehicles': 3168.34, 'car_prop': 0.37, 'truck_prop': 0.07, 'twowheeler_prop': 0.52}
}

# Emission factors (g/km) - Based on ARAI/CPCB standards
EMISSION_FACTORS = {
    'CO2': {
        'car': 150.0, 'truck': 450.0, 'twowheeler': 80.0
    },
    'PM25': {
        'car': 0.005, 'truck': 0.05, 'twowheeler': 0.002
    },
    'NOX': {
        'car': 0.18, 'truck': 1.5, 'twowheeler': 0.08
    }
}

# Sequestration factors
SEQUESTRATION_FACTORS = {
    'CO2_BASE_KG_SQKM_DAY': 1500,  # ~15 tonnes/ha/year
    'PM25_DEPOSITION_VELOCITY_MS': 0.005,
    'NOX_DEPOSITION_VELOCITY_MS': 0.003,
    'MAX_NDVI_HEALTHY': 0.8
}

# Model configuration
MODEL_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'n_estimators': 500,
    'learning_rate': 0.05,
    'early_stopping_rounds': 50
}