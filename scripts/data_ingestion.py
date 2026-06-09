"""
Data Ingestion Module (D1 Deliverable)

This module handles loading and initial inspection of all mutual fund datasets.
Loads all CSV files from data/raw/, inspects structure, dtypes, and samples.
"""

import pandas as pd
import os
import glob
from pathlib import Path


def load_datasets(raw_data_path="data/raw/"):
    """
    Load all CSV files from raw data directory.
    
    Args:
        raw_data_path (str): Path to raw data directory
        
    Returns:
        dict: Dictionary with dataset names as keys and DataFrames as values
    """
    
    # Find all CSV files
    csv_files = sorted(glob.glob(os.path.join(raw_data_path, "*.csv")))
    
    if not csv_files:
        print(f"❌ No CSV files found in {raw_data_path}")
        return {}
    
    datasets = {}
    
    print("=" * 80)
    print("DATA INGESTION REPORT - Loading 10 Mutual Fund Datasets")
    print("=" * 80)
    
    for idx, filepath in enumerate(csv_files, 1):
        filename = os.path.basename(filepath)
        dataset_name = filename.replace(".csv", "")
        
        try:
            # Load dataset
            df = pd.read_csv(filepath)
            datasets[dataset_name] = df
            
            # Print inspection details
            print(f"\n[{idx}/10] {filename}")
            print("-" * 80)
            # print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            print(f"\n  Data Types:")
            for col, dtype in df.dtypes.items():
                print(f"    - {col}: {dtype}")
            print(f"\n  First 3 Rows:")
            print(f"    {df.head(3).to_string()}")
            print(f"\n  Null Values:")
            null_summary = df.isnull().sum()
            if null_summary.sum() == 0:
                print(f"    ✓ No null values detected")
            else:
                for col, count in null_summary[null_summary > 0].items():
                    print(f"    - {col}: {count} nulls")
            print(f"\n  Duplicates: {df.duplicated().sum()} duplicate rows")
            
        except Exception as e:
            print(f"  ❌ Error loading {filename}: {str(e)}")
    
    print("\n" + "=" * 80)
    # print(f"✓ Successfully loaded {len(datasets)} datasets")
    print("=" * 80)
    
    return datasets


def save_dataset_summary(datasets, output_path="data/processed/"):
    """
    Save a summary of loaded datasets to a text file.
    
    Args:
        datasets (dict): Dictionary of loaded DataFrames
        output_path (str): Path to save summary
    """
    summary_file = os.path.join(output_path, "data_ingestion_summary.txt")
    
    os.makedirs(output_path, exist_ok=True)
    
    with open(summary_file, 'w') as f:
        f.write("DATA INGESTION SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        for name, df in datasets.items():
            f.write(f"Dataset: {name}\n")
            f.write(f"Shape: {df.shape}\n")
            f.write(f"Columns: {', '.join(df.columns)}\n")
            f.write(f"Dtypes:\n")
            for col, dtype in df.dtypes.items():
                f.write(f"  {col}: {dtype}\n")
            f.write(f"Nulls: {df.isnull().sum().sum()}\n")
            f.write(f"Duplicates: {df.duplicated().sum()}\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"\n✓ Summary saved to {summary_file}")


def get_dataset_stats(datasets):
    """
    Get statistics about loaded datasets.
    
    Args:
        datasets (dict): Dictionary of loaded DataFrames
        
    Returns:
        dict: Statistics dictionary
    """
    stats = {
        "total_datasets": len(datasets),
        "total_rows": sum(df.shape[0] for df in datasets.values()),
        "total_columns": sum(df.shape[1] for df in datasets.values()),
        "datasets": {}
    }
    
    for name, df in datasets.items():
        stats["datasets"][name] = {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "null_count": int(df.isnull().sum().sum()),
            "duplicate_count": int(df.duplicated().sum())
        }
    
    return stats


if __name__ == "__main__":
    """
    Main execution: Load all datasets and generate reports
    """
    
    # Load datasets
    datasets = load_datasets(raw_data_path="data/raw/")
    
    if datasets:
        # Get statistics
        stats = get_dataset_stats(datasets)
        
        # Print summary statistics
        print("\nOVERALL STATISTICS:")
        print(f"  Total Datasets: {stats['total_datasets']}")
        print(f"  Total Rows: {stats['total_rows']:,}")
        print(f"  Total Columns: {stats['total_columns']}")
        
        # Save summary report
        save_dataset_summary(datasets)
        
        print("\n✓ Data ingestion completed successfully!")
    else:
        print("\n❌ No datasets loaded. Check data/raw/ directory.")
