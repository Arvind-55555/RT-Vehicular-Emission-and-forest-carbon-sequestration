# app.py (Streamlit Implementation Sketch)

import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="Urban Carbon & Air Quality Policy Simulator")

st.sidebar.title("🛠️ Policy Simulation Inputs")

selected_city = st.sidebar.selectbox("Select City", ["Delhi", "Mumbai", "Bengaluru", "Chennai"])

# 1. Afforestation Policy
afforestation_increase = st.sidebar.number_input(
    "🌳 Afforestation Increase (sq km)",
    min_value=0.0, max_value=100.0, value=10.0, step=1.0,
    help="Increase in city forest cover area."
)

# 2. Traffic Policy
traffic_reduction = st.sidebar.slider(
    "🚗 Traffic Reduction (%)",
    min_value=0, max_value=50, value=15, step=5,
    help="Simulates Odd-Even rule or Congestion Pricing."
)

# 3. Fleet Modernization Policy
bs_upgrade = st.sidebar.slider(
    "🚚 Fleet BS-VI Upgrade (%)",
    min_value=0, max_value=100, value=0, step=10,
    help="Percentage of old fleet upgraded to cleaner BS-VI norms."
)

if st.sidebar.button("Run Simulation"):
    # Mock/Actual API call with current/mocked input features for the selected city
    # In a real app, you would fetch the latest observed data for traffic/NDVI/weather here.
    payload = {
        "city_id": selected_city,
        "traffic_index": 75.0, # Mock current traffic index
        "avg_speed_kph": 25.0, # Mock current speed
        "median_ndvi": 0.45,   # Mock current NDVI
        "forest_area_sqkm": 20.0, # Mock static forest area
        "max_temp_c": 32.0,    # Mock current weather
        "traffic_reduction_pct": float(traffic_reduction),
        "afforestation_increase_sqkm": afforestation_increase,
        "bs_norm_upgrade_pct": float(bs_upgrade)
    }

    # API_URL = "http://localhost:8000/api/v1/predict_net_impact"
    # response = requests.post(API_URL, json=payload).json()
    
    # --- MOCKING API RESPONSE FOR DEMO ---
    import numpy as np
    
    # Simulate a 25% reduction in CO2 for a scenario
    co2_base = 35000 + np.random.rand() * 5000
    co2_net = co2_base * (1 - (traffic_reduction / 100) * 0.5 - (afforestation_increase / 100) * 0.5)

    response = {
        "city": selected_city,
        "net_co2_tonnes_day": round(co2_net / 1000, 2),
        "net_pm25_tonnes_day": round(150 * (1 - (traffic_reduction / 100) * 0.8), 4),
        "net_nox_tonnes_day": round(280 * (1 - (bs_upgrade / 100) * 0.6), 4),
    }

    st.session_state['simulation_result'] = response
    st.session_state['scenario_run'] = True

    # app.py (Streamlit Implementation Sketch - Continued)

st.title("🌏 Real-Time Urban Net CO2 & Air Quality Simulator")
st.markdown("### Analyzing the Multi-Benefit Impact of Policy Interventions")

if st.session_state.get('scenario_run', False):
    result = st.session_state['simulation_result']
    
    st.header(f"Results for {result['city']} under Policy Scenario")
    
    col1, col2, col3 = st.columns(3)
    
    # Current Baseline (Mocked for simplicity)
    baseline_co2 = 35.0
    baseline_pm25 = 0.150
    baseline_nox = 0.280

    # Policy Impact Card 1: Net CO2
    delta_co2 = result['net_co2_tonnes_day'] - baseline_co2
    col1.metric(
        label="Net CO₂ Contribution (tonnes/day)",
        value=f"{result['net_co2_tonnes_day']:.2f}",
        delta=f"{delta_co2:.2f} (Change from Baseline)",
        delta_color="inverse" if delta_co2 > 0 else "normal"
    )
    
    # Policy Impact Card 2: Net PM2.5
    delta_pm25 = result['net_pm25_tonnes_day'] - baseline_pm25
    col2.metric(
        label="Net PM₂.₅ Contribution (tonnes/day)",
        value=f"{result['net_pm25_tonnes_day']:.4f}",
        delta=f"{delta_pm25:.4f} (Change from Baseline)",
        delta_color="inverse"
    )

    # Policy Impact Card 3: Net NOx
    delta_nox = result['net_nox_tonnes_day'] - baseline_nox
    col3.metric(
        label="Net NOₓ Contribution (tonnes/day)",
        value=f"{result['net_nox_tonnes_day']:.4f}",
        delta=f"{delta_nox:.4f} (Change from Baseline)",
        delta_color="inverse"
    )

    st.subheader("Key Policy Driver Insights")
    # This chart would use a saved SHAP Explainer model to show feature importance 
    # for the current prediction.
    st.info(f"The primary driver for the $\\Delta$ in $\text{Net\_CO}_2$ is currently the **{traffic_reduction}% Traffic Reduction** (SHAP Value: -12.5 tonnes/day).")
    
    #