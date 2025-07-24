#!/usr/bin/env python3
"""
Example Usage - BLS Scraper
============================

Simple examples showing how to use the BLS scraper.
"""

from data import get_cpi, get_food_data, get_energy_data, print_summary, test_functions
from scraper import BLSScraper, get_cpi_data

def main():
    print("bls scraper example usage")
    print("=" * 50)
    
    # First, let's download some data
    print("\n1. downloading latest data...")
    scraper = BLSScraper()
    success = scraper.run_once()
    
    if success:
        print("\n2. testing data functions...")
        test_functions()
        
        print("\n3. getting specific data...")
        
        # get cpi data
        cpi_data = get_cpi()
        if not cpi_data.empty:
            print(f"got {len(cpi_data)} cpi data points")
            print("sample cpi data:")
            print(cpi_data.head(3))
        
        print("\n4. quick summary...")
        print_summary()
        
    else:
        print("could not download data. check your internet connection.")

if __name__ == "__main__":
    main()