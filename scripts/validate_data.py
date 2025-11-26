#!/usr/bin/env python3
"""
Data validation script for GitHub Actions
"""

import sys
import os
import pandas as pd
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data_loader import DataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_data_schemas():
    """Validate that data files conform to expected schemas"""
    try:
        loader = DataLoader()

        # Check if data directory exists
        data_dir = Path("data")
        if not data_dir.exists():
            logger.warning("Data directory not found - skipping validation")
            return True

        # Validate vehicle data schema if file exists
        vehicle_data_path = data_dir / "raw" / "vehicle_emissions.csv"
        if vehicle_data_path.exists():
            vehicle_data = loader.load_vehicle_data(str(vehicle_data_path))
            logger.info(f"Vehicle data validated: {len(vehicle_data)} records")

        # Validate forest data schema if file exists
        forest_data_path = data_dir / "raw" / "forest_data.csv"
        if forest_data_path.exists():
            forest_data = loader.load_forest_data(str(forest_data_path))
            logger.info(f"Forest data validated: {len(forest_data)} records")

        logger.info("All data validation checks passed")
        return True

    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = validate_data_schemas()
    sys.exit(0 if success else 1)
