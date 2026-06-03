"""
load_to_sqlite.py — Day 2 Task 5
=================================
Loads all cleaned datasets into the bluestock_mf.db SQLite database.

Tables populated (in dependency order):
    1. fund_master          ← data/raw/01_fund_master.csv
    2. nav_history          ← data/processed/clean_nav.csv  (+ daily_return computed)
    3. aum_by_fund_house    ← data/raw/03_aum_by_fund_house.csv
    4. monthly_sip_inflows  ← data/raw/04_monthly_sip_inflows.csv
    5. category_inflows     ← data/raw/05_category_inflows.csv
    6. scheme_performance   ← data/processed/clean_performance.csv
    7. portfolio_holdings   ← data/raw/09_portfolio_holdings.csv
    8. fact_transactions    ← data/processed/clean_transactions.csv

Usage:
    python scripts/load_to_sqlite.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
DB_PATH       = BASE_DIR / "data" / "db" / "bluestock_mf.db"
SCHEMA_PATH   = BASE_DIR / "sql" / "schema.sql"
RAW_DIR       = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Open SQLite connection with FK enforcement enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def apply_schema(conn):
    """Drop & recreate all tables from schema.sql."""
    print("[1/9] Applying schema …")
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    print("      ✓ Schema applied — all tables created.")


# ─── Loaders ────────────────────────────────────────────────────────────────

def load_fund_master(conn):
    """Load fund_master from raw CSV."""
    print("[2/9] Loading fund_master …")
    df = pd.read_csv(RAW_DIR / "01_fund_master.csv")

    # Normalise column names
    df.columns = df.columns.str.strip()

    df.to_sql("fund_master", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM fund_master", conn)["n"][0]
    print(f"      ✓ fund_master loaded: {count} rows")
    return count


def load_nav_history(conn):
    """Load nav_history from clean_nav.csv and compute daily_return."""
    print("[3/9] Loading nav_history (+ computing daily_return) …")
    df = pd.read_csv(PROCESSED_DIR / "clean_nav.csv", parse_dates=["date"])
    df.sort_values(["amfi_code", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Compute per-fund daily percentage return
    df["daily_return"] = (
        df.groupby("amfi_code")["nav"]
          .pct_change()               # NaN for first row of each fund
    )

    df.to_sql("nav_history", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM nav_history", conn)["n"][0]
    print(f"      ✓ nav_history loaded: {count:,} rows (daily_return computed)")
    return count


def load_aum_by_fund_house(conn):
    """Load aum_by_fund_house from raw CSV."""
    print("[4/9] Loading aum_by_fund_house …")
    df = pd.read_csv(RAW_DIR / "03_aum_by_fund_house.csv")
    df.columns = df.columns.str.strip()

    # Column mapping: normalise to schema names
    col_map = {
        "aum_lakh_crores": "aum_lakh_crore",
        "aum_lakh_crore_s": "aum_lakh_crore",
        "number_of_schemes": "num_schemes",
    }
    df.rename(columns=col_map, inplace=True)

    # Keep only schema columns
    schema_cols = ["date", "fund_house", "aum_lakh_crore", "aum_crore", "num_schemes"]
    keep = [c for c in schema_cols if c in df.columns]
    df = df[keep]

    df.to_sql("aum_by_fund_house", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM aum_by_fund_house", conn)["n"][0]
    print(f"      ✓ aum_by_fund_house loaded: {count} rows")
    return count


def load_monthly_sip_inflows(conn):
    """Load monthly_sip_inflows from raw CSV."""
    print("[5/9] Loading monthly_sip_inflows …")
    df = pd.read_csv(RAW_DIR / "04_monthly_sip_inflows.csv")
    df.columns = df.columns.str.strip()

    col_map = {
        "month_year": "month",
        "sip_inflow_crores": "sip_inflow_crore",
        "sip_inflow_cr": "sip_inflow_crore",
        "active_sip_accounts": "active_sip_accounts_crore",
        "new_sip_accounts": "new_sip_accounts_lakh",
        "sip_aum": "sip_aum_lakh_crore",
        "yoy_growth": "yoy_growth_pct",
    }
    df.rename(columns=col_map, inplace=True)

    schema_cols = [
        "month", "sip_inflow_crore", "active_sip_accounts_crore",
        "new_sip_accounts_lakh", "sip_aum_lakh_crore", "yoy_growth_pct"
    ]
    keep = [c for c in schema_cols if c in df.columns]
    df = df[keep]

    df.to_sql("monthly_sip_inflows", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM monthly_sip_inflows", conn)["n"][0]
    print(f"      ✓ monthly_sip_inflows loaded: {count} rows")
    return count


def load_category_inflows(conn):
    """Load category_inflows from raw CSV."""
    print("[6/9] Loading category_inflows …")
    df = pd.read_csv(RAW_DIR / "05_category_inflows.csv")
    df.columns = df.columns.str.strip()

    col_map = {
        "month_year": "month",
        "net_inflow": "net_inflow_crore",
        "net_inflow_crores": "net_inflow_crore",
    }
    df.rename(columns=col_map, inplace=True)

    schema_cols = ["month", "category", "net_inflow_crore"]
    keep = [c for c in schema_cols if c in df.columns]
    df = df[keep]

    df.to_sql("category_inflows", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM category_inflows", conn)["n"][0]
    print(f"      ✓ category_inflows loaded: {count} rows")
    return count


def load_scheme_performance(conn):
    """Load scheme_performance from clean_performance.csv."""
    print("[7/9] Loading scheme_performance …")
    df = pd.read_csv(PROCESSED_DIR / "clean_performance.csv")
    df.columns = df.columns.str.strip()

    # Ensure boolean flag columns are 0/1 integers for SQLite
    for flag_col in ["negative_sharpe_flag", "expense_ratio_out_of_range_flag"]:
        if flag_col in df.columns:
            df[flag_col] = df[flag_col].astype(int)

    df.to_sql("scheme_performance", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM scheme_performance", conn)["n"][0]
    print(f"      ✓ scheme_performance loaded: {count} rows")
    return count


def load_portfolio_holdings(conn):
    """Load portfolio_holdings from raw CSV."""
    print("[8/9] Loading portfolio_holdings …")
    df = pd.read_csv(RAW_DIR / "09_portfolio_holdings.csv")
    df.columns = df.columns.str.strip()

    col_map = {
        "market_value_crore": "market_value_cr",
        "market_value_cr": "market_value_cr",
        "current_price": "current_price_inr",
    }
    df.rename(columns=col_map, inplace=True)

    schema_cols = [
        "amfi_code", "stock_symbol", "stock_name", "sector",
        "weight_pct", "market_value_cr", "current_price_inr", "portfolio_date"
    ]
    keep = [c for c in schema_cols if c in df.columns]
    df = df[keep]

    # Only load rows where amfi_code is in fund_master
    valid_codes = pd.read_sql("SELECT amfi_code FROM fund_master", conn)["amfi_code"].tolist()
    original_len = len(df)
    df = df[df["amfi_code"].isin(valid_codes)]
    skipped = original_len - len(df)
    if skipped:
        print(f"      ⚠ Skipped {skipped} rows with amfi_code not in fund_master")

    df.to_sql("portfolio_holdings", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM portfolio_holdings", conn)["n"][0]
    print(f"      ✓ portfolio_holdings loaded: {count} rows")
    return count


def load_fact_transactions(conn):
    """Load fact_transactions from clean_transactions.csv."""
    print("[9/9] Loading fact_transactions …")
    df = pd.read_csv(PROCESSED_DIR / "clean_transactions.csv", parse_dates=["transaction_date"])
    df.columns = df.columns.str.strip()

    # Only load rows where amfi_code is in fund_master (FK constraint)
    valid_codes = pd.read_sql("SELECT amfi_code FROM fund_master", conn)["amfi_code"].tolist()
    original_len = len(df)
    df = df[df["amfi_code"].isin(valid_codes)]
    skipped = original_len - len(df)
    if skipped:
        print(f"      ⚠ Skipped {skipped} rows with amfi_code not in fund_master")

    # Drop investor_id from schema load (it remains as a data column)
    # transaction_id is AUTOINCREMENT — do not pass it
    if "transaction_id" in df.columns:
        df.drop(columns=["transaction_id"], inplace=True)

    df.to_sql("fact_transactions", conn, if_exists="append", index=False)
    count = pd.read_sql("SELECT COUNT(*) AS n FROM fact_transactions", conn)["n"][0]
    print(f"      ✓ fact_transactions loaded: {count:,} rows")
    return count


# ─── Verification ─────────────────────────────────────────────────────────────

def verify_load(conn):
    """Print a final row-count summary for all tables."""
    tables = [
        "fund_master", "nav_history", "aum_by_fund_house",
        "monthly_sip_inflows", "category_inflows", "scheme_performance",
        "portfolio_holdings", "fact_transactions"
    ]
    print("\n" + "=" * 55)
    print("  LOAD VERIFICATION — ROW COUNTS")
    print("=" * 55)
    total = 0
    for tbl in tables:
        n = pd.read_sql(f"SELECT COUNT(*) AS n FROM {tbl}", conn)["n"][0]
        total += n
        status = "✓" if n > 0 else "✗ EMPTY"
        print(f"  {status:3s} {tbl:<35s}: {n:>8,} rows")
    print("-" * 55)
    print(f"  Total rows across all tables        : {total:>8,}")
    print("=" * 55)

    # Assert all critical tables have data
    for tbl in tables:
        n = pd.read_sql(f"SELECT COUNT(*) AS n FROM {tbl}", conn)["n"][0]
        assert n > 0, f"ERROR: {tbl} is empty after load!"

    print("  ALL TABLES POPULATED — bluestock_mf.db is ready\n")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  BLUESTOCK MF — SQLite ETL Loader")
    print("=" * 55)
    print(f"  DB path : {DB_PATH}")
    print()

    conn = get_connection()
    try:
        apply_schema(conn)
        load_fund_master(conn)
        load_nav_history(conn)
        load_aum_by_fund_house(conn)
        load_monthly_sip_inflows(conn)
        load_category_inflows(conn)
        load_scheme_performance(conn)
        load_portfolio_holdings(conn)
        load_fact_transactions(conn)
        verify_load(conn)
    finally:
        conn.close()
