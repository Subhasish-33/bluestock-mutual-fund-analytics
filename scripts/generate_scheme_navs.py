"""
Generate 5 NAV CSV files for specific schemes
"""

import pandas as pd
import os
from datetime import datetime

# Load the fund master and NAV history from raw data
fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav_history = pd.read_csv("data/raw/02_nav_history.csv")

# Target schemes
target_amfi_codes = [119551, 120503, 118632, 119092, 120841]

print("=" * 80)
print("GENERATING 5 NAV CSV FILES FOR BLUECHIP SCHEMES")
print("=" * 80)

# Filter NAV history for these schemes
filtered_nav = nav_history[nav_history['amfi_code'].isin(target_amfi_codes)]

# print(f"\nFiltered NAV records: {len(filtered_nav)}")
print(f"Unique schemes in filtered: {filtered_nav['amfi_code'].nunique()}")
print(f"AMFI codes found: {sorted(filtered_nav['amfi_code'].unique().tolist())}")

# Get scheme names
scheme_names = fund_master[fund_master['amfi_code'].isin(target_amfi_codes)][['amfi_code', 'scheme_name']]
print("\nSchemes found:")
print(scheme_names.to_string(index=False))

# Create CSV files for each scheme
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
count = 0

print("\n" + "-" * 80)
for amfi_code in target_amfi_codes:
    scheme_data = nav_history[nav_history['amfi_code'] == amfi_code]
    if len(scheme_data) > 0:
        # Get scheme name
        scheme_info = fund_master[fund_master['amfi_code'] == amfi_code]
        if len(scheme_info) > 0:
            full_name = scheme_info['scheme_name'].values[0]
            scheme_name = full_name.lower().replace(" ", "_").replace("-", "_")[:40]
        else:
            scheme_name = f"scheme_{amfi_code}"
        
        filename = f"data/raw/live_nav_{scheme_name}_{timestamp}.csv"
        scheme_data.to_csv(filename, index=False)
        print(f"✓ [{count+1}/5] {full_name}")
        print(f"   → {filename}")
        # print(f"   → {len(scheme_data)} records | Date range: {scheme_data['date'].min()} to {scheme_data['date'].max()}")
        count += 1
    else:
        print(f"✗ No NAV data found for AMFI code {amfi_code}")

print("\n" + "=" * 80)
print(f"✓ COMPLETED: {count}/5 scheme CSV files created!")
print("=" * 80)
