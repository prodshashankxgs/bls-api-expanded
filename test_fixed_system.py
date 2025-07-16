#!/usr/bin/env python3
"""
Test script to verify the FRED scraper system is working
"""

from fred_data_loader import FREDDataLoader
import logging

logging.basicConfig(level=logging.INFO)

def test_fred_loader():
    """Test the FRED data loader"""
    print("Testing FRED Data Loader...")
    
    # Initialize the loader
    loader = FREDDataLoader()
    
    # Test loading GDP data
    print("\n1. Loading GDP data...")
    gdp_data = loader.load_data("GDP", force_refresh=True)
    
    if gdp_data:
        print(f"✅ Successfully loaded GDP data!")
        print(f"   Series: {gdp_data.series_id}")
        print(f"   Title: {gdp_data.title}")
        print(f"   Data points: {len(gdp_data.data_points)}")
        if gdp_data.data_points:
            latest = gdp_data.data_points[-1]
            print(f"   Latest: {latest.date} = {latest.value}")
    else:
        print("❌ Failed to load GDP data")
    
    # Test loading unemployment data
    print("\n2. Loading UNRATE data...")
    unrate_data = loader.load_data("UNRATE", force_refresh=True)
    
    if unrate_data:
        print(f"✅ Successfully loaded UNRATE data!")
        print(f"   Series: {unrate_data.series_id}")
        print(f"   Data points: {len(unrate_data.data_points)}")
        if unrate_data.data_points:
            latest = unrate_data.data_points[-1]
            print(f"   Latest: {latest.date} = {latest.value}%")
    else:
        print("❌ Failed to load UNRATE data")
    
    print("\n🎉 FRED scraper system test completed!")

if __name__ == "__main__":
    test_fred_loader() 