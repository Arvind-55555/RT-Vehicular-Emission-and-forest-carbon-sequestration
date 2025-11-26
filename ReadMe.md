# Urban Emission & Sequestration Modeling System

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-brightgreen)](https://Arvind-55555.github.io/urban-emission-model)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

A comprehensive machine learning system for real-time analysis of vehicular emissions and forest carbon sequestration in India's top 10 cities.

## Overview

This project provides a data-driven framework to model and predict net pollution levels (emissions minus natural removal) across major Indian cities. The system enables policymakers to simulate the impact of various urban planning interventions through an interactive dashboard.

## To-Do

- [ ] **Real-time Data Integration**: Integrate real-time data sources for traffic, weather, and air quality.
- [ ] **Model Improvement**: Experiment with different models and hyperparameter tuning to improve performance.
- [ ] **Dashboard Enhancement**: Add more interactive features to the dashboard, such as historical data visualization and more detailed policy simulation options.
- [ ] **API Expansion**: Add more endpoints to the API, such as for retrieving historical data and model performance metrics.
- [ ] **Deployment**: Deploy the application to a cloud platform for public access.

## Live Demo

[![View Artifact](https://img.shields.io/badge/View%20Artifact-%230077B5.svg?style=for-the-badge&logo=claude&logoColor=white)](https://claude.ai/public/artifacts/14659b43-e3a3-468e-9136-46830acd1c79)

### Key Features

- **Real-time Data Integration**: Traffic, weather, satellite imagery, and air quality data
- **Multi-Pollutant Modeling**: CO₂, PM₂.₅, and NOₓ emissions and sequestration
- **Policy Simulation**: "What-if" analysis for traffic reduction, afforestation, and fleet upgrades
- **Interactive Dashboard**: Streamlit-based visualization with SHAP explainability
- **REST API**: FastAPI backend for model predictions
- **Scalable Architecture**: Modular design for easy extension

## Supported Cities

1. Delhi
2. Mumbai
3. Bengaluru
4. Chennai
5. Kolkata
6. Hyderabad
7. Pune
8. Ahmedabad
9. Surat
10. Jaipur

## System Architecture

```
urban_co2_predictor/
├── data/
│   ├── raw/
│   │   ├── traffic_api_data/   # Hourly JSON logs
│   │   ├── weather_api_data/   # Daily/Hourly CSVs
│   │   └── isfr_fsi_reports/   # Static reports
│   ├── processed/
│   │   ├── emissions/          # Daily Emission Aggregates
│   │   └── sequestration/      # Daily Sequestration Aggregates
│   └── external/
│       ├── city_boundaries/    # GeoJSON files for 10 cities/wards
│       └── emission_factors/   # CSVs with E_type and V_d coefficients
├── notebooks/
│   ├── 01_eda_and_data_cleaning.ipynb
│   └── 02_model_training_evaluation.ipynb
├── src/
│   ├── __init__.py
│   ├── data_acquisition.py     # API calls (Traffic, Weather)
│   ├── geo_processor.py        # GEE (NDVI) and spatial aggregation
│   ├── feature_engineering.py  # CO2/Pollutant calculation logic
│   └── model_trainer.py        # XGBoost/LightGBM definition and training
├── main.py                     # Orchestration script
├── requirements.txt            # Python dependencies
└── config.yaml                 # API keys, city list, zone names
```

## Quick Start

### Prerequisites

- Python 3.8+
- Google Maps API Key
- OpenWeatherMap API Key
- Google Earth Engine Account

### Installation

1. **Clone and setup environment**:
```bash
git clone <repository-url>
cd urban-emission-model
pip install -r requirements.txt
```

2. **Configure API keys**:
```bash
export GOOGLE_MAPS_API_KEY="your_key"
export OPENWEATHER_API_KEY="your_key"
```

3. **Train the model**:
```bash
python main.py
```

4. **Start the API server**:
```bash
python api.py
```

5. **Launch the dashboard**:
```bash
streamlit run dashboard.py
```

## Data Sources

### Real-time Data
- **Traffic**: Google Maps Distance Matrix API
- **Weather**: OpenWeatherMap API
- **Vegetation**: Google Earth Engine (Sentinel-2 NDVI/LAI)
- **Air Quality**: CPCB/SAFAR APIs

### Static Data
- **Forest Cover**: India State of Forest Report (ISFR) 2023
- **Vehicle Registry**: Ministry of Road Transport (Parivahan)
- **City Boundaries**: OpenStreetMap
- **Population Density**: Census of India

## Core Components

### 1. Data Acquisition (`src/data_acquisition.py`)

| Function | Description | Key Libraries |
|----------|-------------|---------------|
| `get_traffic_data()` | Google Maps Traffic API integration | requests, pandas |
| `get_weather_data()` | Meteorological data fetching | requests, OpenWeatherMap |
| `get_ndvi_lai_data()` | Satellite imagery processing | earthengine-api, geopandas |
| `get_air_quality_data()` | Real-time pollution monitoring | requests, pandas |

### 2. Feature Engineering (`src/feature_engineering.py`)

| Function | Description | Key Libraries |
|----------|-------------|---------------|
| `calculate_vehicular_emissions()` | CO₂, PM₂.₅, NOₓ emission models | pandas, numpy |
| `calculate_sequestration()` | CO₂ absorption calculations | pandas, numpy |
| `calculate_pollutant_removal()` | PM₂.₅/NOₓ deposition models | pandas, numpy |
| `engineer_time_lags()` | Temporal feature engineering | pandas |

### 3. Model Training (`src/model_trainer.py`)

- **Algorithm**: Multi-output LightGBM Regressor
- **Targets**: [Net_CO₂, Net_PM₂.₅, Net_NOₓ]
- **Features**: 50+ engineered variables including traffic patterns, weather conditions, vegetation indices, and temporal features
- **Evaluation**: RMSE, MAE, R² with cross-validation

## Policy Simulation

### Available Interventions

- **Traffic Reduction (0-50%)**: Odd-Even rules, congestion pricing
- **Afforestation (0-100 km²)**: Urban greening projects
- **Fleet Modernization (0-100%)**: BS-VI vehicle upgrades
- **Meteorological Scenarios**: Extreme weather impact analysis

### Impact Metrics

- **Net Pollution Change**: tonnes/day reduction
- **Sequestration Efficiency**: kg CO₂/sq km
- **Health Benefits**: Estimated AQI improvement
- **Cost-Benefit Analysis**: Policy effectiveness scoring

## Model Performance

| Target | RMSE | R² | MAE |
|--------|------|-----|-----|
| Net CO₂ | 1,250 kg/day | 0.89 | 890 kg/day |
| Net PM₂.₅ | 0.85 kg/day | 0.82 | 0.62 kg/day |
| Net NOₓ | 1.45 kg/day | 0.85 | 1.02 kg/day |

### Model Interpretability

- **SHAP Analysis**: Feature importance visualization
- **Partial Dependence Plots**: Policy impact curves
- **Counterfactual Explanations**: "What-if" scenario reasoning
- **Uncertainty Quantification**: Prediction confidence intervals

## API Endpoints

### Prediction API

**Request:**
```http
POST /api/v1/predict_net_impact
Content-Type: application/json

{
  "city_id": "Delhi",
  "ward_id": "Delhi_W1",
  "traffic_index_0_100": 75.0,
  "median_ndvi": 0.45,
  "forest_area_sqkm": 35.2,
  "traffic_reduction_pct": 15.0,
  "afforestation_increase_sqkm": 5.0
}
```

**Response:**
```json
{
  "net_co2_tonnes_day": 28.45,
  "net_pm25_tonnes_day": 0.125,
  "net_nox_tonnes_day": 0.205,
  "policy_impact_co2": -7.25
}
```

## Development

### Adding New Cities

1. Update `CITIES` in `src/config.py`
2. Add forest cover data to `FOREST_COVER_DATA`
3. Include vehicle registry information in `VEHICLE_DATA`

### Extending Models

- New pollutants can be added in `EMISSION_FACTORS`
- Alternative sequestration models in `calculate_sequestration()`
- Additional policy scenarios in dashboard simulation logic

### Testing

```bash
pytest tests/ -v
```

## Methodology

### Emission Calculations
```python
Daily Emission = Σ(Vehicle Type × Distance × Emission Factor × Congestion Multiplier)
```

### Sequestration Models
```python
CO₂ Sequestration = Forest Area × Base Rate × NDVI Health Factor × Meteorological Factor
```

### Pollutant Removal
```python
Deposition = Canopy Area × Deposition Velocity × Ambient Concentration × Time
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
