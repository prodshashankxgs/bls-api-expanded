#!/usr/bin/env python3
"""
BLS Economic Data Scraper - Complete Historical Dataset

Scrapes and displays all available BLS economic data from 1913 to present.
Shows the complete historical dataset in a clean table format.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader import DataLoader

def main():
    print("BLS Economic Data Scraper - Complete Historical Dataset")
    print("=" * 80)
    
    # Initialize the data loader
    dl = DataLoader()
    
    # Check if server is running
    if not dl.health_check():
        print("❌ Error: BLS API server is not running!")
        print("Please start the server first:")
        print("   python3 run.py")
        return
    
    print("✅ Server is running")
    print("\nScraping complete historical BLS data from 1913 to present...")
    
    # Load all available indicators with complete historical data
    all_indicators = list(dl.get_available_indicators().keys())
    print(f"Loading {len(all_indicators)} indicators: {all_indicators}")
    
    # Load complete historical dataset (no date restriction for maximum coverage)
    df = dl.load_data(all_indicators)
    
    if df.is_empty():
        print("❌ No data loaded!")
        return
    
    print(f"\n✅ Successfully loaded {len(df)} total data points")
    print(f"📊 Indicators: {len(df['ticker'].unique())} different economic indicators")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"📈 Historical coverage: {df['date'].max().year - df['date'].min().year + 1} years")
    
    print(f"\n{'='*80}")
    print("COMPLETE BLS ECONOMIC DATA (1913-PRESENT)")
    print(f"{'='*80}")
    
    # Display all data in the same format as the recent data sample table
    display_df = df.select(['ticker', 'period', 'value', 'category']).sort(['ticker', 'period'])
    
    print(display_df)
    
    print(f"\n{'='*80}")
    print("DATA SUMMARY BY INDICATOR")
    print(f"{'='*80}")
    
    # Show summary statistics
    summary = dl.get_summary(df)
    
    print(summary)
    
    print(f"\n{'='*80}")
    print("HISTORICAL MILESTONES")
    print(f"{'='*80}")
    
    # Show key historical data points
    milestone_years = [1913, 1929, 1945, 1970, 1980, 2000, 2008, 2020, 2025]
    
    for year in milestone_years:
        year_data = df.filter(df['year'] == year)
        if len(year_data) > 0:
            print(f"\n{year}:")
            for row in year_data.head(5).iter_rows(named=True):
                print(f"  {row['ticker']}: {row['value']} ({row['period']})")
    
    print(f"\n{'='*80}")
    print("EXPORT COMPLETE DATASET")
    print(f"{'='*80}")
    
    # Save the complete historical dataset
    filename = "complete_bls_historical_data.csv"
    dl.save_data(df, filename)
    print(f"✅ Saved complete historical dataset to: {filename}")
    print(f"📊 File contains {len(df)} data points from {df['date'].min()} to {df['date'].max()}")
    
    print(f"\n{'='*80}")
    print("MISSION ACCOMPLISHED!")
    print(f"{'='*80}")
    print("Complete BLS economic data from 1913 to present has been scraped and displayed.")
    print(f"Dataset includes {len(df)} data points across {len(all_indicators)} economic indicators.")

if __name__ == "__main__":
    main()