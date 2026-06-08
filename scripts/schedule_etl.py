"""
Bonus Challenge 1: Scheduled ETL Pipeline
Bluestock MF Capstone

Auto-fetches NAV from mfapi.in and updates the SQLite database
every weekday at 8:00 PM using the `schedule` library.

Usage:
    python scripts/schedule_etl.py

    To test immediately (one-shot):
    python scripts/schedule_etl.py --run-now
"""

import schedule
import time
import subprocess
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# ── Resolve project root from this file's location ──────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
BASE        = SCRIPTS_DIR.parent
LOG_DIR     = BASE / "logs"

# Ensure log directory exists BEFORE configuring the logger
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "schedule_etl.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
)
# Also show logs in console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)


def run_etl():
    """Execute the live NAV fetch → SQLite load pipeline."""
    logging.info("=" * 60)
    logging.info("Scheduled ETL pipeline starting...")

    try:
        # Step 1: Fetch live NAV from mfapi.in
        logging.info("Step 1 — Running live_nav_fetch.py ...")
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "live_nav_fetch.py")],
            check=True,
            cwd=str(BASE),
        )

        # Step 2: Load / upsert into SQLite
        logging.info("Step 2 — Running load_to_sqlite.py ...")
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "load_to_sqlite.py")],
            check=True,
            cwd=str(BASE),
        )

        logging.info("ETL pipeline completed successfully at %s",
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    except subprocess.CalledProcessError as e:
        logging.error("ETL step failed (exit code %s): %s", e.returncode, e)
    except Exception as e:
        logging.error("Unexpected error in ETL pipeline: %s", e, exc_info=True)


# ── Schedule every weekday at 20:00 IST ──────────────────────────────────────
for day in ("monday", "tuesday", "wednesday", "thursday", "friday"):
    getattr(schedule.every(), day).at("20:00").do(run_etl)


if __name__ == "__main__":
    if "--run-now" in sys.argv:
        logging.info("--run-now flag detected. Executing immediately.")
        run_etl()
        sys.exit(0)

    logging.info("Scheduler started. ETL will run every weekday at 20:00.")
    print("ETL Scheduler is running. Press Ctrl+C to stop.")
    print("Next scheduled runs: every Mon–Fri at 8:00 PM.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)   # check every 30 s for accuracy
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user.")
        print("\nScheduler stopped.")
