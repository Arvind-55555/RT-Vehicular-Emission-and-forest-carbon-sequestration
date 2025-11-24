import os
import sys
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_outputs(output_dir="data/processed"):
    """Validate that expected output files exist and are valid."""
    logger.info(f"Validating outputs in {output_dir}...")
    
    expected_files = ['processed_data.csv']
    
    if not os.path.exists(output_dir):
        logger.error(f"Output directory {output_dir} does not exist.")
        sys.exit(1)
        
    all_valid = True
    
    for filename in expected_files:
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            logger.error(f"Missing expected file: {filename}")
            all_valid = False
            continue
            
        try:
            # Try to read the file to ensure it's valid
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
                if df.empty:
                    logger.error(f"File is empty: {filename}")
                    all_valid = False
                else:
                    logger.info(f"Successfully validated {filename} ({len(df)} rows)")
            else:
                logger.info(f"File exists: {filename} (content validation skipped)")
                
        except Exception as e:
            logger.error(f"Error validating {filename}: {str(e)}")
            all_valid = False
            
    if all_valid:
        logger.info("All outputs validated successfully.")
        sys.exit(0)
    else:
        logger.error("Validation failed.")
        sys.exit(1)

if __name__ == "__main__":
    validate_outputs()
