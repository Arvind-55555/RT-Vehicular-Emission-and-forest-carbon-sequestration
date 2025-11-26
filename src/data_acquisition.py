"""
This module is responsible for acquiring data from various sources.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, Any
from src.config import CITIES, FOREST_COVER_DATA, VEHICLE_DATA
from src.utils import create_time_features, calculate_rolling_features

logger = logging.getLogger(__name__)


class DataAcquisition:
    """
    A class to acquire data from various sources.
    """

    def get_traffic_data(self, city: str) -> Dict[str, Any]:
        """
        Get traffic data for a city using Google Maps API.
        In production, this would use real API calls.

        Args:
            city (str): The city for which to get traffic data.

        Returns:
            Dict[str, Any]: A dictionary containing traffic data.
        """
        try:
            # Mock implementation - replace with actual Google Maps API calls
            base_traffic = {
                "Delhi": 75,
                "Mumbai": 80,
                "Bengaluru": 85,
                "Chennai": 70,
                "Kolkata": 65,
                "Hyderabad": 72,
                "Pune": 68,
                "Ahmedabad": 62,
                "Surat": 60,
                "Jaipur": 58,
            }

            # Add some randomness to simulate real data
            traffic_index = base_traffic.get(city, 50) + np.random.uniform(-10, 10)
            avg_speed = max(10, 60 - traffic_index * 0.4)  # Inverse relationship

            return {
                "traffic_index": max(0, min(100, traffic_index)),
                "avg_speed_kph": avg_speed,
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error fetching traffic data for {city}: {e}")
            return {
                "traffic_index": 50,
                "avg_speed_kph": 30,
                "timestamp": datetime.now(),
            }

    def get_weather_data(self, city: str) -> Dict[str, Any]:
        """
        Get weather data using OpenWeatherMap API.
        Mock implementation - replace with actual API calls.

        Args:
            city (str): The city for which to get weather data.

        Returns:
            Dict[str, Any]: A dictionary containing weather data.
        """
        try:
            # Base weather patterns for Indian cities
            base_weather = {
                "temperature": np.random.uniform(25, 35),
                "humidity": np.random.uniform(40, 80),
                "wind_speed": np.random.uniform(1, 5),
                "pressure": np.random.uniform(1000, 1020),
            }

            return {
                "max_temp_c": base_weather["temperature"],
                "humidity_pct": base_weather["humidity"],
                "wind_speed_ms": base_weather["wind_speed"],
                "pressure_hpa": base_weather["pressure"],
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error fetching weather data for {city}: {e}")
            return {
                "max_temp_c": 30,
                "humidity_pct": 60,
                "wind_speed_ms": 3,
                "pressure_hpa": 1013,
                "timestamp": datetime.now(),
            }

    def get_ndvi_data(self) -> Dict[str, Any]:
        """
        Calculate NDVI using Google Earth Engine.
        Mock implementation - replace with actual GEE integration.

        Returns:
            Dict[str, Any]: A dictionary containing NDVI data.
        """
        try:
            # This would normally use Google Earth Engine
            # For now, return mock NDVI data with seasonal variation
            month = datetime.now().month
            # Higher NDVI in monsoon months (June-Sept)
            seasonal_factor = 1.2 if 6 <= month <= 9 else 1.0
            base_ndvi = np.random.uniform(0.3, 0.6) * seasonal_factor

            return {
                "median_ndvi": min(0.9, base_ndvi),
                "mean_ndvi": min(0.9, base_ndvi * 0.95),
                "ndvi_std": 0.05,
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error calculating NDVI: {e}")
            return {
                "median_ndvi": 0.5,
                "mean_ndvi": 0.48,
                "ndvi_std": 0.05,
                "timestamp": datetime.now(),
            }

    def get_air_quality_data(self, city: str) -> Dict[str, Any]:
        """
        Get real-time air quality data from CPCB/SAFAR.
        Mock implementation - replace with actual API calls.

        Args:
            city (str): The city for which to get air quality data.

        Returns:
            Dict[str, Any]: A dictionary containing air quality data.
        """
        try:
            # Base levels with some randomness
            base_pm25 = np.random.uniform(80, 200)  # µg/m³
            base_nox = np.random.uniform(40, 120)  # µg/m³

            return {
                "pm25_ug_m3": base_pm25,
                "nox_ug_m3": base_nox,
                "aqi": min(500, int(base_pm25 * 2)),
                "timestamp": datetime.now(),
            }

        except Exception as e:
            logger.error(f"Error fetching air quality data for {city}: {e}")
            return {
                "pm25_ug_m3": 150,
                "nox_ug_m3": 80,
                "aqi": 300,
                "timestamp": datetime.now(),
            }

    def generate_training_data(
        self, start_date: str = "2023-01-01", days: int = 180
    ) -> pd.DataFrame:
        """
        Generate comprehensive training data with realistic patterns.

        Args:
            start_date (str): The start date for generating data.
            days (int): The number of days for which to generate data.

        Returns:
            pd.DataFrame: A DataFrame containing the generated training data.
        """
        logger.info("Generating training data...")

        data_list = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")

        for i in range(days):
            date = current_date + timedelta(days=i)

            for city in CITIES:
                # Create multiple wards per city
                for ward_id in range(1, 6):  # 5 wards per city
                    ward_key = f"{city}_W{ward_id}"

                    # Get simulated real-time data
                    traffic_data = self.get_traffic_data(city)
                    weather_data = self.get_weather_data(city)
                    ndvi_data = self.get_ndvi_data()  # Pass actual boundary in production
                    aq_data = self.get_air_quality_data(city)

                    # Calculate ward-specific forest area (distribute total city area)
                    total_wards = 5
                    forest_area = FOREST_COVER_DATA[city]["area_sqkm"] / total_wards

                    record = {
                        "daily_date": date,
                        "city_id": city,
                        "ward_id": ward_key,
                        "traffic_index_0_100": traffic_data["traffic_index"],
                        "avg_speed_kph": traffic_data["avg_speed_kph"],
                        "max_temp_c": weather_data["max_temp_c"],
                        "humidity_pct": weather_data["humidity_pct"],
                        "wind_speed_ms": weather_data["wind_speed_ms"],
                        "median_ndvi": ndvi_data["median_ndvi"],
                        "forest_area_sqkm": forest_area,
                        "pm25_ambient_ug_m3": aq_data["pm25_ug_m3"],
                        "nox_ambient_ug_m3": aq_data["nox_ug_m3"],
                        "total_vehicles": VEHICLE_DATA[city]["total_vehicles"]
                        / total_wards,
                        "car_prop": VEHICLE_DATA[city]["car_prop"],
                        "truck_prop": VEHICLE_DATA[city]["truck_prop"],
                        "twowheeler_prop": VEHICLE_DATA[city]["twowheeler_prop"],
                    }

                    data_list.append(record)

        df = pd.DataFrame(data_list)

        # Add time-based features
        df = create_time_features(df)
        df = calculate_rolling_features(
            df, ["traffic_index_0_100", "median_ndvi", "max_temp_c"]
        )

        logger.info(f"Generated training data with {len(df)} records")
        return df
