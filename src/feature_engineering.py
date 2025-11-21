# src/feature_engineering.py
import pandas as pd
import numpy as np
import logging
from src.config import EMISSION_FACTORS, SEQUESTRATION_FACTORS, VEHICLE_DATA

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self):
        self.emission_factors = EMISSION_FACTORS
        self.sequestration_factors = SEQUESTRATION_FACTORS
    
    def calculate_vehicular_emissions(self, df):
        """Calculate detailed vehicular emissions with improved formulas."""
        logger.info("Calculating vehicular emissions...")
        
        df = df.copy()
        
        # Calculate vehicle kilometers traveled (VKT) with congestion factor
        # Higher traffic index = more congestion = more emissions per km
        congestion_factor = 1 + (df['traffic_index_0_100'] / 100) * 0.5
        
        df['total_vkt_km'] = (
            (df['total_vehicles'] * 0.1) *  # 10% of vehicles active daily
            congestion_factor * 
            (50 - (df['traffic_index_0_100'] / 2))  # Distance varies with traffic
        )
        
        # Calculate emissions for each vehicle type
        # CO2 Emissions
        df['co2_car_kg'] = (
            df['total_vkt_km'] * df['car_prop'] * 
            self.emission_factors['CO2']['car'] / 1000
        )
        df['co2_truck_kg'] = (
            df['total_vkt_km'] * df['truck_prop'] * 
            self.emission_factors['CO2']['truck'] / 1000
        )
        df['co2_twowheeler_kg'] = (
            df['total_vkt_km'] * df['twowheeler_prop'] * 
            self.emission_factors['CO2']['twowheeler'] / 1000
        )
        df['CO2_emission_kg'] = df[['co2_car_kg', 'co2_truck_kg', 'co2_twowheeler_kg']].sum(axis=1)
        
        # PM2.5 Emissions
        df['pm25_car_kg'] = (
            df['total_vkt_km'] * df['car_prop'] * 
            self.emission_factors['PM25']['car'] / 1000
        )
        df['pm25_truck_kg'] = (
            df['total_vkt_km'] * df['truck_prop'] * 
            self.emission_factors['PM25']['truck'] / 1000
        )
        df['pm25_twowheeler_kg'] = (
            df['total_vkt_km'] * df['twowheeler_prop'] * 
            self.emission_factors['PM25']['twowheeler'] / 1000
        )
        df['PM25_emission_kg'] = df[['pm25_car_kg', 'pm25_truck_kg', 'pm25_twowheeler_kg']].sum(axis=1)
        
        # NOx Emissions
        df['nox_car_kg'] = (
            df['total_vkt_km'] * df['car_prop'] * 
            self.emission_factors['NOX']['car'] / 1000
        )
        df['nox_truck_kg'] = (
            df['total_vkt_km'] * df['truck_prop'] * 
            self.emission_factors['NOX']['truck'] / 1000
        )
        df['nox_twowheeler_kg'] = (
            df['total_vkt_km'] * df['twowheeler_prop'] * 
            self.emission_factors['NOX']['twowheeler'] / 1000
        )
        df['NOX_emission_kg'] = df[['nox_car_kg', 'nox_truck_kg', 'nox_twowheeler_kg']].sum(axis=1)
        
        logger.info("Vehicular emissions calculation completed")
        return df
    
    def calculate_sequestration_and_removal(self, df):
        """Calculate CO2 sequestration and pollutant removal with improved models."""
        logger.info("Calculating sequestration and removal...")
        
        df = df.copy()
        
        # 1. CO2 Sequestration (Improved model)
        # NDVI health factor (0 to 1.5)
        ndvi_max = self.sequestration_factors['MAX_NDVI_HEALTHY']
        df['f_ndvi'] = np.where(
            df['median_ndvi'] > ndvi_max, 
            1.5,  # Very healthy vegetation
            df['median_ndvi'] / ndvi_max  # Linear scaling
        )
        
        # Meteorological stress factor
        # Optimal temperature range: 20-30°C
        df['f_temp'] = np.where(
            (df['max_temp_c'] >= 20) & (df['max_temp_c'] <= 30),
            1.0,  # Optimal
            np.where(df['max_temp_c'] < 20, 
                    0.7 + (df['max_temp_c'] / 20) * 0.3,  # Cold stress
                    1.0 - ((df['max_temp_c'] - 30) / 20) * 0.5  # Heat stress
            )
        ).clip(0.3, 1.2)
        
        # Humidity factor (optimal: 60-80%)
        df['f_humidity'] = np.where(
            (df['humidity_pct'] >= 60) & (df['humidity_pct'] <= 80),
            1.0,
            np.where(df['humidity_pct'] < 60,
                    0.5 + (df['humidity_pct'] / 60) * 0.5,  # Dry stress
                    1.0 - ((df['humidity_pct'] - 80) / 20) * 0.3  # Too humid
            )
        ).clip(0.4, 1.1)
        
        # Total CO2 sequestration
        df['co2_sequestered_kg'] = (
            df['forest_area_sqkm'] * 
            self.sequestration_factors['CO2_BASE_KG_SQKM_DAY'] *
            df['f_ndvi'] * df['f_temp'] * df['f_humidity']
        )
        
        # 2. Pollutant Removal (Deposition)
        # Convert ambient concentration from µg/m³ to kg/m³
        df['ambient_pm25_kg_m3'] = df['pm25_ambient_ug_m3'] * 1e-9
        df['ambient_nox_kg_m3'] = df['nox_ambient_ug_m3'] * 1e-9
        
        # Calculate canopy area (assuming 15,000 sqm canopy per sqkm forest)
        canopy_density = 150000  # sqm canopy per sqkm forest
        df['canopy_area_sqm'] = df['forest_area_sqkm'] * canopy_density
        
        # Deposition velocity adjustment based on weather
        wind_effect = np.where(
            df['wind_speed_ms'] < 1, 0.7,  # Low wind reduces deposition
            np.where(df['wind_speed_ms'] > 5, 1.3, 1.0)  # High wind increases
        )
        
        # Time for deposition (seconds in a day)
        time_seconds_day = 86400
        
        # PM2.5 removal
        pm25_depo_velocity = self.sequestration_factors['PM25_DEPOSITION_VELOCITY_MS']
        df['PM25_removed_kg'] = (
            df['canopy_area_sqm'] * 
            (pm25_depo_velocity * wind_effect) * 
            df['ambient_pm25_kg_m3'] * 
            time_seconds_day
        )
        
        # NOx removal
        nox_depo_velocity = self.sequestration_factors['NOX_DEPOSITION_VELOCITY_MS']
        df['NOX_removed_kg'] = (
            df['canopy_area_sqm'] * 
            (nox_depo_velocity * wind_effect) * 
            df['ambient_nox_kg_m3'] * 
            time_seconds_day
        )
        
        logger.info("Sequestration and removal calculation completed")
        return df
    
    def calculate_net_pollutants(self, df):
        """Calculate net pollutant values (emission - removal)."""
        df = df.copy()
        
        df['Net_CO2_kg'] = df['CO2_emission_kg'] - df['co2_sequestered_kg']
        df['Net_PM25_kg'] = df['PM25_emission_kg'] - df['PM25_removed_kg']
        df['Net_NOX_kg'] = df['NOX_emission_kg'] - df['NOX_removed_kg']
        
        # Calculate efficiency metrics
        df['sequestration_efficiency'] = df['co2_sequestered_kg'] / df['forest_area_sqkm']
        df['pm25_removal_efficiency'] = df['PM25_removed_kg'] / df['forest_area_sqkm']
        df['nox_removal_efficiency'] = df['NOX_removed_kg'] / df['forest_area_sqkm']
        
        return df

def calculate_vehicular_emissions(df):
    engineer = FeatureEngineer()
    return engineer.calculate_vehicular_emissions(df)

def calculate_sequestration_and_removal(df):
    engineer = FeatureEngineer()
    df = engineer.calculate_vehicular_emissions(df)
    df = engineer.calculate_sequestration_and_removal(df)
    df = engineer.calculate_net_pollutants(df)
    return df