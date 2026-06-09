"""
Bluestock Mutual Fund Analytics Capstone - Master Run Pipeline

This script orchestrates the entire data pipeline sequentially:
1. Data Ingestion (fetching live NAVs and merging history)
2. Database Loading (ETL to SQLite)
3. Basic Metric Computation (CAGR, Volatility, Sharpe, etc.)
4. Advanced Risk & Cohort Analytics
"""

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_script(script_path):
    """Executes a python script and monitors its completion."""
    logging.info(f"🚀 Starting step: {script_path}")
    try:
        # Run script
        result = subprocess.run([sys.executable, script_path], check=True, text=True, capture_output=True)
        logging.info(f"✅ Successfully completed: {script_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error in {script_path}:\n{e.stderr}")
        sys.exit(1)

def main():
    logging.info("Starting Bluestock Mutual Fund Analytics Pipeline...")

    # Define the sequence of scripts
    pipeline_scripts = [
        "scripts/data_ingestion.py",
        "scripts/load_to_sqlite.py",
        "scripts/compute_metrics.py",
        "scripts/compute_var_cvar.py",
        "scripts/compute_sector_hhi.py",
        "scripts/compute_cohort_analysis.py",
        "scripts/compute_sip_continuity.py"
    ]

    for script in pipeline_scripts:
        run_script(script)

    logging.info("🎉 All pipeline steps executed successfully!")

if __name__ == "__main__":
    main()
