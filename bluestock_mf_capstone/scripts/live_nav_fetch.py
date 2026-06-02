"""
Live NAV Fetch Module

Fetches live NAV (Net Asset Value) data from mfapi.in for mutual funds.
Parses JSON response and saves as raw CSV in data/raw/.

API Reference: https://api.mfapi.in/mf/{amfi_code}
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path


def fetch_live_nav(amfi_code, fund_name="fund"):
    """
    Fetch live NAV data from mfapi.in API.
    
    Args:
        amfi_code (int): AMFI code of the mutual fund
        fund_name (str): Name of the fund for file naming
        
    Returns:
        dict: Parsed JSON response from API
    """
    
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    
    try:
        print(f"\n📡 Fetching NAV for {fund_name} (AMFI: {amfi_code})...")
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✓ Success! Status: {response.status_code}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error fetching data: {str(e)}")
        return None


def parse_nav_data(data):
    """
    Parse NAV data from API response JSON.
    
    Args:
        data (dict): API response data
        
    Returns:
        pd.DataFrame: DataFrame with nav, date, and metadata
    """
    
    if not data or 'data' not in data:
        print("   ❌ Invalid data format")
        return None
    
    # Extract metadata
    metadata = {
        'amfi_code': data.get('meta', {}).get('amfi_code'),
        'fund_name': data.get('meta', {}).get('fund_name'),
        'fund_house': data.get('meta', {}).get('fund_house'),
        'scheme_type': data.get('meta', {}).get('scheme_type'),
        'scheme_category': data.get('meta', {}).get('scheme_category'),
        'isin_growth': data.get('meta', {}).get('isin_growth'),
        'isin_div_payout': data.get('meta', {}).get('isin_div_payout'),
    }
    
    print(f"\n   Fund Details:")
    print(f"   - Fund Name: {metadata['fund_name']}")
    print(f"   - Fund House: {metadata['fund_house']}")
    print(f"   - Category: {metadata['scheme_category']}")
    
    # Extract NAV history
    nav_records = []
    for nav_entry in data['data']:
        nav_records.append({
            'amfi_code': metadata['amfi_code'],
            'date': nav_entry['date'],
            'nav': float(nav_entry['nav']),
            'fund_name': metadata['fund_name'],
            'fund_house': metadata['fund_house'],
            'scheme_category': metadata['scheme_category']
        })
    
    df = pd.DataFrame(nav_records)
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"   - Total NAV records: {len(df)}")
    print(f"   - Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df


def save_to_csv(df, fund_name, output_path="data/raw/"):
    """
    Save NAV data to CSV file.
    
    Args:
        df (pd.DataFrame): NAV data
        fund_name (str): Fund name for file naming
        output_path (str): Path to save CSV
        
    Returns:
        str: Path to saved file
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"live_nav_{fund_name}_{timestamp}.csv"
    filepath = os.path.join(output_path, filename)
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    
    print(f"\n   ✓ Saved to: {filepath}")
    print(f"   - File size: {os.path.getsize(filepath)} bytes")
    
    return filepath


def fetch_and_save_nav(amfi_code, fund_name):
    """
    Complete pipeline: Fetch -> Parse -> Save NAV data.
    
    Args:
        amfi_code (int): AMFI code
        fund_name (str): Fund name
        
    Returns:
        pd.DataFrame: Loaded NAV data
    """
    
    print("=" * 80)
    print(f"LIVE NAV FETCH - {fund_name.upper()}")
    print("=" * 80)
    
    # Fetch data
    raw_data = fetch_live_nav(amfi_code, fund_name)
    if not raw_data:
        return None
    
    # Parse data
    df = parse_nav_data(raw_data)
    if df is None:
        return None
    
    # Display sample
    print(f"\n   First 3 rows:")
    print(f"   {df.head(3).to_string()}")
    print(f"\n   Last 3 rows:")
    print(f"   {df.tail(3).to_string()}")
    
    # Save to CSV
    filepath = save_to_csv(df, fund_name)
    
    print("\n" + "=" * 80)
    print("✓ NAV fetch completed successfully!")
    print("=" * 80)
    
    return df


def main():
    """
    Main execution: Fetch live NAV data for mutual funds.
    
    Default: HDFC Top 100 (AMFI: 125497)
    """
    
    # HDFC Top 100
    amfi_code = 125497
    fund_name = "hdfc_top_100"
    
    # Fetch and save
    df = fetch_and_save_nav(amfi_code, fund_name)
    
    if df is not None:
        print(f"\n📊 Statistics:")
        print(f"   - Total records: {len(df)}")
        print(f"   - Latest NAV: ₹{df['nav'].iloc[-1]:.2f}")
        print(f"   - NAV change: {df['nav'].iloc[-1] - df['nav'].iloc[-2]:.4f}")


if __name__ == "__main__":
    main()
