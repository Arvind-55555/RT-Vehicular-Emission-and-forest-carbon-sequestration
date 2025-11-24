# src/api/main.py (FastAPI Sketch)
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from src.utils import load_model

app = FastAPI()

class PolicyInput(BaseModel):
    city_id: str
    traffic_reduction_pct: float
    afforestation_increase_sqkm: float
    bs_norm_upgrade_pct: float

# Load the trained LightGBM model globally
# Ensure the model file exists or handle the error gracefully for the API to start
try:
    model = load_model("models/trained_model.pkl") 
except Exception:
    model = None # Handle case where model is not yet trained

@app.post("/api/v1/predict_net_impact")
async def predict_net_impact(data: PolicyInput):
    # 1. Load baseline features into a DataFrame (X_base)
    X_base = pd.DataFrame([data.dict(exclude={'traffic_reduction_pct', 'afforestation_increase_sqkm', 'bs_norm_upgrade_pct'})])
    
    # 2. Apply Policy Overrides to create Scenario Features (X_scenario)
    X_scenario = X_base.copy()
    
    # Traffic Policy: Reduce traffic_index and adjust speed
    if data.traffic_reduction_pct > 0:
        reduction_factor = 1.0 - data.traffic_reduction_pct / 100
        X_scenario['traffic_index'] *= reduction_factor
        X_scenario['avg_speed_kph'] = (X_scenario['avg_speed_kph'] / reduction_factor).clip(upper=70)

    # Afforestation Policy: Increase forest area
    X_scenario['forest_area_sqkm'] += data.afforestation_increase_sqkm
    
    # Note: BS Norm policy would modify the *internal* calculated emission factor (E') logic before prediction.

    # 3. Predict using the trained model
    Y_scenario = model.predict(X_scenario)
    
    # The output is an array of [Net_CO2, Net_PM25, Net_NOx]
    return {
        "city": data.city_id,
        "net_co2_tonnes_day": round(Y_scenario[0, 0] / 1000, 2), # Convert kg to tonnes
        "net_pm25_tonnes_day": round(Y_scenario[0, 1] / 1000, 4),
        "net_nox_tonnes_day": round(Y_scenario[0, 2] / 1000, 4),
    }