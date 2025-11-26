"""
This module contains the EmissionsCalculator class, which is responsible for calculating emissions.
"""
import pandas as pd
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EmissionsCalculator:
    """
    Enhanced emissions calculator with proper error handling.
    """

    # Emission factors (kg CO2 per km)
    EMISSION_FACTORS: Dict[str, float] = {
        "petrol": 0.21,
        "diesel": 0.25,
        "electric": 0.05,
        "hybrid": 0.12,
    }

    def calculate_emissions(self, distance: float, fuel_type: str) -> float:
        """
        Calculate emissions with validation.

        Args:
            distance (float): The distance traveled.
            fuel_type (str): The type of fuel used.

        Returns:
            float: The calculated emissions.
        """
        try:
            # Input validation
            if distance <= 0:
                raise ValueError("Distance must be positive")

            if fuel_type.lower() not in self.EMISSION_FACTORS:
                raise ValueError(f"Unsupported fuel type: {fuel_type}")

            # Calculate emissions
            emission_factor = self.EMISSION_FACTORS[fuel_type.lower()]
            emissions = distance * emission_factor

            logger.debug(f"Calculated emissions: {emissions} kg CO2")
            return round(emissions, 2)

        except Exception as e:
            logger.error(f"Error calculating emissions: {str(e)}")
            raise

    def calculate_bulk_emissions(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate emissions for multiple vehicles.

        Args:
            data (pd.DataFrame): A DataFrame containing vehicle data.

        Returns:
            pd.DataFrame: The DataFrame with an added 'calculated_emissions' column.
        """
        try:
            if not isinstance(data, pd.DataFrame):
                raise TypeError("Input must be a pandas DataFrame")

            results = data.copy()
            results["calculated_emissions"] = results.apply(
                lambda row: self.calculate_emissions(row["distance"], row["fuel_type"]),
                axis=1,
            )

            return results

        except Exception as e:
            logger.error(f"Error in bulk emissions calculation: {str(e)}")
            raise
