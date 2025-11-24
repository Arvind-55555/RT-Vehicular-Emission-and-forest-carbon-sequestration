import argparse
import os
import json
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_report(output_dir, data_path="data/processed/processed_data.csv"):
    """Generate a daily report from processed data."""
    logger.info(f"Generating report in {output_dir}...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    report_data = {
        "date": datetime.now().isoformat(),
        "status": "success",
        "metrics": {}
    }
    
    try:
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            
            # Calculate some basic metrics
            if 'Net_CO2_kg' in df.columns:
                report_data["metrics"]["total_net_co2_kg"] = float(df['Net_CO2_kg'].sum())
                report_data["metrics"]["avg_net_co2_kg"] = float(df['Net_CO2_kg'].mean())
            
            if 'Net_PM25_kg' in df.columns:
                report_data["metrics"]["total_net_pm25_kg"] = float(df['Net_PM25_kg'].sum())
            
            report_data["metrics"]["total_records"] = len(df)
            
        else:
            logger.warning(f"Data file not found at {data_path}. Generating empty report.")
            report_data["status"] = "warning"
            report_data["message"] = "Data file not found"
            
        # Save report
        report_filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        report_path = os.path.join(output_dir, report_filename)
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=4)
            
        logger.info(f"Report saved to {report_path}")
        
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate daily report')
    parser.add_argument('--output', type=str, required=True, help='Output directory for reports')
    args = parser.parse_args()
    
    generate_report(args.output)
